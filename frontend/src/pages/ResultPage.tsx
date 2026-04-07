import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, message, Result, Spin } from 'antd';
import { DownloadOutlined, LeftOutlined, FileWordOutlined, LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { getDocument, exportDocument } from '../services/documentService';
import MarkdownRenderer from '../components/MarkdownRenderer';
import type { DocumentResponse } from '../types';
import { ApiError } from '../services/request';
import './ResultPage.css';

export default function ResultPage() {
  const { docId } = useParams<{ docId: string }>();
  const navigate = useNavigate();

  const [doc, setDoc] = useState<DocumentResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (!docId) return;
    let isMounted = true;
    const fetchDoc = async () => {
      setLoading(true);
      try {
        const res = await getDocument(docId);
        if (isMounted) setDoc(res);
      } catch (error: unknown) {
        if (isMounted) {
          if (error instanceof ApiError && error.status === 404) {
            setNotFound(true);
          } else {
            message.error('无法加载文档，请稍后重试');
          }
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    fetchDoc();
    return () => { isMounted = false; };
  }, [docId]);

  const handleExport = async () => {
    if (!docId) return;
    setExporting(true);
    try {
      const res = await exportDocument(docId);
      if (res && res.message) {
        message.info(`下载状态: ${res.message}`);
      } else {
        message.info('下载功能正在完善中，敬请期待');
      }
    } catch (error: unknown) {
      if (error instanceof ApiError) {
        message.error(error.message);
      } else {
        message.error('导出请求失败，请稍后重试');
      }
    } finally {
      setExporting(false);
    }
  };

  if (notFound) {
    return (
      <div className="page-container glass-card" style={{ marginTop: '10vh' }}>
        <Result
          status="404"
          title="文档不存在"
          subTitle="抱歉，您访问的文档无效或已被删除。"
          extra={<Button type="primary" onClick={() => navigate('/')}>返回首页</Button>}
        />
      </div>
    );
  }

  const getStatusTag = (status?: string) => {
    // 放弃 AntD 写死的颜色，改用可完美适配日夜间的自定义 CSS 样式
    switch (status) {
      case 'pending': 
        return <div className="custom-status-tag border-blue"><LoadingOutlined /> 生成中</div>;
      case 'generated': 
        return <div className="custom-status-tag border-green"><CheckCircleOutlined /> 生成完成</div>;
      case 'exported': 
        return <div className="custom-status-tag border-gray">已导出</div>;
      case 'failed': 
        return <div className="custom-status-tag border-red"><CloseCircleOutlined /> 生成失败</div>;
      default: 
        return <div className="custom-status-tag border-gray">状态未知</div>;
    }
  };

  const formatSize = (bytes?: number) => {
    if (!bytes) return '未知';
    if (bytes < 1024) return bytes + ' B';
    return (bytes / 1024).toFixed(2) + ' KB';
  };

  return (
    <div className="result-page">
      <div className="result-container glass-card noise-texture">
        {loading ? (
          <div className="result-loading">
            <Spin size="large" tip="加载文档信息中..." />
          </div>
        ) : doc ? (
          <>
            <div className="result-header">
              <Button type="text" icon={<LeftOutlined />} onClick={() => navigate(`/chat/${doc.session_id}`)} className="result-back-btn">
                返回聊天
              </Button>
              <div className="result-header-content">
                <div className="result-doc-icon">
                  <FileWordOutlined />
                </div>
                <div className="result-doc-info">
                  <h2 className="result-title">{doc.title || '未命名文档'}</h2>
                  <div className="result-meta-tags">
                    {getStatusTag(doc.status)}
                    {doc.file_size && doc.file_size > 0 ? (
                       <div className="custom-status-tag border-gray">{formatSize(doc.file_size)}</div>
                    ) : null}
                  </div>
                </div>
              </div>
            </div>

            <div className="result-content-area">
              <div className="result-info-grid">
                <div className="info-item">
                  <div className="info-label">
                    <span className="dot"></span>
                    文档标识
                  </div>
                  <div className="info-value doc-id-font">#{doc.id.substring(0,8)}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">
                    <span className="dot"></span>
                    创建时间
                  </div>
                  <div className="info-value">{new Date(doc.created_at).toLocaleString()}</div>
                </div>
                <div className="info-item">
                  <div className="info-label">
                    <span className="dot"></span>
                    更新时间
                  </div>
                  <div className="info-value">{new Date(doc.updated_at).toLocaleString()}</div>
                </div>
              </div>

              <div className="result-mock-box">
                {doc.content ? (
                  <div className="result-content">
                    <MarkdownRenderer 
                      content={doc.content}
                      className="document-content"
                    />
                  </div>
                ) : (
                  <>
                    <div className="mock-shimmer"></div>
                    <p className="mock-text">
                      {doc.status === 'pending' ? '文档生成中，请稍候...' : '文档内容为空或正在处理。'}
                      <br/>
                      您可点击下方按钮尝试获取本地完整文件。
                    </p>
                  </>
                )}
              </div>
            </div>

            <div className="result-footer">
               <Button 
                type="primary" 
                size="large" 
                icon={<DownloadOutlined />} 
                loading={exporting}
                onClick={handleExport}
                className="result-download-btn press-effect"
                disabled={doc.status === 'pending'}
               >
                 下载诉状 (Word)
               </Button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
