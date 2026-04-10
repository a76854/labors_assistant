import { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { Input, Button, message, Modal, Result, Spin, Tooltip } from 'antd';
import { SendOutlined, FileTextOutlined, StopOutlined } from '@ant-design/icons';
import SessionHistoryPanel from '../components/SessionHistoryPanel';
import { deleteSession, getSession, getMessages, listSessions, streamChat, syncMessages } from '../services/chatService';
import { generateDocument } from '../services/documentService';
import MarkdownRenderer from '../components/MarkdownRenderer';
import type { MessageResponse, SessionListItem, SessionResponse } from '../types';
import { ApiError } from '../services/request';
import { formatBeijingTime } from '../utils/time';
import './ChatPage.css';

type ChatEntrySource = 'new' | 'history';

interface ChatLocationState {
  entry?: ChatEntrySource;
}

interface CaseGuidanceConfig {
  intro: string;
  suggestions: string[];
}

const DOCUMENT_READY_SIGNAL = '请点击右上角生成诉状';

const CASE_GUIDANCE_MAP: Record<string, CaseGuidanceConfig> = {
  wage_arrears: {
    intro: '您好，我是劳动报酬纠纷助手。先告诉我您与单位的关系、拖欠周期和金额，我会快速帮您梳理维权路径。',
    suggestions: [
      '我在这家公司工作多久了，最近3个月工资都没发，应该先走什么流程？',
      '公司只发了基本工资，绩效和加班费一直拖着，我可以一起主张吗？',
      '我手里有劳动合同和工资流水，还需要补哪些证据才能申请仲裁？',
    ],
  },
  labor_contract: {
    intro: '您好，我是劳动合同争议助手。您先说清楚合同类型、解除经过和通知方式，我会帮您判断是否违法解除。',
    suggestions: [
      '公司突然通知我明天不用来了，没有书面文件，这算违法解除吗？',
      '我签的是无固定期限合同，公司要求降薪续签，我可以拒绝吗？',
      '竞业限制约定了补偿但公司一直没发，我还需要继续履行吗？',
    ],
  },
  work_injury: {
    intro: '您好，我是工伤赔偿助手。请先描述受伤经过、时间地点和就医情况，我会帮您评估工伤认定与赔付项目。',
    suggestions: [
      '我在上班途中发生交通事故，单位说不算工伤，这种情况该怎么认定？',
      '工伤认定已经通过，后续停工留薪期工资和护理费怎么主张？',
      '单位没给我交工伤保险，发生工伤后赔偿责任由谁承担？',
    ],
  },
  other: {
    intro: '您好，我是劳动法律咨询助手。您可以先告诉我遇到的核心问题和时间线，我会给您对应的处理建议。',
    suggestions: [
      '公司长期不给我缴社保，我可以要求补缴并主张赔偿吗？',
      '离职后公司拖着不给离职证明，影响我入职新公司怎么办？',
      '试用期被辞退，单位说不需要补偿，这种说法合法吗？',
    ],
  },
};

function buildCurrentSessionItem(
  currentSessionId: string,
  currentSession: SessionResponse,
  currentMessages: MessageResponse[],
): SessionListItem {
  const lastMessage = currentMessages[currentMessages.length - 1];

  return {
    id: currentSessionId,
    case_type: currentSession.case_type,
    status: currentSession.status,
    description: currentSession.description,
    created_at: currentSession.created_at,
    updated_at: lastMessage?.timestamp || currentSession.updated_at,
    message_count: currentMessages.length,
    last_message_preview: lastMessage?.content || currentSession.description || '点击继续补充案件信息',
    last_message_role: lastMessage?.role,
    last_message_at: lastMessage?.timestamp,
  };
}

function containsDocumentReadySignal(content?: string | null): boolean {
  if (!content) return false;
  return content.replace(/\s+/g, '').includes(DOCUMENT_READY_SIGNAL);
}

function getCaseGuidance(caseType?: string): CaseGuidanceConfig {
  if (!caseType) {
    return CASE_GUIDANCE_MAP.other;
  }
  return CASE_GUIDANCE_MAP[caseType] || CASE_GUIDANCE_MAP.other;
}

export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const entrySource = (location.state as ChatLocationState | null)?.entry;
  const isEntryFromNewSession = entrySource === 'new';

  const [session, setSession] = useState<SessionResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [historySessions, setHistorySessions] = useState<SessionListItem[]>([]);
  
  const [inputText, setInputText] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [currentReply, setCurrentReply] = useState('');
  const [toolHint, setToolHint] = useState('');
  const [notFound, setNotFound] = useState(false);
  const [isGeneratingDoc, setIsGeneratingDoc] = useState(false);
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const getErrorMessage = (error: unknown, fallback: string): string => {
    if (error instanceof ApiError || error instanceof Error) {
      return error.message;
    }
    return fallback;
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    if (!sessionId) return;
    let isMounted = true;

    const initData = async () => {
      setIsInitializing(true);
      setNotFound(false);
      setSession(null);
      setMessages([]);
      try {
        const [sessionData, historyData] = await Promise.all([
          getSession(sessionId),
          getMessages(sessionId)
        ]);
        if (isMounted) {
          setSession(sessionData);
          setMessages(historyData.messages || []);
        }
      } catch (error: unknown) {
        if (isMounted) {
          if (error instanceof ApiError && error.status === 404) {
            setNotFound(true);
          } else {
            message.error(getErrorMessage(error, '无法加载会话信息，请稍后重试'));
          }
        }
      } finally {
        if (isMounted) setIsInitializing(false);
      }
    };

    initData();
    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    let isMounted = true;

    const fetchHistorySessions = async () => {
      setHistoryLoading(true);
      try {
        const response = await listSessions(20, 0);
        const visibleSessions = (response.sessions || []).filter(
          (historySession) => historySession.message_count > 0,
        );

        if (isMounted) {
          setHistorySessions(visibleSessions);
        }
      } catch (error: unknown) {
        if (!isMounted) return;
        setHistorySessions([]);
        message.error(getErrorMessage(error, '加载历史对话失败，请稍后重试'));
      } finally {
        if (isMounted) {
          setHistoryLoading(false);
        }
      }
    };

    fetchHistorySessions();

    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  useEffect(() => {
    if (isInitializing || !sessionId || !session || notFound) return;

    const currentSessionItem = buildCurrentSessionItem(sessionId, session, messages);
    setHistorySessions((prev) => {
      const hasCurrent = prev.some((item) => item.id === currentSessionItem.id);
      const sessionsWithoutCurrent = prev.filter((item) => item.id !== currentSessionItem.id);

      if (isEntryFromNewSession || !hasCurrent) {
        return [currentSessionItem, ...sessionsWithoutCurrent];
      }

      return prev.map((item) => (
        item.id === currentSessionItem.id ? currentSessionItem : item
      ));
    });
  }, [isEntryFromNewSession, isInitializing, messages, notFound, session, sessionId]);

  const handleSelectSession = (targetSessionId: string) => {
    if (targetSessionId === sessionId) return;
    navigate(`/chat/${targetSessionId}`, { state: { entry: 'history' } });
  };

  const handleDeleteSession = async (targetSessionId: string) => {
    setDeletingSessionId(targetSessionId);
    try {
      await deleteSession(targetSessionId);
      setHistorySessions((prev) => prev.filter((item) => item.id !== targetSessionId));
      message.success('历史对话已删除');

      if (targetSessionId === sessionId) {
        message.info('当前会话已删除，已返回首页');
        navigate('/');
      }
    } catch (error: unknown) {
      message.error(getErrorMessage(error, '删除对话失败，请稍后重试'));
    } finally {
      setDeletingSessionId(null);
    }
  };

  const navigateHomeForNewConversation = () => {
    navigate('/');
  };

  const handleStartNewConversation = () => {
    const hasConversationContent = messages.length > 0;

    if (isSending) {
      Modal.confirm({
        title: '结束当前生成并返回首页？',
        content: '当前回复仍在生成中。返回首页后会结束本轮生成，但已经产生的对话仍会保留在历史记录里，您稍后可以继续回来查看。',
        okText: '返回首页',
        cancelText: '继续当前对话',
        okButtonProps: { type: 'primary' },
        centered: true,
        onOk: navigateHomeForNewConversation,
      });
      return;
    }

    if (hasConversationContent) {
      Modal.confirm({
        title: '返回首页开始新的咨询？',
        content: '当前对话不会丢失。返回首页后，您可以重新选择案件类型开始新的咨询，这段对话仍会保留在左侧历史记录中。',
        okText: '返回首页',
        cancelText: '留在当前对话',
        okButtonProps: { type: 'primary' },
        centered: true,
        onOk: navigateHomeForNewConversation,
      });
      return;
    }

    navigateHomeForNewConversation();
  };

  const handleSend = async (presetText?: string) => {
    if (!sessionId || isSending || isInitializing) return;

    const sourceText = typeof presetText === 'string' ? presetText : inputText;
    if (!sourceText.trim()) return;

    const currentText = sourceText.trim();
    setInputText('');
    setIsSending(true);
    setIsTyping(true);
    setCurrentReply('');
    setToolHint('');
    abortControllerRef.current = new AbortController();
    let replyBuffer = '';
    let localUserMessageId = '';
    const persistConversation = async (items: Array<Pick<MessageResponse, 'role' | 'content'>>) => {
      try {
        await syncMessages(sessionId, items);
      } catch (syncError: unknown) {
        message.warning(getErrorMessage(syncError, '当前对话已显示，但同步历史记录失败，刷新后可能看不到本轮消息'));
      }
    };

    try {
      const nowIso = new Date().toISOString();
      const userMessage: MessageResponse = {
        id: `local-user-${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content: currentText,
        timestamp: nowIso,
      };
      localUserMessageId = userMessage.id;
      setMessages((prev) => [...prev, userMessage]);

      await streamChat(sessionId, currentText, {
        onToken: (token) => {
          replyBuffer += token;
          setCurrentReply(replyBuffer);
        },
        onToolStart: (toolName) => {
          if (toolName === 'search_public_laws_tool') {
            setToolHint('正在为您检索法律条文...');
          } else if (toolName === 'search_public_cases_tool') {
            setToolHint('正在为您检索相似判例...');
          } else if (toolName === 'search_private_knowledge_tool') {
            setToolHint('正在为您检索私域知识...');
          } else if (toolName === 'generate_legal_doc_tool') {
            setToolHint('正在为您生成法律文书...');
          } else {
            setToolHint(`正在调用工具：${toolName}`);
          }
        },
        onToolEnd: () => {
          setToolHint('');
        },
        onError: (errMsg) => {
          throw new Error(errMsg || '流式请求异常');
        },
      }, abortControllerRef.current.signal);

      if (replyBuffer.trim()) {
        const assistantMessage: MessageResponse = {
          id: `local-assistant-${Date.now()}`,
          session_id: sessionId,
          role: 'assistant',
          content: replyBuffer,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        await persistConversation([
          { role: 'user', content: currentText },
          { role: 'assistant', content: replyBuffer },
        ]);
      } else {
        await persistConversation([
          { role: 'user', content: currentText },
        ]);
      }

    } catch (error: unknown) {
      const isAbort = error instanceof DOMException && error.name === 'AbortError';
      if (isAbort) {
        if (replyBuffer.trim()) {
          const assistantMessage: MessageResponse = {
            id: `local-assistant-${Date.now()}`,
            session_id: sessionId,
            role: 'assistant',
            content: replyBuffer,
            timestamp: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          await persistConversation([
            { role: 'user', content: currentText },
            { role: 'assistant', content: replyBuffer },
          ]);
        } else {
          await persistConversation([
            { role: 'user', content: currentText },
          ]);
        }
        message.info('已停止生成');
      } else {
        setMessages((prev) => prev.filter((msg) => msg.id !== localUserMessageId));
        setInputText(currentText);
        message.error(getErrorMessage(error, '发送失败，请稍后重试'));
      }
    } finally {
      abortControllerRef.current = null;
      setIsSending(false);
      setIsTyping(false);
      setToolHint('');
      setCurrentReply('');
    }
  };

  const handleStopGenerate = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleGenerateDoc = async () => {
    const currentCaseType = session?.case_type
      || historySessions.find((historyItem) => historyItem.id === sessionId)?.case_type;

    if (!sessionId) return;
    if (!isDocumentGenerationReady) {
      message.info('助手尚未确认可以生成诉状。请继续咨询，直到回复中明确出现“请点击右上角生成诉状”。');
      return;
    }
    if (!currentCaseType) {
      message.info('会话类型仍在加载中，请稍后重试。');
      return;
    }
    if (currentCaseType === 'other') {
      message.info('当前会话类型为“其他法律咨询”，暂不支持直接生成诉状。请先选择明确案件类型后再试。');
      return;
    }
    setIsGeneratingDoc(true);
    try {
      const res = await generateDocument(sessionId, {
        template_id: currentCaseType,
        format: 'docx'
      });
      message.success('文档生成请求已提交');
      navigate(`/result/${res.id}`);
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        message.error(error.message);
      } else {
        message.error('生成诉状失败，请稍后重试');
      }
    } finally {
      setIsGeneratingDoc(false);
    }
  };

  const caseTypeMap: Record<string, string> = {
    wage_arrears: '拖欠工资',
    labor_contract: '劳动合同纠纷',
    work_injury: '工伤赔偿',
    other: '其他',
  };

  const currentSessionCaseType = session?.case_type
    || historySessions.find((historyItem) => historyItem.id === sessionId)?.case_type;
  const caseGuidance = useMemo(
    () => getCaseGuidance(currentSessionCaseType),
    [currentSessionCaseType],
  );
  const isDocumentGenerationReady = useMemo(
    () => messages.some(
      (msg) => msg.role === 'assistant' && containsDocumentReadySignal(String(msg.content || '')),
    ) || containsDocumentReadySignal(currentReply),
    [currentReply, messages],
  );
  const showGenerateDocButton = currentSessionCaseType !== 'other';
  const actionButtonLabel = isSending ? '停止' : '发送';
  const actionButtonIcon = isSending ? <StopOutlined /> : <SendOutlined />;
  const actionButtonDisabled = isInitializing || (!isSending && !inputText.trim());
  const actionButtonClassName = `chat-action-btn ${isSending ? 'chat-action-btn-stop' : 'chat-action-btn-send'} press-effect`;
  const historyTotal = historySessions.length;
  const isGenerateDocButtonDisabled = isInitializing || isSending || !isDocumentGenerationReady;
  const generateDocTooltipTitle = isGenerateDocButtonDisabled
    ? '前置信息不足，无法生成诉状文书'
    : '生成诉状文书';

  const historyPanel = (
    <SessionHistoryPanel
      sessions={historySessions}
      loading={historyLoading}
      total={historyTotal}
      onSelectSession={handleSelectSession}
      onDeleteSession={handleDeleteSession}
      deletingSessionId={deletingSessionId}
      activeSessionId={sessionId}
      onCreateSession={handleStartNewConversation}
      createSessionLabel="开始新的案件咨询"
      createSessionDescription="返回首页重新选择案件类型，当前对话会自动保留在历史记录中。"
      createSessionDisabled={isInitializing}
    />
  );

  if (notFound) {
    return (
      <div className="chat-page">
        <div className="chat-shell">
          <div className="chat-history-column">{historyPanel}</div>
          <div className="chat-main">
            <div className="chat-not-found glass-card">
              <Result
                status="404"
                title="会话不存在"
                subTitle="抱歉，您访问的会话无效或已被删除。"
                extra={<Button type="primary" onClick={() => navigate('/')}>返回首页</Button>}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-page">
      <div className="chat-shell">
        <div className="chat-history-column">{historyPanel}</div>
        <div className="chat-main">
          <div className="chat-container">
        {isInitializing && (
          <div className="chat-loading-mask">
            <Spin size="large" />
          </div>
        )}
        
        {/* 顶部标题栏 */}
        <div className="chat-header">
          <div className="chat-header-left">
            <div className="chat-header-title">案件咨询</div>
            {session?.case_type && (
              <div className="chat-header-desc">
                类型：{caseTypeMap[session.case_type] || session.case_type}
              </div>
            )}
          </div>
          <div className="chat-header-right">
            {showGenerateDocButton && (
              <Tooltip title={generateDocTooltipTitle}>
                <span className="chat-generate-doc-tooltip-wrapper">
                <Button
                  type="default"
                  icon={<FileTextOutlined />}
                  loading={isGeneratingDoc}
                  onClick={handleGenerateDoc}
                  disabled={isGenerateDocButtonDisabled}
                  className="chat-generate-doc-btn press-effect"
                >
                  生成诉状
                </Button>
                </span>
              </Tooltip>
            )}
          </div>
        </div>

        {/* 消息历史区域 */}
        <div className="chat-messages">
          {messages.length === 0 && !isInitializing ? (
            <div className="chat-empty-guide">
              <div className="chat-message-row assistant chat-welcome-row">
                <div className="chat-avatar">⚖️</div>
                <div className="chat-content-wrapper">
                  <div className="chat-bubble chat-welcome-bubble">
                    {caseGuidance.intro}
                  </div>
                </div>
              </div>

              <div className="chat-welcome-suggestions">
                <div className="chat-welcome-suggestions-title">你可以这样问我</div>
                <div className="chat-welcome-suggestions-list">
                  {caseGuidance.suggestions.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="chat-welcome-suggestion-btn"
                      onClick={() => {
                        void handleSend(suggestion);
                      }}
                      disabled={isSending || isInitializing}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`chat-message-row ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'assistant' ? '⚖️' : '👤'}
                </div>
                <div className="chat-content-wrapper">
                  <div className="chat-bubble">
                    <MarkdownRenderer 
                      content={msg.content} 
                      isChatBubble={true}
                    />
                  </div>
                  <div className="chat-timestamp">
                    {formatBeijingTime(msg.timestamp)}
                  </div>
                </div>
              </div>
            ))
          )}
          
          {/* 打字指示器 */}
          {isTyping && (
            <div className="chat-message-row assistant">
              <div className="chat-avatar">⚖️</div>
              <div className="chat-content-wrapper">
                {toolHint && <div className="chat-tool-hint">{toolHint}</div>}
                <div className="chat-bubble">
                  {currentReply ? (
                    <MarkdownRenderer content={currentReply} isChatBubble={true} />
                  ) : (
                    <div className="typing-indicator">
                      <span className="typing-dot"></span>
                      <span className="typing-dot"></span>
                      <span className="typing-dot"></span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 底部输入框 */}
        <div className="chat-input-area">
          <Input.TextArea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSending || isInitializing}
            className="chat-textarea"
            placeholder="请输入案件相关的详细信息..."
            autoSize={{ minRows: 2, maxRows: 4 }}
            onPressEnter={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                void handleSend();
              }
            }}
          />
          <Button
            type="default"
            icon={actionButtonIcon}
            onClick={isSending ? handleStopGenerate : () => { void handleSend(); }}
            disabled={actionButtonDisabled}
            className={actionButtonClassName}
            aria-label={actionButtonLabel}
          >
            {actionButtonLabel}
          </Button>
        </div>
          </div>
        </div>
      </div>
    </div>
  );
}
