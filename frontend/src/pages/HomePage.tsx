import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, message } from 'antd';
import SessionHistoryPanel from '../components/SessionHistoryPanel';
import { createSession, deleteSession, listSessions } from '../services/chatService';
import type { CaseType, SessionListItem } from '../types';
import { ApiError } from '../services/request';
import './HomePage.css';

const CASE_TYPES: Array<{ key: CaseType; icon: string; label: string; desc: string }> = [
  { key: 'wage_arrears', icon: '💰', label: '劳动报酬纠纷', desc: '拖欠工资、加班费、年终奖等。' },
  { key: 'labor_contract', icon: '📄', label: '合同争议', desc: '无固定期限、竞业限制、解雇等。' },
  { key: 'work_injury', icon: '🏥', label: '工伤赔偿', desc: '工作伤害认定、职业病等。' },
  { key: 'other', icon: '⚙️', label: '其他法律咨询', desc: '社会保险、解除合同赔偿等。' },
];

/**
 * 首页 — 案件类型选择 + 开始咨询
 * 当前为占位版本，阶段 2 接入会话创建逻辑
 */
export default function HomePage() {
  const navigate = useNavigate();
  const [selectedType, setSelectedType] = useState<CaseType | null>(null);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historySessions, setHistorySessions] = useState<SessionListItem[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [deletingSessionId, setDeletingSessionId] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchHistorySessions = async () => {
      setHistoryLoading(true);
      try {
        const response = await listSessions(20, 0);
        const visibleSessions = (response.sessions || []).filter(
          (session) => session.message_count > 0,
        );
        if (isMounted) {
          setHistorySessions(visibleSessions);
          setHistoryTotal(response.total || visibleSessions.length);
        }
      } catch (error: unknown) {
        if (!isMounted) return;

        setHistorySessions([]);
        setHistoryTotal(0);
        if (error instanceof ApiError || error instanceof Error) {
          message.error(error.message);
        } else {
          message.error('加载历史对话失败，请稍后重试');
        }
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
  }, []);

  const handleStart = async () => {
    if (!selectedType) {
      message.error('请先选择一个案件类型');
      return;
    }
    
    setLoading(true);
    try {
      const resp = await createSession({
        case_type: selectedType,
      });
      navigate(`/chat/${resp.id}`, { state: { entry: 'new' } });
    } catch (error: unknown) {
      if (error instanceof ApiError || error instanceof Error) {
        message.error(error.message);
      } else {
        message.error('创建会话失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    setDeletingSessionId(sessionId);
    try {
      await deleteSession(sessionId);
      setHistorySessions((prev) => prev.filter((session) => session.id !== sessionId));
      setHistoryTotal((prev) => Math.max(0, prev - 1));
      message.success('历史对话已删除');
    } catch (error: unknown) {
      if (error instanceof ApiError || error instanceof Error) {
        message.error(error.message);
      } else {
        message.error('删除对话失败，请稍后重试');
      }
    } finally {
      setDeletingSessionId(null);
    }
  };

  return (
    <div className="home-page">
      <div className="home-shell">
        <div className="home-history-column">
          <SessionHistoryPanel
            sessions={historySessions}
            loading={historyLoading}
            total={historyTotal}
            onSelectSession={(sessionId) => navigate(`/chat/${sessionId}`, { state: { entry: 'history' } })}
            onDeleteSession={handleDeleteSession}
            deletingSessionId={deletingSessionId}
          />
        </div>

        <div className="home-main">
          <div className="home-hero">
            <span className="home-icon">⚖️</span>
            <h1 className="home-title">劳动者维权 AI 助手</h1>
            <p className="home-subtitle">
              通过智能对话收集您的案件信息，
              <br />
              自动生成格式规范、法律用语准确的诉状文书。
            </p>

            <div className="home-cards">
              {CASE_TYPES.map((item) => (
                <div
                  key={item.key}
                  className={`home-card ${selectedType === item.key ? 'selected' : ''}`}
                  onClick={() => setSelectedType(item.key)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) =>
                    e.key === 'Enter' && setSelectedType(item.key)
                  }
                >
                  <div className="home-card-icon-wrapper">
                    <span className="home-card-icon">{item.icon}</span>
                  </div>
                  <div className="home-card-content">
                    <span className="home-card-label">{item.label}</span>
                    <span className="home-card-desc">{item.desc}</span>
                  </div>
                </div>
              ))}
            </div>

            <Button
              type="primary"
              size="large"
              className="home-start-btn press-effect"
              onClick={handleStart}
              loading={loading}
              icon={
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '4px' }}>
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  <path d="M12 7v5l3 3"></path>
                </svg>
              }
            >
              开始咨询
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
