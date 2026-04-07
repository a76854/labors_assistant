import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-dark.css';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
  /** Markdown内容 */
  content: string;
  /** 是否为聊天消息气泡（应用特殊样式） */
  isChatBubble?: boolean;
  /** 自定义class */
  className?: string;
}

/**
 * Markdown 渲染器组件
 * - 支持GitHub-flavored markdown (表格、删除线等)
 * - 支持代码块语法高亮
 * - 支持数学公式渲染
 * - 自动转换链接和特殊格式
 */
export default function MarkdownRenderer({
  content,
  isChatBubble = false,
  className = ''
}: MarkdownRendererProps) {
  return (
    <div className={`markdown-renderer ${isChatBubble ? 'chat-bubble-markdown' : ''} ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          // 自定义不同元素的样式
          h1: ({ node, ...props }) => <h1 className="markdown-heading markdown-h1" {...props} />,
          h2: ({ node, ...props }) => <h2 className="markdown-heading markdown-h2" {...props} />,
          h3: ({ node, ...props }) => <h3 className="markdown-heading markdown-h3" {...props} />,
          h4: ({ node, ...props }) => <h4 className="markdown-heading markdown-h4" {...props} />,
          h5: ({ node, ...props }) => <h5 className="markdown-heading markdown-h5" {...props} />,
          h6: ({ node, ...props }) => <h6 className="markdown-heading markdown-h6" {...props} />,
          
          // 段落
          p: ({ node, ...props }) => <p className="markdown-paragraph" {...props} />,
          
          // 列表
          ul: ({ node, ...props }) => <ul className="markdown-list markdown-ul" {...props} />,
          ol: ({ node, ...props }) => <ol className="markdown-list markdown-ol" {...props} />,
          li: ({ node, ...props }) => <li className="markdown-list-item" {...props} />,
          
          // 代码块
          pre: ({ node, ...props }) => <pre className="markdown-pre" {...props} />,
          code: ({ node, inline, className: codeClassName, ...props }: any) => {
            // 行内代码 vs 代码块
            if (inline) {
              return <code className="markdown-inline-code" {...props} />;
            }
            return <code className={`markdown-code-block ${codeClassName || ''}`} {...props} />;
          },
          
          // 引用块
          blockquote: ({ node, ...props }) => <blockquote className="markdown-blockquote" {...props} />,
          
          // 水平线
          hr: ({ node, ...props }) => <hr className="markdown-hr" {...props} />,
          
          // 表格
          table: ({ node, ...props }) => <table className="markdown-table" {...props} />,
          thead: ({ node, ...props }) => <thead className="markdown-table-head" {...props} />,
          tbody: ({ node, ...props }) => <tbody className="markdown-table-body" {...props} />,
          tr: ({ node, ...props }) => <tr className="markdown-table-row" {...props} />,
          th: ({ node, ...props }) => <th className="markdown-table-header" {...props} />,
          td: ({ node, ...props }) => <td className="markdown-table-cell" {...props} />,
          
          // 链接
          a: ({ node, ...props }) => <a className="markdown-link" target="_blank" rel="noopener noreferrer" {...props} />,
          
          // 图片
          img: ({ node, ...props }) => <img className="markdown-image" {...props} />,
          
          // 强调
          em: ({ node, ...props }) => <em className="markdown-em" {...props} />,
          strong: ({ node, ...props }) => <strong className="markdown-strong" {...props} />,
          
          // 删除线和其他GFM特性由remarkGfm处理
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
