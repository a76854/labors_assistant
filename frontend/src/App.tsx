import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme as antTheme, App as AntApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import ResultPage from './pages/ResultPage';

/**
 * 根组件
 * - BrowserRouter 管理路由
 * - ConfigProvider 注入 Ant Design 自定义主题
 * - MainLayout 包裹所有页面
 */
export default function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        // 默认使用暗色算法；布局组件内通过 data-theme 控制 CSS 变量
        algorithm: antTheme.darkAlgorithm,
        token: {
          // 主题色
          colorPrimary: '#3b82f6',
          // 圆角
          borderRadius: 10,
          borderRadiusLG: 14,
          borderRadiusSM: 6,
          // 字体
          fontFamily:
            '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Noto Sans SC", sans-serif',
          // 背景色
          colorBgContainer: 'rgba(40, 40, 46, 0.75)',
          colorBgElevated: '#282830',
          colorBgLayout: '#141416',
        },
        components: {
          Button: {
            // 主按钮渐变效果通过 CSS 补充
            controlHeight: 40,
            controlHeightLG: 48,
            paddingContentHorizontal: 24,
          },
          Input: {
            // 输入框内阴影效果通过 CSS 补充
            controlHeight: 40,
          },
          Message: {
            // 消息提示
            contentBg: 'rgba(40, 40, 46, 0.92)',
          },
        },
      }}
    >
      <AntApp>
        <BrowserRouter>
          <MainLayout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/chat/:sessionId" element={<ChatPage />} />
              <Route path="/result/:docId" element={<ResultPage />} />
            </Routes>
          </MainLayout>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  );
}
