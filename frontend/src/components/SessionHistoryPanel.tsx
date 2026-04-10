import { ClockCircleOutlined, DeleteOutlined, HistoryOutlined, MessageOutlined, PlusOutlined, RightOutlined } from '@ant-design/icons';
import { Button, Empty, Popconfirm, Spin } from 'antd';
import type { SessionListItem } from '../types';
import { formatBeijingSessionTime } from '../utils/time';
import './SessionHistoryPanel.css';

interface SessionHistoryPanelProps {
  sessions: SessionListItem[];
  loading: boolean;
  total: number;
  onSelectSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
  deletingSessionId?: string | null;
  activeSessionId?: string | null;
  onCreateSession?: () => void;
  createSessionLabel?: string;
  createSessionDescription?: string;
  createSessionDisabled?: boolean;
}

const CASE_TYPE_LABEL_MAP: Record<string, string> = {
  wage_arrears: '拖欠工资',
  labor_contract: '劳动合同纠纷',
  work_injury: '工伤赔偿',
  other: '其他',
};

function buildSessionPreview(session: SessionListItem): string {
  if (session.last_message_preview?.trim()) {
    return session.last_message_preview;
  }

  if (session.description?.trim()) {
    return session.description;
  }

  return '点击继续补充案件信息';
}

export default function SessionHistoryPanel({
  sessions,
  loading,
  total,
  onSelectSession,
  onDeleteSession,
  deletingSessionId,
  activeSessionId,
  onCreateSession,
  createSessionLabel = '开始新咨询',
  createSessionDescription = '返回首页重新选择案件类型，当前对话会保留在历史记录中。',
  createSessionDisabled = false,
}: SessionHistoryPanelProps) {
  return (
    <aside className="session-history-panel glass-card noise-texture">
      <div className="session-history-header">
        <div>
          <div className="session-history-kicker">
            <HistoryOutlined />
            <span>历史对话</span>
          </div>
          <h2 className="session-history-title">继续上次咨询</h2>
          <p className="session-history-subtitle">最近活跃的案件会优先显示在这里。</p>
        </div>
        <div className="session-history-count">{total}</div>
      </div>

      <div className="session-history-body">
        {onCreateSession && (
          <button
            type="button"
            className="session-history-create-card press-effect"
            onClick={onCreateSession}
            disabled={createSessionDisabled}
          >
            <span className="session-history-create-icon">
              <PlusOutlined />
            </span>
            <span className="session-history-create-copy">
              <span className="session-history-create-title">{createSessionLabel}</span>
              <span className="session-history-create-desc">{createSessionDescription}</span>
            </span>
            <span className="session-history-create-arrow">
              <RightOutlined />
            </span>
          </button>
        )}

        {loading ? (
          <div className="session-history-loading">
            <Spin size="large" />
            <span>正在加载历史对话...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="session-history-empty">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="暂无历史对话"
            />
          </div>
        ) : (
          <div className="session-history-list">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`session-history-item ${activeSessionId === session.id ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
                role="button"
                tabIndex={0}
                aria-current={activeSessionId === session.id ? 'page' : undefined}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    onSelectSession(session.id);
                  }
                }}
              >
                <div className="session-history-item-top">
                  <div className="session-history-item-heading">
                    <span className="session-history-tag">
                      {CASE_TYPE_LABEL_MAP[session.case_type] || session.case_type}
                    </span>
                    <span className="session-history-time">
                      <ClockCircleOutlined />
                      <span>{formatBeijingSessionTime(session.last_message_at || session.updated_at)}</span>
                    </span>
                  </div>

                  <Popconfirm
                    title="删除对话"
                    description="删除后将同时清空该会话的历史消息。"
                    okText="删除"
                    cancelText="取消"
                    okButtonProps={{ danger: true, loading: deletingSessionId === session.id }}
                    onConfirm={(event) => {
                      event?.stopPropagation?.();
                      onDeleteSession(session.id);
                    }}
                  >
                    <Button
                      type="text"
                      size="small"
                      danger
                      className="session-history-delete-btn"
                      icon={<DeleteOutlined />}
                      loading={deletingSessionId === session.id}
                      aria-label="删除对话"
                      onClick={(event) => event.stopPropagation()}
                    />
                  </Popconfirm>
                </div>

                <div className="session-history-preview">{buildSessionPreview(session)}</div>

                <div className="session-history-item-bottom">
                  <span className="session-history-meta">
                    <MessageOutlined />
                    <span>{session.message_count} 条消息</span>
                  </span>
                  <span className="session-history-enter-btn">
                    <RightOutlined />
                    继续
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
