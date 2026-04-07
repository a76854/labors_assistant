import { useState, useEffect, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import './MainLayout.css';

interface MainLayoutProps {
  children: ReactNode;
}

/**
 * 主布局组件
 * - 固顶导航栏（毛玻璃效果）
 * - 主题切换（深色 / 浅色）
 * - 内容区由子组件填充
 */
export default function MainLayout({ children }: MainLayoutProps) {
  const navigate = useNavigate();

  // 读取用户偏好或默认深色模式
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const saved = localStorage.getItem('app-theme');
    if (saved === 'light' || saved === 'dark') return saved;
    return 'dark';
  });

  // 同步 data-theme 到 html 元素
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="main-layout">
      {/* 导航栏 */}
      <nav className="main-navbar noise-texture">
        <div
          className="navbar-brand"
          onClick={() => navigate('/')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && navigate('/')}
        >
          <span className="navbar-brand-icon">⚖</span>
          <span>劳动者维权 AI 助手</span>
        </div>

        <div className="navbar-actions">
          <button
            className="theme-toggle-btn press-effect"
            onClick={toggleTheme}
            title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
            aria-label="切换主题"
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
        </div>
      </nav>

      {/* 内容区 */}
      <main className="main-content">{children}</main>
    </div>
  );
}
