# 对话内 HTML 渲染方案

> 与 `agent_html_preview_proposal.pptx` 同大纲（7 页）

---

## 01 问题定义

**需要：** 在端侧对话中直接渲染并展示模型生成的 HTML 内容。

### 典型场景：个人健康分析报告

用户：「帮我生成最近的个人健康分析报告」

1. Agent 调用「运动健康数据」Skill 拉取指标  
2. 模型结合数据，用图表/卡片等图形化方式生成 HTML  
3. 在对话中直接展示可交互报告（而不是源码或附件）

**成功标准：** 会话内可见、可交互；无需下载后另开应用。

**本质诉求：** 不是「模型会不会写 HTML」，而是对话产品能否完成「取数 → 可视化生成 → 端内安全渲染」。

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

**结论：** 生成 / 落盘 / 同步已通；断点在渲染 + 安全。

场景映射：Skill 取数 ⊂ 生成层；图形化 HTML ⊂ 生成层；对话内看见 ⊂ 渲染层；防脚本越权 ⊂ 安全层。

---

## 03 竞品对比

| 维度 | OpenClaw | Cursor | Claude | Gemini | ChatGPT | Manus |
|------|----------|--------|--------|--------|---------|-------|
| 对话内实时预览 | 强（show_widget） | 弱*（偏 IDE） | 强（Artifacts） | 中～强（Canvas 预览） | 中（Canvas/部分预览） | 强（托管预览） |
| 呈现形态 | Widget/Canvas | 工作区文件 | 侧栏 Artifact | Canvas 工作区 | Canvas + 代码解释器 | 站点/App 预览 |
| 数据/工具 | Skill/工具调用 | FS/终端/浏览器 | 工具 + MCP | 工具 + Workspace | GPTs / ADA 取数画图 | Agent 全流程 |
| 安全隔离 | 双层 iframe 沙箱 | 工作区隔离 | 独立域 + 严 CSP | 平台沙箱 | 平台沙箱 | 托管隔离 |
| 分享 | pin/渠道 | Git/PR | Publish 链接 | 分享/导出 Docs | 分享链接（偏账号） | 一键 publish |
| 对我们启示 | widget 语义+沙箱 | 复用 write，不强造工具 | 单文件预览体验 | Canvas+预览可参考 | 取数可视化可参考 ADA | 后期分享可参考 |

\* Cursor 强在仓库内工程能力，对话内「小工具预览」不是主路径。

**对标优先级：** Claude Artifacts / OpenClaw Widget → Gemini/ChatGPT Canvas → 分享演进参考 Manus。

---

## 04 现状与目标架构 Gap

### 现状

```text
Skill 取数 → 模型生成 HTML → write → 云空间同步 → 端 REST 可下载
```

用户感知：多为附件或源码，「报告」没有在对话里长出来。

### 目标

```text
…… → 识别为 HTML 预览 → sandbox iframe/WebView → 会话内可见可交互 →（可选）分享
```

### Gap（按优先级）

| 优先级 | Gap |
|--------|-----|
| P0 | 端侧无 HTML 预览容器（iframe / WebView） |
| P0 | 缺 preview 元数据（mime、preview.kind、sync_status、file_id） |
| P0 | 缺安全默认（sandbox=allow-scripts，慎开 allow-same-origin） |
| P1 | 同步就绪信号、刷新/降级 |
| P2 | 流式通道、混合预览、对外分享 |

---

## 05 实现方案对比（三列）

| | 方案 A：下载后推送到端渲染 | 方案 B：模型输出流式到端实时渲染 | 方案 C（混合）：流式粗预览 + 完成后落盘定稿 |
|--|---------------------------|----------------------------------|-----------------------------------------------|
| 流程 | write→同步→REST 下载全文→一次加载 | token/delta→端 buffer→边收边刷新 | 流式先出粗画面→同时/完成后 write 同步→完整版替换 |
| 优势 | 稳、完整、易刷新/回放、贴合云空间 | 首屏快、体感像流式 MD | 体验接近 B，正确性兜底靠 A，适合报告类长 HTML |
| 劣势 | 需等生成+同步才出首屏 | 未闭合标签易花屏、脚本易重复、要推送通道 | 状态机更复杂，需明确粗预览/定稿切换 |
| 依赖 | write+云空间+端预览容器 | 流式协议+端节流策略 | A+B 能力叠加 |
| 建议 | **一期默认** | 二期体验增强 | **报告场景推荐演进** |

---

## 06 实现示例

### 工具返回约定

```json
{
  "path": "artifacts/health-report.html",
  "cloud_file_id": "f_xxx",
  "mime": "text/html",
  "sync_status": "synced",
  "preview": { "kind": "html", "entry": true }
}
```

### 方案 A

```javascript
const html = await downloadText(fileId);
iframe.sandbox = "allow-scripts";
iframe.srcdoc = html; // 默不加 allow-same-origin
```

### 方案 C

```javascript
onDelta(t => { buf += t; schedulePaint(buf); });
onDone(async () => {
  await writeAndSync(finalHtml);
  iframe.srcdoc = await downloadText(id);
});
```

### 健康报告串接

1. Skill 获取运动健康数据  
2. 模型生成含图表的单文件 HTML（CSS/JS 尽量内联）  
3. write → 云空间同步就绪  
4. 端 REST 下载 → sandbox 预览  
5. 用户在会话内查看/交互  

---

## 07 结论与建议

1. **问题本质：** 对话内安全渲染可视化 HTML，不是再造存储。  
2. **能力优先级：** 先补渲染 + 安全；分享与流式后置。  
3. **竞品对标：** Claude Artifacts / OpenClaw Widget；Canvas 作参考；分享看 Manus。  
4. **方案选择：** 一期默认 A；报告等待较长时演进 C；纯 B 不作唯一路径。  
5. **安全底线：** 模型 HTML=不可信；`allow-scripts`；慎开 `allow-same-origin`。  
6. **下一步：** 元数据约定 + 端预览卡片 + sandbox；用「健康分析报告」做验收场景。
