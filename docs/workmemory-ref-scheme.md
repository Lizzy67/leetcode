# workmemory 工具结果引用方案

> 一页纸：`docs/workmemory-ref-onepager.html` · 跨端对齐简报：`docs/issue-2520-ref-design.html`

## 1. 目标

- 降低串行/链式调工具时，大段工具结果反复进入模型上下文带来的 **input token** 与时延。
- 避免 URI / `fileId` / 大段文本等精确值被模型多次搬运抄错。
- 支持下游工具入参引用上游工具结果，由 **Runtime** 在执行前解析填参。

非目标：

- 不引入 `save_as_variable` 类显式存变量工具。
- V0 不做快慢系统之间的引用透传（出边界恢复为后续能力）。

---

## 2. 核心概念

| 名称 | 说明 |
|------|------|
| `resultId` | 统一算法：`UUID.randomUUID().toString().substring(0, 8)`（取 32 位 UUID 字符串的前 8 位）。 |
| `toolCallId` | Provider/框架签发的调用关联键，仅用于来源追踪，不进入 `${...}` 身份。 |
| `resultDataList` | 工具返回的业务结果；**Runtime 必须缓存**，作为引用解析主数据源。 |
| `${resultId.jsonpath}` | 模型侧使用的短引用。 |
| Mask policy | 与 **Runtime 绑定**；默认拦截 + 工具覆盖 + 可选正则。 |

### 原则：值可见 / 不可见

| 原则 | 进模型 | 模型输出 | 执行前 |
|------|--------|----------|--------|
| **值不可见** | 加 mask，换成 `${id.path}` | 只能输出引用 | Runtime 还原真值 |
| **值可见** | **原样**输入给模型 | 仍按 SystemPrompt / Skill **只输出引用** | Runtime 还原真值 |

---

## 3. 总体流程

### 3.1 慢系统 Loop（DM ↔ 太初）

```text
DM 调用 MCP 工具
    ↓
缓存到 workmemory（Runtime 缓存 resultDataList）
    ↓
太初按默认/工具 policy（+ 正则）加 mask
    ↓
送模型推理（不可见见引用；可见见原文）
    ↓
模型按 Skill/SystemPrompt 输出引用
    ↓
Runtime 解析引用为真值 → 交 DM 执行
```

### 3.2 逻辑架构（三步）

1. **进模型前**：按默认 policy（约束 uri、fileId 等默认拦截）或工具 policy 标明拦截变量加 mask；支持配置正则约束某类变量值要加 mask；同时 Runtime 缓存工具返回的 `resultDataList`。
2. **Skill / SystemPrompt**：约束模型输出引用变量（加 mask 后只能输出引用）。
3. **Runtime**：解析引用变量为真实值（递归遍历入参 JSON：整体引用 + 值内引用）。

---

## 4. 详细设计

### 4.1 resultId 生成

```text
resultId = UUID.randomUUID().toString().substring(0, 8)
```

- 全链路统一此算法，禁止各系统各自另算。
- 示例：`a1b2c3d4` → 引用 `${a1b2c3d4.fileUri}`。

### 4.2 Mask policy

- **默认 policy**：拦截 `fileUri` / `fileId` / `objectId` / `*Url` 等字段。
- **工具 policy**：可增删拦截变量；优先级 **工具配置 > 默认**。
- **正则**：可配置某类变量值命中则加 mask。
- policy 与 Runtime 绑定：一套 Runtime ↔ 一套 policy。

### 4.3 工具入参替换（递归）

对工具入参 JSON **递归遍历所有字段**：

1. **整体变量引用**：整值 = `${resultId.jsonpath}` → 整体替换。
2. **值内引用**：字符串内嵌完整 `${...}` → 就地替换。
3. 未命中 / 类型不匹配 → fail closed。

查找：Runtime 缓存的 `resultDataList`（必要时再查 `dataForTool`）。

### 4.4 SubAgent 特殊规则

- 输出阶段对 URI 等加 mask。
- hook 从自然语言抽出 `${...}`，随 `memoryList` 返回。
- **输入 / 输出 mask 均不还原**；裁剪 `memoryList{引用变量名: 变量值}` 交回父侧。

### 4.5 快慢系统边界

- 引用逻辑在慢系统 / 单 Runtime 内闭环。
- 引用不在快慢系统之间传递；出边界恢复为后续能力。

---

## 5. SystemPrompt 建议

见一页纸 §7。要点：

- 写法：`${<resultId>.<字段路径>}`，`resultId` 为 UUID 前 8 位。
- 已被 mask 或长值：禁止照抄，只出引用。
- 用户原话 / 可独立确定的短字面量仍直接填。

---

## 6. 规范决策（定稿）

| 项 | 定稿 |
|----|------|
| 引用格式 | `${resultId.jsonpath}` |
| resultId | `UUID.randomUUID().toString().substring(0, 8)` |
| 值不可见 | 进模型前加 mask |
| 值可见 | 原样进模型；输出仍只出引用 |
| 入参替换 | 递归；整体 + 值内 |
| Mask | Runtime 绑定；默认字段 + 工具覆盖 + 正则 |
| 缓存 | Runtime 缓存 `resultDataList` |

---

## 7. 一句话总结

**进模型前按 policy 加 mask 并缓存 resultDataList；模型按 Prompt/Skill 只出引用；Runtime 把引用还原成真值再调工具。**
