import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, message } from 'antd';
import { createSession } from '../services/chatService';
import type { CaseType } from '../types';
import { ApiError } from '../services/request';
import './HomePage.css';

/** 案件类型选项 — key 对齐后端 SessionCreateRequest.case_type 枚举 */
const CASE_TYPES: Array<{ key: CaseType; icon: string; label: string }> = [
  { key: 'wage_arrears', icon: '💰', label: '拖欠工资' },
  { key: 'labor_contract', icon: '📄', label: '劳动合同纠纷' },
  { key: 'work_injury', icon: '🏥', label: '工伤赔偿' },
];

/**
 * 首页 — 案件类型选择 + 开始咨询
 * 当前为占位版本，阶段 2 接入会话创建逻辑
 */
export default function HomePage() {
  const navigate = useNavigate();
  const [selectedType, setSelectedType] = useState<CaseType | null>(null);
  const [loading, setLoading] = useState(false);

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
      navigate(`/chat/${resp.id}`);
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

  return (
    <div className="home-page">
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
              <span className="home-card-icon">{item.icon}</span>
              <span className="home-card-label">{item.label}</span>
            </div>
          ))}
        </div>

        <Button
          type="primary"
          size="large"
          className="home-start-btn press-effect"
          onClick={handleStart}
          loading={loading}
        >
          开始咨询
        </Button>
      </div>
    </div>
  );
}
