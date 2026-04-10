# 前端开发 Git / PR 操作说明（主干合并后版本）

这份文档是给当前项目用的，按你现在的实际情况来写：

- 你的仓库是 fork 出来的仓库。
- 你自己的仓库地址是：`https://github.com/SleepPause/labors_assistant.git`
- 源仓库地址是：`https://github.com/a76854/labors_assistant.git`
- 后端分支 `feature/backend` 已经合并进源仓库 `main`。
- 所以后续前端开发、同步和提 PR，默认都围绕 `main` 进行。

也就是说，**现在不再把 `feature/backend` 当作前端开发基线**。

---

## 先理解这几个概念

### 1. `origin` 是什么
- `origin` 指向你自己的 GitHub 仓库。
- 你最终把代码推送到这里。

当前项目里，`origin` 是：

```bash
https://github.com/SleepPause/labors_assistant.git
```

### 2. `upstream` 是什么
- `upstream` 指向源仓库。
- 你需要从这里同步团队最新代码。

当前项目里，`upstream` 是：

```bash
https://github.com/a76854/labors_assistant.git
```

### 3. 现在前端应该基于哪个分支开发
- 现在后端已经进了 `main`。
- 所以后续前端分支应该直接基于：

```bash
upstream/main
```

不再基于：

```bash
upstream/feature/backend
```

### 4. 为什么这是更好的状态
- 以后不需要再额外跟 `feature/backend` 对齐。
- PR 目标可以直接是 `main`。
- 分支关系更简单，review 也更干净。

---

## 整体流程图

你之后基本按这个流程走：

1. 本地配置 `upstream`
2. 拉取最新 `upstream/main`
3. 基于 `upstream/main` 创建自己的前端分支
4. 在自己的前端分支开发
5. 提交前检查改动内容
6. 推送到自己的 `origin`
7. 在 GitHub 上发起 PR，目标分支选择 `main`

---

## 第一次配置：把源仓库加到本地

这一步只需要做一次。

```bash
git remote add upstream https://github.com/a76854/labors_assistant.git
git fetch upstream
```

如果提示：

```text
remote upstream already exists
```

说明你已经配置过了，直接执行：

```bash
git fetch upstream
```

---

## 现在正确的前端分支创建方式

### 正确命令

```bash
git fetch upstream
git checkout -b feature/frontend/chat-ui upstream/main
git push -u origin feature/frontend/chat-ui
```

### 这三条命令是什么意思

```bash
git fetch upstream
```

作用：
- 拿到源仓库最新的 `main`

```bash
git checkout -b feature/frontend/chat-ui upstream/main
```

作用：
- 创建新的本地前端分支
- 分支起点是最新的源仓库主干

```bash
git push -u origin feature/frontend/chat-ui
```

作用：
- 把分支推到你自己的 GitHub 仓库
- 以后可以直接 `git push`

### 分支名建议

推荐格式：

```bash
feature/frontend/功能名
```

例如：

```bash
feature/frontend/chat-ui
feature/frontend/document-preview
feature/frontend/generate-result
```

---

## 日常开发流程

每次开发前先确认当前分支：

```bash
git branch
```

查看状态：

```bash
git status
```

正常开发后提交：

```bash
git status
git add 具体文件路径
git commit -m "feat(frontend): add chat ui"
git push
```

---

## 更稳妥的提交方式

不推荐一上来就：

```bash
git add .
```

更推荐：

```bash
git add frontend/src/pages/ChatPage.tsx
git add frontend/src/components/ChatBox.tsx
git add frontend/src/services/api.ts
```

这样更不容易把后端改动、本地调试文件或临时文件误提交进去。

---

## 如果上游 `main` 更新了，你怎么同步

这是后面最常见的操作。

### 推荐写法：用 `merge`

```bash
git fetch upstream
git checkout feature/frontend/chat-ui
git merge upstream/main
```

作用：
- 把最新主干代码合并到你的前端分支

### 合并后检查

```bash
git status
```

如果没有冲突，就可以继续开发。

### 如果出现冲突

处理步骤：

1. 打开冲突文件手动修改
2. 删除冲突标记

```text
<<<<<<< HEAD
=======
>>>>>>> upstream/main
```

3. 改完后执行：

```bash
git add 冲突文件路径
git commit
```

### 建议什么时候同步一次

- 每天开始开发前
- 上游主干合了新功能后
- 准备提 PR 前

---

## 你本地有后端代码，为什么 PR 里仍然只显示前端改动

因为你当前前端分支是基于：

```bash
upstream/main
```

创建的。

GitHub 比较 PR 时，比较的是：

```text
main -> feature/frontend/chat-ui
```

所以：
- 已经在 `main` 里的后端代码不会重复出现在你的 PR 里
- PR 里只会出现你相对于主干新增的前端改动

前提是：
- 不要在前端分支里混入无关后端修改
- 如果确实改了后端，要知道自己为什么改

---

## 提交前一定要做的检查

```bash
git status
git diff --stat
git diff --cached --stat
```

重点确认没有误提交这些内容：

- 后端无关改动
- 调试日志
- 本地环境文件
- 临时代码
- 构建产物

---

## 在 GitHub 上怎么发 PR

当你执行过：

```bash
git push -u origin feature/frontend/chat-ui
```

之后，去 GitHub 页面一般会看到：

```text
Compare & pull request
```

最关键的是看清楚这两项：

### Base branch

应该选：

```text
a76854/labors_assistant:main
```

### Compare branch

应该选：

```text
SleepPause/labors_assistant:feature/frontend/chat-ui
```

### 为什么这一步重要

现在后端已经在 `main` 里了，所以当前阶段：

- PR 目标应该是 `main`
- 不再是 `feature/backend`

---

## PR 标题和说明怎么写

### 标题建议

```text
feat(frontend): 完成聊天页面基础交互
```

### 说明模板

```md
## 改动内容
- 新增聊天页面基础布局
- 接入后端对话接口
- 增加加载态和错误提示

## 联调情况
- 基于 `main` 分支中的后端接口联调
- 当前已验证基础对话流程可通

## 待确认
- 返回字段命名是否最终确定
- 错误码展示文案是否需要统一
```

---

## 你最常用的一套命令

### 第一次创建前端分支

```bash
git remote add upstream https://github.com/a76854/labors_assistant.git
git fetch upstream
git checkout -b feature/frontend/chat-ui upstream/main
git push -u origin feature/frontend/chat-ui
```

### 日常开发提交

```bash
git status
git add 具体文件
git commit -m "feat(frontend): add chat ui"
git push
```

### 同步最新主干

```bash
git fetch upstream
git checkout feature/frontend/chat-ui
git merge upstream/main
```

---

## 常见错误

### 错误 1：继续把 `feature/backend` 当基线

问题：
- 这已经是旧流程
- 会让分支关系变复杂

正确做法：

```bash
git checkout -b feature/frontend/chat-ui upstream/main
```

### 错误 2：PR 还提到 `feature/backend`

问题：
- 后端已经合进主干了
- 再提到 `feature/backend` 没意义

正确做法：
- PR 目标直接选 `main`

### 错误 3：直接在 `main` 上开发

问题：
- 自己的前端改动会失去隔离

正确做法：
- 永远在 `feature/frontend/*` 分支上开发

### 错误 4：直接 `git add .`

问题：
- 很容易把不该提交的文件一起带进去

更推荐：

```bash
git add 具体文件路径
```

---

## 你可以直接照抄的最小流程

```bash
git fetch upstream
git checkout -b feature/frontend/chat-ui upstream/main
git push -u origin feature/frontend/chat-ui
```

开始开发后，每次提交：

```bash
git status
git add 具体文件路径
git commit -m "feat(frontend): 描述你的功能"
git push
```

需要同步主干时：

```bash
git fetch upstream
git checkout feature/frontend/chat-ui
git merge upstream/main
```

最后发 PR 时：

- Base：`a76854/labors_assistant:main`
- Compare：`SleepPause/labors_assistant:feature/frontend/chat-ui`

---

## 一句话总结

你现在的开发基线是：

```bash
upstream/main
```

所以你的正确工作方式是：

- 用 `upstream/main` 作为前端开发底座
- 在自己的 `feature/frontend/*` 分支上写代码
- 推到自己的 `origin`
- 最后把 PR 提给源仓库的 `main`
