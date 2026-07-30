# Agent 对话内 HTML 生成与端侧呈现

> 系统方案说明（与 `agent_html_preview_proposal.pptx` 同内容）

---

## 01 先把问题说完整

**用户真正要的**

- 在对话里看到可点可交互的页面，而不是只能复制的源码
- 可刷新、可回看，最好可分享
- 体验对标：Claude Artifacts / OpenClaw Widget

**容易误判的点**

| 误判 | 正解 |
|------|------|
| 需要 `generate_html` 神器 | 生成是 LLM 文本能力 |
| 云空间「不支持」= 存不了 | 多半是预览/白名单/端能力问题 |
| 有 `write` 就等于能预览 | 还缺识别 + 渲染容器 |
| 流式下发 = 必须上存储 | 流式与存储是两条可选路径 |

**本次要讲清**

1. 能力分层：生成 → 落盘 → 同步 → 识别 → 渲染 → 安全 → 分享  
2. 竞品四类范式与可抄点  
3. 我们已有链路与缺口  
4. 双路径：完整下载 vs 流式  
5. 安全边界与落地节奏  

---

## 02 能力分层：支持 HTML 到底需要什么

| 层 | 含义 | 我们状态 |
|----|------|----------|
| 1. 生成 | LLM 产出 HTML/CSS/JS 文本 | 已有 |
| 2. 落盘 | `write` / `edit` 写入 workspace | 已有 |
| 3. 同步 | workspace → 华为云空间 | 已有 |
| 4. 识别 | MIME / 扩展名 / preview hint | 待补齐 |
| 5. 渲染 | iframe（Web）/ WebView（原生） | **缺口** |
| 6. 安全 | sandbox / CSP / 独立源 | **缺口** |
| 7. 分享 | 稳定 URL / TTL / 历史回放 | 可选增强 |

**结论：** 不是从 0 做「生成 HTML」。产品断点在「识别 + 端侧安全渲染」。分享与流式是体验增强，不是第一期阻塞项。

---

## 03 竞品范式

### A. Artifact / Widget（Claude · OpenClaw）

单文件自包含页面 → 会话侧栏 sandbox 预览；独立源 + 严 CSP；可 Publish / pin。  
**可抄：** `show_widget` 语义 + 沙箱 iframe。

### B. IDE Agent（Cursor · Claude Code）

HTML 即普通文件；FS + 终端 + 浏览器；交付物是仓库/PR。  
**可抄：** 复用 `write`，不强造 `generate_html`。

### C. App Builder（Manus · Lovable · Bolt · v0）

生成工程 + 托管预览 / WebContainer；发布是一等能力。  
**可抄：** 后期的 publish / TTL 预览域。

### D. Doc Canvas（ChatGPT Canvas）

侧栏协作改文档/代码，不是 HTML runtime。  
**启示：** 别把「编辑面」当成「渲染面」。我们应对标 A，必要时向 C 演进。

---

## 04 现状与目标架构

### 现状（已通）

```text
Agent → write(path, content)
     → workspace 落盘
     → 同步华为云空间（KooDrive）
     → 端 REST 按 file_id 下载
```

断点：下载后当附件/源码，没有「这是网页，请画出来」的产品路径。

### 目标闭环（要补）

- `write` 返回：`file_id` + `mime` + `sync_status`
- 运行时标记：`previewable=html`
- 端：REST 取文本 → iframe/WebView 渲染
- 安全：`sandbox=allow-scripts`（默不加 `allow-same-origin`）
- 可选：`show_widget` 薄封装；流式粗预览，最终仍以完整版为准

### 端到端目标流

```text
用户要交互页
  → 模型生成 HTML
  → write 到 artifacts/*.html
  → 云空间同步就绪
  → 工具结果带 file_id/mime
  → 端下载
  → sandbox iframe/WebView 呈现
  → 用户可交互
  →（可选）再次 write 覆盖并刷新
  →（可选）云空间 URL/签名链分享
```

---

## 05 两条渲染路径

### 路径 A · 下载后完整渲染（推荐默认）

**时机：** sync 完成 → REST 拉全文 → 一次加载  

**优点：** 标签完整、脚本只执行一次、可刷新/多端/回放、与云空间零阻抗  

**代价：** 需等生成+同步结束才出画面  

**适用：** 几乎所有一期场景  

### 路径 B · 流式边传边渲染（体验增强）

**时机：** token/delta 推送 → buffer → 节流刷新  

**优点：** 首屏更早，体感像流式 Markdown  

**挑战：** 未闭合标签破坏 DOM；`srcdoc` 重设导致脚本重复跑；需要独立推送通道  

**建议：** 结构可增量，脚本等 done；最终仍 write 定稿  

---

## 06 关键概念与安全默认

### MIME（Content-Type）

给字节贴类型标签：`text/html` 当网页，`octet-stream` 常当附件。  
实践：同步带 `mime=text/html`；若云侧一律 `octet-stream`，端按 `.html` 自行处理。

### iframe / WebView

同一类能力：Web 控制台用 iframe，原生 App 用 WebView。  
喂法：`srcdoc`/`loadData`（下载文本）或 `src`/`loadUrl`（URL）。  
没有它们：只能下载或看源码。

### 安全默认

模型 HTML = 不可信内容。  
`sandbox=allow-scripts`，默认不加 `allow-same-origin`。  
限制外链、预览域与主站 cookie 隔离、体积上限；需要时用 postMessage 桥。

---

## 07 建议契约与实现示例

### write / 同步完成后的建议返回

```json
{
  "path": "artifacts/demo/index.html",
  "cloud_file_id": "f_xxx",
  "mime": "text/html",
  "sync_status": "synced",
  "preview": { "kind": "html", "entry": true }
}
```

### 路径 A

```javascript
const html = await downloadText(fileId);
iframe.sandbox = "allow-scripts";
iframe.srcdoc = html;
```

### 路径 B

```javascript
onDelta(t => { buf += t; schedulePaint(); });
onDone(() => { iframe.srcdoc = buf; });
```

### 端侧最小产品行为

1. 识别 `preview.kind===html` 或 `.html` → 预览卡片，而非纯附件  
2. 未 synced 显示加载态；就绪后再 REST 拉正文  
3. Web 用 sandbox iframe；原生用 WebView；失败降级下载/外开  
4. 可选 `show_widget`：对模型暴露「请展示」语义，内部仍走 write+同步  

---

## 08 落地路径

| 阶段 | 目标 | 事项 |
|------|------|------|
| Phase 0 | 对齐与验通 | 确认可写 `.html`；手工同步下载；MIME/扩展名策略 |
| Phase 1 | 完整下载渲染 | 返回 mime/file_id/hint；预览卡片；sandbox 默认策略 |
| Phase 2 | 体验与稳定 | 同步就绪推送；刷新/降级；单文件内联约定 |
| Phase 3 | 流式 + 分享 | delta 通道；脚本延后执行；签名 URL / TTL |

---

## 09 结论与建议

1. **定位**：对标 Artifact/Widget，而不是一上来做全栈 App Builder。  
2. **真相**：生成靠模型；write+云空间已解决分发；缺口在端侧安全渲染。  
3. **默认方案**：路径 A——同步完成后下载全文，sandbox 一次渲染。  
4. **增强方案**：路径 B——流式粗预览提升体感，定稿仍落盘；勿替代 A。  
5. **安全底线**：模型 HTML 当不可信；`allow-scripts`，慎开 `allow-same-origin`。  
6. **下一步**：Phase 0 验通 → Phase 1 预览卡片上线 → 再评估是否做流式。
