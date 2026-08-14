# workmemory 工具结果引用方案

> 对齐 TaiChu [#2520](https://taichu.fun/gitea/SystemAgentDev/TaiChu/issues/2520) V0 与 Lizzy67 定稿要点。  
> 一页纸：`docs/workmemory-ref-onepager.html` · 跨端对齐简报：`docs/issue-2520-ref-design.html`

## 1. 目标

- 降低串行/链式调工具时，大段工具结果反复进入模型上下文带来的 **input token** 与时延。
- 避免 URI / `fileId` / 大段 JSON 等精确值被模型多次搬运抄错。
- 支持下游工具入参引用上游工具结果，由 **太初 Runtime / DM** 在执行前解析填参。
- 跨端（PC → taichu-service）只传递 summary 实际使用的引用（`referenceBundle`），不改 Relay 公共协议。

非目标：

- 不引入 `save_as_variable` 类显式存变量工具。
- V0 不做快慢系统之间的引用透传（出边界恢复为后续能力）。
- V0 不建设共享 Artifact Service / 跨实例长期恢复。

---

## 2. 核心概念

| 名称 | 说明 |
|------|------|
| `resultId` | **Runtime 生成的 UUID**（opaque 128-bit）。公开引用身份，不再由 `toolCallId` 截断 hash 派生。 |
| `toolCallId` | Provider/框架签发的调用关联键，仅用于来源追踪或内部幂等索引，不进入 `${...}` 身份。 |
| `workmemory` | 会话级工作记忆。**可见值**：仅内存临时保存；**不可见精确值**：持久化到 sessionStore Message.`extendData`。 |
| `resultDataList` | 工具返回的业务结果（JSON 可寻址）。引用解析主数据源之一。 |
| `dataForTool` | 执行/端侧附加数据。次级查找源；已有非空 `dataForTool` 时 #1919 原生契约优先。 |
| `${resultId.jsonpath}` | 模型可见的短引用控制面。 |
| CapturePolicy | 与 **Runtime 绑定** 的 mask/捕获策略；一套 Runtime ↔ 一套 policy。 |
| `referenceBundle` | 跨端按需导出的精确值包；与公共 `SubagentRunResult` 平级私有字段 / extendData。 |

原则：

- **引用控制面**（模型可见）：短 token `${uuid.selector}`。
- **精确值数据面**（模型不可见）：WM / Reference Map / `extendData.toolResultReferences` / bundle。
- **执行时才还原**：原始 ToolCall/history 保留 ref；只在执行副本中恢复真值。

---

## 3. 总体流程

### 3.1 慢系统 Loop（DM ↔ 太初）

```text
DM 调用 MCP 工具
    ↓
DM 将结果缓存到 workmemory
    ↓
太初按 Runtime policy 对结果加 mask（不可见字段 → ${uuid.path}）
    ↓
送模型推理（模型输出带引用）
    ↓
太初还原引用为真值
    ↓
交 DM 执行；若 DM 侧已无引用 token，则无需再次还原
```

### 3.2 跨端（#2520 五阶段）

```text
捕获 → PC 内流转 → summary 按需导出 bundle → service 导入/remap → sink execution-only resolve
```

逻辑架构图：`docs/workmemory-logic-architecture.html`  
跨端对齐简报：`docs/issue-2520-ref-design.html`

---

## 4. 详细设计

### 4.1 resultId = UUID

| 项 | 定稿 |
|----|------|
| 生成方 | Runtime（统一生成，禁止各系统 `UUID[:8]` 或各自 hash） |
| 形式 | 标准 UUID / 128-bit opaque，parser **不**固化为 8 位 hex |
| 与 toolCallId | 解耦；需要幂等时用内部 `invocationId → resultId` 索引 |
| 冲突 | 相同 resultId + 相同 value → 幂等；相同 ID + 不同 value → fail closed |

背景：#2520 Review concern 指出旧方案把 Artifact 身份、ToolCall 幂等键、Session 命名空间压进 32-bit `resultId`，跨端协议一旦固化迁移成本高。

### 4.2 可见 vs 不可见

| 场景 | 模型侧 | 存储 |
|------|--------|------|
| 值不可见（URI / fileId…） | policy 替换为 `${uuid.path}` | **持久化**到 sessionStore，挂在 ToolResult message 的 `extendData.toolResultReferences` |
| 值可见（需读正文再加工） | 结果根目录缓存到工作区；Prompt/Skill 要求输出引用 | workmemory **仅内存**，不持久化 |

`extendData` 逻辑结构示例：

```json
{
  "toolCallId": "call-001",
  "toolName": "invoke.DocTranslate",
  "toolIsError": false,
  "toolResultReferences": {
    "version": 1,
    "artifacts": [
      {
        "referenceId": "019f0000-0000-7000-8000-0000000000a12",
        "sourceToolCallId": "call-001",
        "values": {
          "fileLink": "https://download.example/very-long-signed-url",
          "fileId": "file-7f31..."
        }
      }
    ]
  }
}
```

约束：原值不得进入普通日志、UI 投影或 Provider request。Session reopen 时从完整历史聚合 Reference Map，再安装模型上下文。

### 4.3 Mask policy（绑定 Runtime）

- 通用默认：字段名命中 `fileUri` / `fileId` / `objectId` / `*Url` 等指针型 → 默认 mask。
- 工具覆盖：单工具可增删 mask 字段；优先级 **工具配置 > Runtime 默认**。
- 修改 policy 需重建 Runtime（与 #2520 CapturePolicy 不可变快照一致）。
- 约束序：**mask > Skill > SystemPrompt**（Prompt 为软兜底，建议 token>12 禁照抄）。

### 4.4 工具入参替换（递归）

对工具入参 JSON **递归遍历所有字段**：

1. **整体变量引用**：字段值整段等于 `${resultId.jsonpath}` → 整体替换为解析值。
2. **值内引用**：字符串内部嵌有完整 `${...}` token → 就地替换 token。
3. 未命中 / 类型不匹配 / 跨 session → fail closed，禁止把未解析 `${...}` 交给下游工具。

查找顺序建议：`resultDataList` → `dataForTool` / Reference Map values。

> 说明：#2520 对 **sink / summary 交付** 仍要求「完整 token 独占 string、禁止拼接 URL」。DM 入参侧按本条支持递归与值内替换；跨端 summary 扫描仍只认完整独立 token。

### 4.5 SubAgent 特殊规则

- 输出阶段即对 URI 等加 mask。
- 特殊工具 / hook：从返回自然语言中抽取 `${...}`，连同 `memoryList` 返回。
- **输入中的 mask 不还原；输出中的 mask 也不还原。**
- 需裁剪 `memoryList{引用变量名: 变量值}` 交回父侧，由父 Runtime 导入/remap。

### 4.6 快慢系统边界

- UAT：DM 传快系统的上下文中当前 **不会** 出现指代。
- 引用逻辑需在慢系统 / 单 Runtime 内闭环。
- 引用不在快慢系统之间传递；出边界恢复为后续能力。

### 4.7 跨端 referenceBundle（摘要）

- 放在 terminal private payload / extendData，**不修改 Relay 协议**。
- `items.sourceReference` 集合必须等于 summary 中唯一完整 ref 集合。
- service 侧校验 → 写入 parent Store → remap 为 service-local UUID ref → 主 Agent 只见本地引用。
- 融合回复示例：`下面是脑图 ${uuid.fileLink}` —— 交付层保留完整 token，禁止截断或把内部 ref 暴露给用户。

---

## 5. SystemPrompt 建议

见一页纸 §8（可直接嵌入）。要点：

- 写法：`${<resultId>.<字段路径>}`，`resultId` 为 UUID。
- 完整参数值时，整个参数必须等于占位符本身。
- 允许值内引用时，仍禁止改写 UUID 或路径。
- 用户原话 / 可独立确定的短字面量仍直接填。

---

## 6. 错误处理（建议）

| 错误 | 含义 |
|------|------|
| `ref_syntax_error` | 引用格式非法 |
| `ref_not_found` | resultId 不存在或已随 Message TTL 失效 |
| `path_not_found` | jsonpath 无匹配 |
| `ref_type_mismatch` | 解析值类型与参数 schema 不匹配 |
| `ref_collision` | 相同 ID 不同 value |
| `bundle_integrity_error` | 跨端 bundle 缺项/多项/digest/kind 失败 |

失败时应明确返回给模型或 fail closed；禁止静默降级为长文本搬运。

---

## 7. 规范决策（定稿）

| 项 | 定稿 |
|----|------|
| 引用格式 | `${resultId.jsonpath}` |
| resultId | UUID（Runtime 生成） |
| toolCallId | 仅追踪 / 内部幂等 |
| 不可见值存储 | Message.`extendData.toolResultReferences` |
| 可见值存储 | 内存 WM + 工作区缓存，不持久化 |
| 入参替换 | 递归；整体 + 值内 |
| Mask | Runtime 绑定 policy |
| SubAgent | 出入 mask 不还原；交 memoryList |
| 快慢边界 | V0 不传引用 |
| 跨端 | #2520 `referenceBundle` v1 |

---

## 8. 一句话总结

**工具结果按 policy 投影为 UUID 引用；不可见精确值进 Message.extendData，可见值只活在内存；太初/DM 在执行前递归还原；SubAgent 用 memoryList 交包；跨端走 #2520 referenceBundle。**
