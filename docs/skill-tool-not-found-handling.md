# 工具不存在（幻觉调用）异常处理与模型反思规范

> 背景：模型按 Skill 调度工具时可能幻觉出不存在的工具并下发到端；端已有“工具不存在”错误返回。  
> 目标：**明确错误标识 → Skill 内产品话术兜底 → 有限次模型反思纠错 → 禁止空转 Loop。**

---

## 一、问题与原则

| 问题 | 要求 |
|------|------|
| 幻觉工具名 / 错误 tool_id | 执行链路给出**机器可识别**的“找不到工具”标识 |
| 用户侧体验 | Skill 内有**产品提供的**异常处理与话术，不可静默失败或乱编 |
| 模型可纠错 | 支持反思后改调合法工具 / 改参数；次数有上限 |
| 防 Loop | 反思失败后必须落到固定话术并结束本轮技能路径 |

**分层原则：**

1. **能拦则先拦（云侧预检）**：下发前用「本 Skill 允许工具集 ∩ 设备 capabilities ∩ ToMP 目录」校验。  
2. **端侧仍是最终真相**：预检漏过或动态不可用时，端返回同一错误码。  
3. **错误码统一**：云预检失败与端执行失败对 Runtime/模型暴露同一语义。  
4. **话术归产品，策略归平台**：文案可配置；重试次数、是否允许反思由平台/Skill 策略约束。

---

## 二、错误标识（执行结果契约）

工具执行（含云侧预检失败模拟的执行结果）统一返回：

```json
{
  "ok": false,
  "error_code": "TOOL_NOT_FOUND",
  "error_class": "tool_resolution",
  "retryable": true,
  "reflectable": true,
  "tool": {
    "requested": "gallery.openAlbumX",
    "normalized": "gallery.openAlbumX"
  },
  "hint": {
    "allowed_tools": ["gallery.search", "gallery.open_album"],
    "suggestions": ["gallery.open_album"]
  },
  "message": "tool not found on device",
  "source": "device"  
}
```

| 字段 | 说明 |
|------|------|
| `error_code` | 固定：`TOOL_NOT_FOUND`（对外稳定标识） |
| `error_class` | `tool_resolution`，便于 Runtime 路由到“解析失败”分支，区别于业务失败 |
| `retryable` | 是否允许再调工具（一般为 true） |
| `reflectable` | 是否允许进入模型反思（见第四节策略） |
| `tool.requested` | 模型原始点名 |
| `hint.allowed_tools` | **本 Skill 当前可调白名单**（强烈建议回传，供反思） |
| `hint.suggestions` | 可选：基于编辑距离/别名表的相近工具 |
| `source` | `cloud_precheck` \| `device` \| `runtime` |

**端侧要求：**  
实际工具不存在时，必须返回可解析的 `TOOL_NOT_FOUND`（或平台映射到该码），禁止只回模糊字符串导致模型无法分支。

**相近但不同的码（勿混用）：**

| error_code | 含义 |
|------------|------|
| `TOOL_NOT_FOUND` | 名字/ID 不存在（幻觉或写错） |
| `TOOL_UNAVAILABLE` | 工具登记存在，但本机不可用（权限/裁剪/capabilities 无） |
| `TOOL_DEPRECATED` | 已废弃，应换 `replace_by` |
| `TOOL_SCHEMA_INVALID` | 工具在，参数不合 schema |
| `TOOL_EXEC_FAILED` | 工具在，执行业务失败 |

Skill 话术与反思策略可按 `error_code` 分别配置；**本需求主路径是 `TOOL_NOT_FOUND`。**

---

## 三、Skill 内异常处理与话术（产品提供）

### 3.1 Manifest 扩展

```yaml
skill_name: gallery.search
skill_version: 2.1.0
requires:
  - tool: gallery.search
    version: ">=2.0.0"
  - tool: gallery.open_album
    version: "^1.0.0"

# 本 Skill 运行时允许模型调用的工具白名单（默认 = requires ∪ optional）
allowed_tools:
  - gallery.search
  - gallery.open_album

exception_handlers:
  TOOL_NOT_FOUND:
    # 产品提供
    user_utterance: "抱歉，我这边暂时没法完成这个操作，你可以换种方式说说看，或者稍后再试。"
    # 可选：更细场景
    variants:
      - when: "after_reflect_exhausted"
        user_utterance: "我没能找到对应的功能入口，建议你打开图库手动试一下，或升级系统后再试。"
    # 平台策略（可默认，产品可覆盖上限内参数）
    policy:
      allow_reflect: true
      max_reflect_rounds: 1          # 推荐 1；全局硬顶建议 ≤2
      on_exhaust: speak_and_end      # speak_and_end | degrade_peer | escalate
```

### 3.2 Skill 正文（md / SOP）约定写法

Skill 说明中增加固定章节，供模型与 Runtime 共同遵守，例如：

```markdown
## 异常处理：工具不存在（TOOL_NOT_FOUND）
1. 若返回 TOOL_NOT_FOUND：仅允许从【本 Skill 允许工具列表】中改选工具重试，禁止再发明新工具名。
2. 反思重试仍失败或次数用尽：向用户输出产品话术（见 exception_handlers），结束本技能，勿继续空转调用。
3. 禁止向用户暴露内部 tool_id / 堆栈；使用配置话术。
```

### 3.3 上架门禁

- 热门/全量 Skill：**`exception_handlers.TOOL_NOT_FOUND.user_utterance` 必填**（产品提供文案）。  
- 未配置时平台默认话术（兜底），但上架流水线打黄灯/阻断（按规范等级）。  
- `allowed_tools` 必须 ⊆ ToMP 已登记 tool；禁止 Skill 暗示未登记工具。

---

## 四、模型反思优化流程

```text
模型产生 tool_call
        │
        ▼
云侧预检：tool ∈ allowed_tools ∩ capabilities ∩ ToMP ?
   │否 → 合成 TOOL_NOT_FOUND (source=cloud_precheck)
   │是 → 下发端执行
        │
        ▼
端返回结果
        │
        ├─ OK → 继续 Skill
        └─ TOOL_NOT_FOUND
                │
                ▼
         reflectable && rounds < max ?
                │是
                ▼
         注入结构化反思上下文给模型：
         - error_code
         - requested tool
         - allowed_tools / suggestions
         - 指令：只能改调白名单内工具或改为向用户澄清；禁止再幻觉新名
                │
                ▼
         模型再决策（1 次为主）
                │
                ├─ 合法 tool_call → 再走预检/执行
                ├─ 澄清/拒答 → 用产品话术或澄清话术结束
                └─ 再次非法 / 超次 → on_exhaust：播报产品话术并结束
```

### 4.1 反思上下文（给模型的短消息，示例）

```text
[System/ToolResult]
error_code=TOOL_NOT_FOUND
requested=gallery.openAlbumX
allowed_tools=["gallery.search","gallery.open_album"]
suggestions=["gallery.open_album"]
instruction: 上一工具不存在。你只能从 allowed_tools 中选择一个重试，或结束并使用 Skill 配置的用户话术。禁止创造新的工具名。剩余反思次数=0。
```

### 4.2 防 Loop 硬约束（Runtime）

| 规则 | 建议默认 |
|------|----------|
| 单次用户请求、同一 Skill 内 `TOOL_NOT_FOUND` 反思次数 | **1**（全局硬顶 2） |
| 连续两次点名不在 `allowed_tools` | 立即 `speak_and_end`，不再问模型 |
| 反思轮次中禁止扩大工具集 | 只能用本 Skill `allowed_tools` |
| 总工具调用步数 | 沿用现有 step budget；`TOOL_NOT_FOUND` 计入步数 |
| 日志 | 记录 `requested`、是否预检拦截、反思次数、最终是否话术收口 |

### 4.3 与“能力不匹配”的分工

| 场景 | 处理 |
|------|------|
| Skill 未 Gate 住、工具本机无 | 更应走 `TOOL_UNAVAILABLE` / Compat；话术可引导升级 |
| 模型编造从未登记的名字 | `TOOL_NOT_FOUND` + 反思/话术 |
| 模型把 A 写成近似名 B | `TOOL_NOT_FOUND` + `suggestions` 辅助一次纠错 |

---

## 五、云侧预检（强烈建议，减少端空跑）

在下发端之前：

```text
resolve(tool_call):
  if tool_id not in ToMP:           return TOOL_NOT_FOUND
  if tool_id not in skill.allowed:  return TOOL_NOT_FOUND
  if tool_id not in device.caps:    return TOOL_UNAVAILABLE  # 或 NOT_FOUND，若产品希望统一话术可映射
  validate schema                   return TOOL_SCHEMA_INVALID if fail
  else dispatch to device
```

预检失败也走同一套 `exception_handlers` + 反思策略，用户无感差异；`source` 仅用于监控。

---

## 六、监控与治理

| 指标 | 用途 |
|------|------|
| `tool_not_found_rate`（按 Skill / 模型） | 发现幻觉热点、Skill 描述不清 |
| `precheck_catch_ratio` | 预检是否挡住端空跑 |
| `reflect_success_rate` | 反思是否值得保留 |
| `exhaust_utterance_rate` | 最终靠产品话术收口占比 |
| Top `requested` 幻觉名 | 反哺 Skill 文档 / 别名表 / 训练 |

可选：对高频幻觉别名建 **tool alias → 正式 tool_id**（平台配置，慎用，避免掩盖 Skill 质量问题）。

---

## 七、分工

| 角色 | 职责 |
|------|------|
| 产品 | 提供各 Skill（或全局默认）`TOOL_NOT_FOUND` 用户话术与变体 |
| 端 | 工具不存在时返回明确 `TOOL_NOT_FOUND`（或可映射码） |
| 云 Runtime / skillGate | 预检、统一错误契约、反思轮次控制、话术收口 |
| Skill 作者 | 写清允许工具与异常 SOP；填写 handlers |
| 平台 | 上架校验 handlers；监控幻觉与反思效果 |
| 模型侧 | 遵守反思指令；禁止白名单外造工具 |

---

## 八、验收标准

1. 端或云对“工具不存在”均能产出稳定 `error_code=TOOL_NOT_FOUND`。  
2. Skill（或全局默认）有产品话术；用尽反思后用户听到/看到该话术并结束，无 10 轮空转。  
3. 反思时模型能拿到 `allowed_tools`（及可选 suggestions），且 Runtime 拒绝白名单外二次幻觉。  
4. 监控可区分：预检拦截 vs 端返回；反思成功 vs 话术收口。

---

## 九、与配套治理文档的关系

- 配套/版本问题：解决「该不该有这个工具」。  
- 本文：解决「模型仍点了不存在工具时怎么标识、纠错、收口」。  
- 二者互补：Gate 降低概率；本机制兜住剩余幻觉与体验。
