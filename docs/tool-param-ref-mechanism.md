# 工具参数引用机制 · 顶层设计与开发接入说明

> 状态：设计稿（可开发接入）  
> 目标：用统一的「参数占位符 + 调用前求值」框架，覆盖跨工具传参、语义标识符消歧等多类场景；工具侧零改动，真实值永远来自查表/记忆，结构性降低幻觉与照抄错误。

---

## 1. 问题与目标

### 1.1 共性痛点

| 痛点 | 表现 |
|------|------|
| 多 Loop | 模型须先查再填（如先 `getAllInstalledApps` 再 `forbidPermission`） |
| 幻觉 | 凭记忆编造标识符（如 `com.douyin.app`）或抄错长串 |
| 工具难改 | 带 `bundleName` / `fileUri` 等参数的工具多，无法逐个改造 |
| Token / 遵从 | 大结果回灌 + 要求原样照抄 → 贵且易错 |

### 1.2 统一目标

1. **正常路径尽量 1 次 Loop 完成调用**（无需先为了拿 ID 多跑一轮）。  
2. **工具零改动**；同类参数自动全覆盖。  
3. **真实标识符永远来自查表 / 工作记忆**，结构性消除「模型编造真值」。  
4. **解析失败短路**：不把 `${…}` 字面量透传给工具；可走查询兜底后重试。

---

## 2. 顶层抽象

### 2.1 一句话

> 模型在工具入参里只表达「引用意图」；**Pre-call 拦截器**在 invoke/exec 前扫描 `${…}`，查表求值后替换为真值，再调工具。

### 2.2 两类引用（同一管道，不同数据源）

```
                    ┌─────────────────────────────────────┐
  模型输出入参       │  ${…} 占位符                         │
                    └─────────────────┬───────────────────┘
                                      ▼
                         Pre-call Interceptor
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
     ① 结果引用              ② 语义实体引用              （可扩展）
   Workmemory 查表         Namespace 词典查表
   resultId + path         ns.entity.attr
              │                       │
              └───────────────────────┴───────────────────────┘
                                      ▼
                              真值回填 → 调工具
```

| 类型 | 语法（建议） | 数据源 | 典型用途 |
|------|----------------|--------|----------|
| **A. 结果引用** | `${<resultId>.<jsonpath>}` | 本会话工具返回（workmemory） | 上一工具的 `fileUri`、大字段等 |
| **B. 语义实体引用** | `${<namespace>.<entity>.<attribute>}` | 全局/会话词典 + 同义词表 | 应用包名、联系人 ID、设备 ID 等 |

> 约定：占位符整体作为参数值；`resultId` / `namespace` / `entity` 段**不含**未转义的歧义分隔（见 §5 解析规则）。

### 2.3 非目标

- 不改造存量工具签名与实现。  
- 不要求模型输出真实 packageName / 长 URI。  
- 不把「默认上一工具 / 枚举点选」等策略全部塞进 Prompt；策略在框架侧，Prompt 只保留短约定。

---

## 3. 适用场景矩阵

### 场景 S1：跨工具结果传递（指针型 / 大字段）

| 项 | 内容 |
|----|------|
| **现象** | 工具 A 返回 `fileUri`，工具 B 需要同一 URI；或大段 text 需原样传下游 |
| **风险** | 照抄截断；或 URI 本不必给模型读 |
| **引用类型** | **A. 结果引用** |
| **解法要点** | 结果默认入 workmemory；送模前可 mask；入参写 `${resultId.path}`；invoke 前展开 |
| **Loop** | 链式场景仍可能多工具，但**无需为「记住/抄写」额外 loop**；mask 后模型只回传占位符 |

### 场景 S2：语义标识符（应用包名等）——重点扩展

| 项 | 内容 |
|----|------|
| **现象** | `forbidPermission(bundleName, …)` 等需要真实 `bundleName`；命名不规范、语义弱 |
| **原路径** | ① `getAllInstalledApps` → ② 再调业务工具（**2 Loop**） |
| **风险** | 凭记忆编造 `com.douyin.app`；工具多无法逐个改 |
| **引用类型** | **B. 语义实体引用** |
| **解法要点** | 入参直接 `${app.抖音.bundleName}`；同义词归一 + 映射表求值；工具无感知 |
| **目标路径** | **1 Loop** 完成业务调用；失败再走查询兜底 |

### 场景 S3：模型需要看见值，但仍须引用传参

| 项 | 内容 |
|----|------|
| **现象** | 要读正文才能决策，下游仍要原值 |
| **引用类型** | **A**（可辅以 Skill 约束） |
| **解法要点** | 真值/摘要可见；入参仍 `${resultId.path}`；「看」与「传」分离 |

### 场景 S4：多候选需消歧（并行工具 / 多安装包）

| 项 | 内容 |
|----|------|
| **现象** | 同名应用多包、或并行多个上传结果 |
| **解法要点** | 映射表返回多候选 → 短路并让模型选；或参数 enum 列出合法 `${…}`；禁止静默猜 |

### 场景 S5：跨轮复用稳定实体

| 项 | 内容 |
|----|------|
| **现象** | 多轮都操作「抖音」 |
| **解法要点** | 语义引用 `${app.抖音.bundleName}` 天然跨轮；结果引用则保留 resultId 或会话短句柄 `${rN}` |

### 场景 S6：引用展开 + 入参策略化格式转换

| 项 | 内容 |
|----|------|
| **现象** | 工具 A 返回标识列表（如 `merged_id_list = [563, 563, …]`）；工具 B 要求 `images: [{"file_id":"563"}, …]` |
| **风险** | 让模型改写结构易截断/类型错；为每个工具改输入输出协议成本高 |
| **引用类型** | **A. 结果引用** + **执行前 Transform** |
| **解法要点** | 模型只写 `images: ${resultId.merged_id_list}` → 拦截器先 resolve 成真列表 → 再按参数 policy 做 map/dict/类型转换 → 调工具 B |
| **policy 语义（示例）** | 对已展开列表逐元素生成 `{"file_id": string(item)}`，得到对象列表 |
| **Loop** | 模型侧仍一次表达引用；结构适配不占用模型抄写，工具零改动 |

**流水线示意：**

```text
模型:  {"images": "${resultId.merged_id_list}"}
          ↓ ① Ref resolve
运行时: {"images": [563, 563, …]}
          ↓ ② Policy transform（读该参数转换策略）
运行时: {"images": [{"file_id": "563"}, {"file_id": "563"}, …]}
          ↓ ③ invoke 工具B
```

---

## 4. 关键设计

### 4.1 统一占位符与解析

**推荐语法：**

```text
${<ref-body>}
```

**A. 结果引用**

```text
${<resultId>.<jsonpath>}
```

- `resultId`：`[A-Za-z0-9]+`（建议 8 位 hex），**不含 `.`**  
- `jsonpath`：字段路径，支持点号嵌套（一期可先简单字段名）  
- 示例：`${a1b2c3d4.fileUri}`、`${a1b2c3d4.data.objectId}`

**B. 语义实体引用（三段式）**

```text
${<namespace>.<entity>.<attribute>}
```

- `namespace`：可扩展命名空间，如 `app`、`contact`、`device`  
- `entity`：实体名（展示名 / 别名均可，先经同义词归一）  
- `attribute`：属性名，如 `bundleName`、`appId`  
- 示例：`${app.抖音.bundleName}`、`${app.douyin.bundleName}`

**判别规则（实现建议）：**

1. 去掉外层 `${` `}` 得到 `body`。  
2. 若 `body` 匹配「首段为已注册 namespace」→ 走 **语义实体** 求值。  
3. 否则若首段匹配 `resultId` 形态且 workmemory 命中 → 走 **结果引用**。  
4. 否则 → 解析失败（可再尝试会话短句柄 `${rN}` 映射表）。

> 短句柄（可选）：`${r1}` → 映射到 `(resultId, path)` 或语义三元组；仍走同一拦截器。

### 4.2 Pre-call 拦截器（框架层，工具无感知）

**挂载点：** 所有工具 `invoke` / `exec` 之前（唯一入口，保证全覆盖）。

**算法：**

```
function resolveArgs(args, ctx):
  for each leaf string value v in args:
    if v is placeholder ${...}:
      value = evaluate(v, ctx)   # 查 workmemory 或 namespace 表
      if value == FAIL:
        return ShortCircuit(error)  # 禁止透传字面量
      replace v with value
  return args
```

**硬约束：**

- 解析失败 → **短路**，返回明确错误给编排层/模型，**永不**把 `${…}` 原文传给工具。  
- 工具实现零改动；只要走统一调度即可自动覆盖所有带该类参数的工具。

### 4.3 数据面

#### （1）Workmemory（场景 S1/S3）

| 结构 | 说明 |
|------|------|
| `resultDataList` | 全量工具返回（优先查） |
| `dataForTool` | 部分工具已适配视图（次优查） |
| `resultId ↔ toolCallId` | 对模短 ID ↔ 对内调用 ID |

- 工具成功返回 → **默认写入** workmemory。  
- `resultId` 推荐：`hex8(Hash(toolCallId))`，由 DM **唯一生成**（避免各系统 `UUID[:8]` 不一致）。

#### （2）语义词典（场景 S2/S5）——两张表

**表 T1：同义词 / 别名归一**

| alias（小写规范化） | canonical_entity |
|---------------------|------------------|
| douyin | 抖音 |
| 抖音 | 抖音 |
| tiktok（若需区分包则勿合并） | … |

**表 T2：实体属性映射**

| namespace | entity | attribute | value |
|-----------|--------|-----------|-------|
| app | 抖音 | bundleName | com.ss.android.ugc.aweme |
| app | 微信 | bundleName | com.tencent.mm |

**求值顺序：**

1. 解析出 `namespace, entityRaw, attribute`  
2. `entity = T1.normalize(entityRaw)`  
3. `value = T2.lookup(namespace, entity, attribute)`  
4. 0 条 → FAIL；1 条 → 成功；多条 → FAIL（歧义，附候选列表）

**表数据来源（可组合）：**

- 预置热门应用映射；  
- 设备侧 `getAllInstalledApps` 结果异步/懒加载刷新 T2；  
- 用户纠正写回（可选）。

### 4.4 送模前 Mask（可选，增强 S1）

| 策略 | 说明 |
|------|------|
| 通用默认 | `fileUri` / `fileId` / `objectId` / `*Url` 等指针字段默认 mask 为占位符 |
| 工具覆盖 | 单工具增删 mask 字段；**工具配置 > 通用默认** |
| 形态 | 所见即所填：`${resultId.path}` 或 `${rN}` |

语义实体场景通常**不需要**先把真包名给模型；直接约定填 `${app.x.bundleName}` 即可。

### 4.5 Skill / 提示词约定（软约束）

对模型只保留短规则，例如：

- `bundleName`（及同类 ID 参数）：填 `${app.<应用名>.bundleName}`，**禁止**凭记忆编造包名。  
- 来自上一工具的字段：填 `${resultId.path}` 或照抄上下文中已有 `${…}`。  
- 用户原话/可独立确定的短字面量（相册名、数量等）仍可直接填。

约束优先级建议：**拦截器求值（硬） > Schema/enum（硬） > Skill > SystemPrompt（软）**。

### 4.6 兜底路径（保证可恢复）

```
业务工具调用（含 ${app.抖音.bundleName}）
        │
        ├─ 求值成功 → 1 Loop 完成
        │
        └─ 求值失败（未收录 / 歧义）
                │
                ▼
         触发查询工具（如 getAllInstalledApps）
                │
                ▼
         结果回模型 +（可选）刷新 T1/T2
                │
                ▼
         模型纠正后重试业务工具
```

要点：兜底才引入第 2 Loop；**热路径仍是 1 Loop**。查询结果也可写入 workmemory，后续改走结果引用。

---

## 5. 解析规则（实现细则）

### 5.1 占位符识别

建议正则（整值匹配）：

```text
^\$\{([^{}]+)\}$
```

参数值必须**整个**等于占位符，不允许 `"前缀${…}后缀"`（一期）；需要拼接的场景二期再定。

### 5.2 语义三段切分

对 `body`：按 `.` 切分；

- 段数 == 3 且首段 ∈ 注册 namespace → 语义引用；  
- `entity` 段允许含少量非常规字符时，可采用「首段 namespace + 末段 attribute + 中间全部为 entity」的切法，避免应用名内点号问题（若 entity 禁止 `.` 则可简单 `split('.', 3)`）。

**建议约束：** `entity` 不允许包含 `.`；应用名用中文名或无点别名。

### 5.3 结果引用切分

- `resultId = body` 在第一个 `.` 之前；  
- `jsonpath =` 第一个 `.` 之后全部。  
- 查找：`resultDataList` → `dataForTool`。

### 5.4 失败错误码（建议）

| code | 含义 | 给模型的提示方向 |
|------|------|------------------|
| `REF_SYNTAX` | 语法非法 | 检查 `${…}` 格式 |
| `REF_NOT_FOUND` | 无映射 / 无结果 | 换用查询工具或改 entity |
| `REF_AMBIGUOUS` | 多候选 | 在候选中选一个再填 |
| `REF_ATTR_UNKNOWN` | 属性不支持 | 使用支持的 attribute 列表 |

---

## 6. 开发接入指南

### 6.1 模块划分

| 模块 | 职责 |
|------|------|
| `RefInterceptor` | 扫描参数、调度求值、短路 |
| `ResultRefResolver` | workmemory 结果引用 |
| `SemanticRefResolver` | namespace 三段式 + T1/T2 |
| `MaskPipeline` | 送模前字段掩码（可选） |
| `DictStore` | T1/T2 读写与刷新 |
| `WorkmemoryStore` | 结果入库与按 resultId 查询 |

### 6.2 接入步骤（最小闭环）

1. **调度层**所有工具调用前插入 `RefInterceptor`。  
2. 实现 `ResultRefResolver`（先支持简单字段 path）。  
3. 注册 namespace `app`，实现 T1/T2 + `SemanticRefResolver`。  
4. Skill/系统提示增加 bundleName 等参数的引用约定与示例。  
5. 配置兜底：`REF_NOT_FOUND` / `REF_AMBIGUOUS` → 允许/建议调用 `getAllInstalledApps`。  
6. （可选）通用 mask 名单 + 工具级覆盖。  
7. （可选）动态 enum：把可引用项写入下一工具参数 schema。

### 6.3 工具零改动证明

- 工具仍声明 `bundleName: string`；  
- 模型传入 `"${app.抖音.bundleName}"`；  
- 拦截器替换为 `"com.ss.android.ugc.aweme"` 后进入工具；  
- 工具无分支、无新参数、无 SDK 改造。

### 6.4 示例

**语义引用（1 Loop）：**

```json
{
  "tool": "forbidPermission",
  "args": {
    "bundleName": "${app.抖音.bundleName}",
    "permission": "麦克风"
  }
}
```

拦截后：

```json
{
  "bundleName": "com.ss.android.ugc.aweme",
  "permission": "麦克风"
}
```

**结果引用：**

```json
{
  "tool": "analyze",
  "args": {
    "fileUri": "${a1b2c3d4.fileUri}"
  }
}
```

**别名：**

```text
${app.douyin.bundleName}  --T1-->  entity=抖音  --T2-->  com.ss.android.ugc.aweme
```

### 6.5 配置示例（示意）

```yaml
ref:
  namespaces:
    app:
      attributes: [bundleName]
      synonymTable: app_synonyms
      mappingTable: app_mappings
  resultRef:
    lookupOrder: [resultDataList, dataForTool]
    resultId: { type: hex8, from: toolCallIdHash }
  mask:
    defaults: [fileUri, fileId, objectId, "*Url"]
    toolOverrides: {}
  onError: short_circuit   # never pass through
```

### 6.6 测试清单

- [ ] 语义命中：中文名 / 英文别名均能归一并映射  
- [ ] 未收录：短路 + 错误码，工具未被调用  
- [ ] 歧义：多 bundle 短路并返回候选  
- [ ] 结果引用：resultDataList 优先，dataForTool 回退  
- [ ] 非法语法 / 半截占位符：拒绝  
- [ ] 透传防护：拦截器关闭时的负向用例（发布门禁应失败）  
- [ ] 兜底：失败 → 查询已安装 → 刷新字典 → 重试成功  
- [ ] 回归：无 `${}` 的字面量参数行为不变  

---

## 7. 与 Prompt / Skill 的分工

| 层级 | 做什么 | 不做什么 |
|------|--------|----------|
| Interceptor | 求值、短路、全工具覆盖 | 不教模型业务 |
| Dict / Workmemory | 真值唯一来源 | 不依赖模型记忆 |
| Skill | 标明「此参用引用」+ 示例 | 不写长篇多规则 |
| SystemPrompt | 一条总约定：禁编造 ID，用 `${…}` | 不描述查找顺序等实现细节 |

**SystemPrompt 最小版（可拼装）：**

```text
# 工具参数引用
- 需要真实包名、文件 URI 等标识时：填 ${…} 占位符，禁止凭记忆编造。
- 应用包名：${app.<应用名>.bundleName}（如 ${app.抖音.bundleName}）。
- 上一工具结果字段：${<resultId>.<字段>}，或原样复制上下文中已有的 ${…}。
- 占位符必须是整个参数值；系统会在执行前替换为真实值。
- 用户原话或可独立确定的短信息仍可填字面值。
```

---

## 8. 演进路线

| 阶段 | 交付 |
|------|------|
| P0 | Pre-call 拦截器 + 结果引用（简单 path）+ 短路 |
| P1 | `app` 命名空间 + T1/T2 + bundleName Skill 约定 + 查询兜底 |
| P2 | 通用 mask + resultId 确定性生成统一 |
| P3 | 动态 enum、短句柄 `${rN}`、更多 namespace（contact/device…） |
| P4 | 字典自动从设备应用列表同步、用户纠正学习 |

---

## 9. 总结

| 场景 | 模型填写 | 真值来源 | 正常 Loop | 工具改动 |
|------|----------|----------|-----------|----------|
| 跨工具 fileUri 等 | `${resultId.path}` | workmemory | 无额外为抄写而查 | 无 |
| 应用 bundleName 等 | `${app.名.bundleName}` | 同义词+映射表 | **1**（失败才 2） | 无 |
| 可见仍引用 | `${resultId.path}` | workmemory | 同左 | 无 |
| 列表→对象结构转换 | `${resultId.list}` + policy transform | workmemory + 参数策略 | 模型一次写引用 | 无 |

**结构性保证：** 只要拦截器在统一调度入口生效，真实标识符只能来自查表/记忆；模型不再是真值权威，只负责表达「哪个实体 / 哪条结果的哪个字段」。

---

## 10. 相关文档

- 一页纸：`docs/workmemory-ref-onepager.html`  
- 方案笔记：`docs/workmemory-ref-scheme.md`（若有）  
- 专利草案：`docs/workmemory-ref-patent-draft.md`（建议同步补充语义实体引用实施例）
