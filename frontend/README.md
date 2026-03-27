# 前端工程说明

本目录是项目的前端工程，当前实际技术基线以 `package.json` 为准。

## 当前技术栈

- React `^19.2.4`
- React DOM `^19.2.4`
- Ant Design `^6.3.4`
- React Router DOM `^7.13.2`
- Vite `^8.0.1`
- TypeScript `~5.9.3`

## 版本说明

- 当前前端工程已经确定继续使用 `React 19` 和 `Ant Design 6`。
- 根目录 `README.md` 保持项目级说明，不作为当前前端实际依赖版本的唯一依据。
- 前端后续开发、联调和排查问题时，应优先以本目录 `package.json` 和本文件说明为准。

## 开发命令

在 `frontend/` 目录下执行：

```bash
npm install
npm run dev
```

常用命令：

```bash
npm run lint
npm run build
npm run preview
```

## 环境变量

当前本地开发环境使用：

```bash
VITE_API_BASE_URL=http://localhost:8000
```

默认配置文件：

```text
frontend/.env.development
```

## 当前工程目标

- 先完成前端基础工程搭建
- 再接聊天主链路
- 再接文档生成与结果展示
- 最后进行联调与验收

详细规划以根目录 `plan/` 中的计划文件为准。
