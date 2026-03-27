import { useParams, useNavigate } from 'react-router-dom';
import { Button } from 'antd';
import './ResultPage.css';

/**
 * 结果页 — 文档信息展示 + 下载占位
 * 当前为占位版本，阶段 3 填充文档展示和下载逻辑
 */
export default function ResultPage() {
  const { docId } = useParams<{ docId: string }>();
  const navigate = useNavigate();

  return (
    <div className="result-page">
      <div className="result-placeholder">
        <span className="result-placeholder-icon">📑</span>
        <h2 className="result-placeholder-title">文档结果</h2>
        <p className="result-placeholder-desc">
          阶段 3 将在此展示生成的诉状文档信息和下载入口。
          <br />
          当前为占位页面。
        </p>
        <div className="result-doc-id">文档 ID：{docId}</div>
        <div style={{ marginTop: 24 }}>
          <Button type="default" onClick={() => navigate('/')}>
            返回首页
          </Button>
        </div>
      </div>
    </div>
  );
}
