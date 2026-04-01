import { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Input, Button, message, Result, Spin } from 'antd';
import { SendOutlined, FileTextOutlined } from '@ant-design/icons';
import { getSession, getMessages, sendMessage } from '../services/chatService';
import { generateDocument } from '../services/documentService';
import type { SessionResponse, MessageResponse } from '../types';
import { ApiError } from '../services/request';
import './ChatPage.css';

export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<SessionResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  
  const [inputText, setInputText] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const [isGeneratingDoc, setIsGeneratingDoc] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

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
    if (!sessionId) return;
    let isMounted = true;

    const initData = async () => {
      setIsInitializing(true);
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

  const handleSend = async () => {
    if (!inputText.trim() || !sessionId) return;

    const currentText = inputText.trim();
    setInputText('');
    setIsSending(true);

    try {
      // 1. 发送消息（接口返回用户发送的实体）
      const userMessage = await sendMessage(sessionId, { content: currentText });
      
      // 2. 将刚发送的消息压入列表，并开启打字等待
      setMessages((prev) => [...prev, userMessage]);
      setIsTyping(true);

      // 3. 重新拉取服务端历史消息记录（包含助理的 Mock 回复）
      const historyData = await getMessages(sessionId);
      setMessages(historyData.messages || []);

    } catch (error: unknown) {
      // 失败时恢复输入栏
      setInputText(currentText);
      message.error(getErrorMessage(error, '发送失败，请稍后重试'));
    } finally {
      setIsSending(false);
      setIsTyping(false);
    }
  };

  const handleGenerateDoc = async () => {
    if (!sessionId || !session?.case_type) return;
    setIsGeneratingDoc(true);
    try {
      const res = await generateDocument(sessionId, {
        template_id: session.case_type,
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

  if (notFound) {
    return (
      <div className="page-container glass-card" style={{ marginTop: '10vh' }}>
        <Result
          status="404"
          title="会话不存在"
          subTitle="抱歉，您访问的会话无效或已被删除。"
          extra={<Button type="primary" onClick={() => navigate('/')}>返回首页</Button>}
        />
      </div>
    );
  }

  const caseTypeMap: Record<string, string> = {
    wage_arrears: '拖欠工资',
    labor_contract: '劳动合同纠纷',
    work_injury: '工伤赔偿'
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        {isInitializing && (
          <div className="chat-loading-mask">
            <Spin size="large" />
          </div>
        )}
        
        {/* 顶部标题栏 */}
        <div className="chat-header">
          <div className="chat-header-left" style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="chat-header-title">案件咨询</div>
            {session?.case_type && (
              <div className="chat-header-desc">
                类型：{caseTypeMap[session.case_type] || session.case_type}
              </div>
            )}
          </div>
          <div className="chat-header-right">
            <Button
              type="default"
              icon={<FileTextOutlined />}
              loading={isGeneratingDoc}
              onClick={handleGenerateDoc}
              disabled={isInitializing || !session}
            >
              生成诉状
            </Button>
          </div>
        </div>

        {/* 消息历史区域 */}
        <div className="chat-messages">
          {messages.length === 0 && !isInitializing ? (
            <div style={{ textAlign: 'center', color: 'var(--text-tertiary)', marginTop: '20vh' }}>
              请在下方输入框中描述您的具体情况...
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`chat-message-row ${msg.role}`}>
                <div className="chat-avatar">
                  {msg.role === 'assistant' ? '⚖️' : '👤'}
                </div>
                <div className="chat-content-wrapper">
                  <div className="chat-bubble">{msg.content}</div>
                  <div className="chat-timestamp">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
                <div className="chat-bubble">
                  <div className="typing-indicator">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
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
                handleSend();
              }
            }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            disabled={!inputText.trim() || isInitializing}
            loading={isSending}
            className="chat-send-btn press-effect"
          />
        </div>
      </div>
    </div>
  );
}
