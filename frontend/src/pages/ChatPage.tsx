import { useParams } from 'react-router-dom';
import { Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import './ChatPage.css';

/**
 * 聊天页 — 消息列表 + 输入区 + 生成诉状入口
 * 当前为占位版本，阶段 2 填充完整聊天逻辑
 */
export default function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();

  return (
    <div className="chat-page">
      <div className="chat-placeholder">
        <span className="chat-placeholder-icon">💬</span>
        <h2 className="chat-placeholder-title">聊天窗口</h2>
        <p className="chat-placeholder-desc">
          阶段 2 将在此接入消息列表、消息发送和助手回复展示。
          <br />
          当前为占位页面。
        </p>
        <div className="chat-session-id">会话 ID：{sessionId}</div>
        <div style={{ marginTop: 24 }}>
          <Button type="default" onClick={() => navigate('/')}>
            返回首页
          </Button>
        </div>
      </div>
    </div>
  );
}
