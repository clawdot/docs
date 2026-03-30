# Clawdot 虾点文档中心 — 项目规范

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Run `mint dev` to preview locally
- Run `mint broken-links` to check links

## Terminology

- 产品名：Clawdot / 虾点
- Gateway：指 Clawdot Gateway，AI Agent 到外卖平台的桥接网关
- Agent：接入 Clawdot 的 AI Agent（非用户）
- User Token：外卖用户身份标识
- API Key：Agent 身份标识，`clw_` 前缀

## Style preferences

- Use active voice and second person ("you")
- Keep sentences concise — one idea per sentence
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## 视觉调性指南

视觉风格关键词：活力 · 亲和 · 科技感 · 不端着

核心感受：有温度的科技品牌——足够专业让人信任，又足够亲和让人喜欢。

### 色彩体系

#### 主色调

| 色彩 | 色值 | 使用场景 |
|------|------|----------|
| 虾橙 Shrimp Orange | `#E8593C` | 品牌主色，logo、重要按钮、强调元素 |
| 深墨黑 Ink Black | `#1A1A1A` | 文字、描边、深色背景 |

#### 辅助色

| 色彩 | 色值 | 使用场景 |
|------|------|----------|
| 暖粉 Warm Pink | `#F5A89A` | 浅色背景、hover 状态、柔和装饰 |
| 奶白 Cream White | `#FFF9F5` | 页面背景、留白区域 |
| 科技蓝 Tech Blue | `#3B82F6` | AI/技术相关内容的点缀色 |
| 生态绿 Eco Green | `#34D399` | 成功状态、生态/可持续相关内容 |

#### 色彩使用原则

- 虾橙为绝对主角，出现面积占视觉元素的 40-60%
- 深墨黑用于文字和结构，保证信息清晰
- 辅助色不超过视觉面积的 20%，用于丰富层次
- 避免大面积使用冷灰色，保持温暖基调

#### Mintlify docs.json 色彩映射

- `colors.primary` → `#E8593C`（虾橙）
- `colors.light` → `#F5A89A`（暖粉，浅色模式强调）
- `colors.dark` → `#D14430`（深虾橙，深色模式强调）
- `colors.background.light` → `#FFF9F5`（奶白）

#### Mermaid 图表色彩规范

- Clawdot/Gateway 核心节点：`fill:#fde8e4,stroke:#E8593C,stroke-width:2px`
- AI Agent 节点：`fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px`（科技蓝系）
- 重要/确认步骤：`fill:#f9c4bc,stroke:#D14430,stroke-width:2px`
- 平台/外部服务节点：使用默认样式，不额外着色

### Logo 使用规范

Logo 构成：小龙虾插画 + "claw" 手写字体 + 圆点（dot）

Logo 变体：
- 完整版：虾插画 + "虾点" 中文 + slogan
- 标准版：虾插画 + "claw" 字样
- 图标版：仅虾插画（用于头像、favicon 等小尺寸场景）

Logo 不可操作：
- 不可改变虾橙主色
- 不可拉伸变形
- 不可在杂乱背景上使用
- 不可将虾的方向反转

### 字体系统

| 场景 | 中文字体 | 英文字体 | 备选 |
|------|----------|----------|------|
| 标题 | 思源黑体 Bold | Montserrat Bold | 阿里巴巴普惠体 Bold |
| 正文 | 思源黑体 Regular | Inter Regular | 苹方 Regular |
| 品牌名 "claw" | — | 手写风格（logo 专用）| — |
| 数据/数字 | — | DIN Pro / Montserrat | — |

字体使用原则：
- 标题层级清晰，不超过三级
- 正文字号不小于 14px（移动端）/ 16px（PC端）
- 行距 1.5-1.8 倍
- 手写体仅限 logo 中的 claw 字样

## Content boundaries

- 文档面向 Agent 开发者，不涉及内部管理后台
- API 文档覆盖所有公开端点，内部端点不记录
- 安全相关：说明机制但不暴露具体实现细节
