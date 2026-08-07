# workmemory 工具结果引用方案

## 1. 目标

- 降低串行/链式调工具时，大段工具结果反复进入模型上下文带来的 **input token** 与时延。
- 支持下游工具入参引用上游工具结果，由 **DM/Runtime 统一解析填参**。
- 业务工具无感；引用能力由 Skill 参数显式声明。

非目标：

- 不涉及密钥/脱敏专项设计（假定工具不返回密钥）。
- 不引入 `save_as_variable` 类显式存变量工具（默认写入 workmemory 即可）。

---

## 2. 核心概念

| 名称 | 说明 |
|------|------|
| `resultId` | 一次工具调用结果的唯一 ID。建议直接使用 `tool_call_id`，字符集：`[A-Za-z0-9_-]+`。 |
| `workmemory` | 会话级工作记忆，按 `resultId` 索引存放工具执行结果。 |
| `resultData` / `resultDataList` | 工具返回的业务结果（业务自定义 JSON）。**引用解析的主数据源**。 |
| `dataForTool` | 工具执行附加数据（如给端侧打开的长 URI、展示字段等）。**次级查找源**。 |
| `$` 引用 | Skill 入参中对历史结果的 jsonpath 引用。 |

原则：

- **回灌模型**：短摘要 + `resultId`（及必要的小字段）。
- **链式填参**：DM 从 workmemory 取值注入下游 args，**不必把大字段展开进 prompt**。

---

## 3. 总体流程

```text
模型发起工具调用（可含 plan / 多工具）
    ↓
执行工具 A
    ↓
DM 将结果写入 workmemory[resultId=A]
    （resultData 必写；dataForTool 可选）
    ↓
回灌模型：modelSummary + resultId
    ↓
模型再调工具 B，入参中带 ${A:$.x}
    ↓
DM 在 invoke 前解析引用 → 查 workmemory → 替换入参
    ↓
执行工具 B
```

运行视图见：`docs/assets/workmemory-runtime-view.png`。

---

## 4. 详细设计

### 4.1 工具执行后：默认写入 workmemory

每次工具调用结束（含 Skill 的 `invoke` / `exec`），DM **默认**写入：

```json
{
  "resultId": "call_01",
  "toolName": "get_health_summary",
  "status": "success",
  "resultData": { },
  "dataForTool": { },
  "modelSummary": "近7日步数汇总已生成"
}
```

说明：

| 字段 | 要求 |
|------|------|
| `resultData` | 业务结果，须为 JSON 可寻址结构，便于 jsonpath。 |
| `dataForTool` | 可选；端侧或执行层附加数据，同样建议 JSON 可寻址。 |
| `modelSummary` | 可选；专门用于回灌模型的短文本。 |

**会话隔离**：按 session 分区。  
**容量**：建议限制条数与总字节；超限按 LRU/最旧淘汰，并允许返回 `resultId` 失效类错误。

**对 `resultData` 的建议约束（业务可裁剪）：**

- 优先结构化对象，避免整包无结构巨型字符串。
- 超大字段（如整页 HTML）可单独成字段，引用时按 path 精确取用。
- 列表类结果可约定上限，或同时提供聚合字段供引用。

**对 `dataForTool` 的建议约束：**

- 仅放「执行/端侧需要」的附加字段（例如长 `authorize_url`）。
- 字段含义在工具文档中写清，避免与 `resultData` 职责混淆。

### 4.2 Skill：参数显式声明支持引用

仅在 schema 中声明了可引用的参数，才允许出现 `$` 引用。

示例：

```json
{
  "type": "object",
  "properties": {
    "html": {
      "type": "string",
      "x-ref": true
    },
    "title": {
      "type": "string"
    }
  }
}
```

可选扩展：

```json
{
  "x-ref": true,
  "x-ref-source": "both"
}
```

`x-ref-source` 取值建议：

| 值 | 含义 |
|----|------|
| `resultData` | 只从 `resultData` 解析（默认可设为此，更严） |
| `dataForTool` | 只从 `dataForTool` 解析 |
| `both` | 先 `resultData`，找不到再 `dataForTool`（默认也可设为此，更灵活） |

**未声明 `x-ref` 的参数：**

- **推荐**：若值匹配引用语法，直接校验失败（防止误解析/注入）。
- 备选：当作普通字面量（兼容性更好，安全性较弱）。

### 4.3 引用语法

推荐格式：

```text
${resultId:jsonpath}
```

示例：

```text
${call_01:$.summary}
${call_01:$.data.items[0].name}
${call_auth:$.authorize_url}
```

规则：

1. `resultId` 仅允许 `[A-Za-z0-9_-]+`。
2. 以 **第一个 `:`** 为分隔符；其后整段为 jsonpath。
3. jsonpath 建议限制为只读子集，例如：`$.a.b[0].c`。
4. 不建议使用 `${id.path.path}` 并用「第一个点」切开——jsonpath 本身含多级 `.`，易歧义。

### 4.4 DM：在 invoke/exec 入参阶段解析

**时机：** 真正调用工具之前。  
**对象：** 仅处理声明了 `x-ref` 的参数。  
**不做：** 不对工具「输出」做引用解析（输出只负责写入 workmemory）。

解析流程：

```text
1. 检测参数值是否为 ${resultId:jsonpath}
2. 校验 resultId、jsonpath 合法性
3. 按 resultId 查找 workmemory
4. 按 x-ref-source 规则在 resultData / dataForTool 上执行 jsonpath
5. 用解析值替换原参数
6. 再执行 invoke/exec
```

查找顺序（当 `x-ref-source = both` 或未声明时）：

```text
resultData（resultDataList）→ 若 path 不存在 → dataForTool → 仍无则失败
```

类型处理：

- jsonpath 结果类型应与参数 schema 兼容。
- 若参数要求 `string` 却取到 object/array：**推荐报错**，不默默 `JSON.stringify`（除非该参数明确声明接受序列化）。

### 4.5 回灌模型的内容

每次工具结束后回给模型的内容建议最小化，例如：

```json
{
  "resultId": "call_01",
  "status": "success",
  "summary": "近7日步数汇总已生成",
  "hint": "下游可通过 ${call_01:$.summary} 引用"
}
```

完整 `resultData` / `dataForTool` **默认不进入**模型上下文。

---

## 5. 错误码（建议）

| 错误 | 含义 |
|------|------|
| `ref_syntax_error` | 引用格式非法 |
| `ref_not_allowed` | 参数未声明 `x-ref` |
| `ref_not_found` | resultId 在 workmemory 中不存在或已淘汰 |
| `path_not_found` | jsonpath 在允许的数据源中无匹配 |
| `ref_type_mismatch` | 解析值类型与参数 schema 不匹配 |

失败时应返回明确错误给模型，便于重试或改写计划；勿静默把 `${...}` 原样传给下游工具。

---

## 6. 示例

### 6.1 健康数据 → 再处理

```text
① get_health_summary
   resultId = call_01
   resultData = { "summary": "步数偏少", "steps": 12345 }
   回模型：{ resultId, summary }

② generate_advice
   args.text = "${call_01:$.summary}"
   DM 解析 → text = "步数偏少" → 执行
```

### 6.2 授权 URL 在 dataForTool

```text
① request_auth
   resultId = call_auth
   resultData = { "status": "pending", "auth_session_id": "as_1" }
   dataForTool = { "authorize_url": "https://...很长..." }

   端：从 dataForTool.authorize_url 打开授权页
   模型：只看 status + auth_session_id

② 若某工具参数确实需要 URL，且声明 x-ref + 允许 dataForTool：
   args.url = "${call_auth:$.authorize_url}"
   DM 在 resultData 未命中后，从 dataForTool 取出
```

---

## 7. 与链式调度的关系

本方案可独立落地，也服务于「模型一次 plan，Runtime 链式调度」：

1. 模型输出多步工具计划（可含 `${resultId:jsonpath}` 入参模板）。
2. DM 按依赖执行；每步结果写入 workmemory。
3. 下游步骤 invoke 前解析引用并填参。
4. 仅在计划结束或授权等卡点时，把短状态回灌模型。

这样可同时减少：

- **模型往返轮次**（链式/并行调度）
- **每轮 input token**（大结果不进 prompt，只留 resultId + 摘要）

---

## 8. 规范决策（建议定稿）

| 项 | 建议 |
|----|------|
| 引用格式 | `${resultId:jsonpath}` |
| 未声明 x-ref 却出现引用语法 | 校验失败 |
| 默认 x-ref-source | `both`（先 resultData 再 dataForTool）或更严的 `resultData` |
| 类型不匹配 | 报错 |
| resultId | 复用 `tool_call_id` |

---

## 9. 一句话总结

**工具结果默认进入 workmemory；Skill 参数显式允许 `${resultId:jsonpath}`；DM 在 invoke 前解析并填参；模型只看短摘要与 resultId。**
