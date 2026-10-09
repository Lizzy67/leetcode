# 对话内 HTML 渲染方案

> 与 `agent_html_preview_proposal.pptx` 同大纲

---

## 01 问题定义

**需要：** 在端侧对话中直接渲染并展示模型生成的 HTML 内容。

### 典型场景：个人健康分析报告

用户：「帮我生成最近的个人健康分析报告」

1. Agent 调用「运动健康数据」Skill 拉取指标  
2. 模型结合数据，用图表/卡片等图形化方式生成 HTML  
3. 在对话中直接展示可交互报告（而不是源码或附件）

**成功标准：** 会话内可见、可交互；无需下载后另开应用。

---

## 02 实现能力路径

| 环节 | 含义 | 状态 |
|------|------|------|
| 生成 | LLM + Skill 取数，产出可视化 HTML | 已有 |
| 落盘 | `write` 写入 workspace | 已有 |
| 同步 | workspace → 华为云空间 | 已有 |
| 渲染 | iframe / WebView 会话内展示 | **缺口** |
| 安全 | sandbox / CSP / 不可信隔离 | **缺口** |
| 分享 | 链接 / 回放 / 转发 | 可选增强 |

---

## 03 竞品对比

| 维度 | OpenClaw | Cursor | Claude | Gemini | ChatGPT | Manus |
|------|----------|--------|--------|--------|---------|-------|
| 对话内预览 | 强（widget） | 弱*（偏 IDE） | 强（Artifacts） | 中～强（Canvas） | 中（Canvas/ADA） | 强（托管预览） |
| 呈现形态 | Widget | 工作区文件 | 侧栏 Artifact | Canvas | Canvas+解释器 | 站点/App |
| 数据/工具 | Skill/工具 | FS/终端 | 工具+MCP | 工具+Workspace | GPTs/ADA | Agent 全流程 |
| 安全隔离 | 双层 iframe | 工作区隔离 | 独立域 CSP | 平台沙箱 | 平台沙箱 | 托管隔离 |
| 分享 | pin/渠道 | Git/PR | Publish | 分享/导出 | 分享链接 | 一键发布 |
| 启示 | widget+沙箱 | 复用 write | 单文件预览 | Canvas 可参考 | 取数可视化 | 分享演进 |

对标优先级：Claude Artifacts / OpenClaw Widget → Gemini/ChatGPT Canvas → 分享演进参考 Manus（接近方案 4）。

---

## 04 现状与目标 Gap

**现状：** Skill → 生成 HTML → write → 云空间 → REST 可下载 → 常停在附件/源码  

**目标（方案 4 取向）：** … → 发布预览 URL → WebView 打开 → 会话内交互  

**Gap：** P0 预览容器 / 可打开 URL 或 mime / 沙箱与预览域；P1 同步就绪；P2 流式与混合体验。

---

## 05 四种实现方案

| | 方案 1 A：下载后渲染 | 方案 2 B：流式实时 | 方案 3 C：混合 | **方案 4 D：云预览出链接** |
|--|--|--|--|--|
| 流程 | REST 拉全文 → srcdoc/loadData | delta → 边收边渲 | 流式粗预览 + 落盘定稿 | **发布预览服务 → URL → WebView.loadUrl** |
| 优势 | 稳、贴合现有云空间 | 首屏快 | 体验+正确性兼顾 | **端最简；多文件/分享/统一 CSP** |
| 代价 | 端要注入 HTML；多文件弱 | 半截标签/脚本风险 | 状态机复杂 | 需预览域或签名托管网关 |
| 定位 | 轻量闭环 / 兜底 | 体验增强 | 长报告体验 | **中台主路径推荐** |

### 方案 4 要点

```text
Agent 生成 HTML（可 write 云空间作源）
  → 发布到预览 Web 服务（或对象存储签名 URL 网关）
  → 返回 https://preview.xxx/p/{id}/
  → 端 WebView / iframe 直接打开链接
```

- 云空间 = 源文件仓  
- 预览域 = HTTP 渲染入口（可解耦）  
- 不必强制「先下载到本地磁盘」；端打开的是可访问 URL  

---

## 06 实现示例

### 工具返回（方案 4）

```json
{
  "preview_url": "https://preview.xxx/p/abc/",
  "expires_at": "2026-08-01T00:00:00Z",
  "mime": "text/html",
  "source_file_id": "f_xxx"
}
```

### 端侧（方案 4）

```javascript
webView.loadUrl(previewUrl);
// 或 iframe.src = previewUrl; iframe.sandbox = "allow-scripts";
```

### 兜底（方案 A）

```javascript
const html = await downloadText(fileId);
iframe.srcdoc = html;
```

---

## 07 结论与建议

1. **问题本质：** 对话内安全渲染可视化 HTML，不是再造存储。  
2. **方案 4：** 云预览服务生成可渲染链接，WebView 直接打开 —— **中台主路径**。  
3. **与云空间：** 源文件仓 + 预览域渲染入口，可解耦。  
4. **组合：** 主路径 D；兜底 A；长等待用 C；纯 B 不作唯一路径。  
5. **安全：** 独立预览域 + CSP/TTL；WebView 仍按不可信内容隔离。  
6. **下一步：** 预览发布 API + 短链 URL；用健康报告验收会话内 `loadUrl`。
