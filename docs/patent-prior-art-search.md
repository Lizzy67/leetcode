# 在先公开 / 现有技术检索备忘

**发明名称（建议）：** 一种面向智能体工具链的参数引用解析机制  
**检索日期：** 2026-08-27  
**检索范围：** Google Patents、公开论文（arXiv）、开源框架文档、云厂商产品文档  
**性质：** 非正式预检索。正式新颖性/创造性结论以智慧芽 + 代理人检索报告为准。

---

## 0. 检索口径（对照本发明保护点）

本发明主张的**组合**，而不是“占位符”或“工作流变量”单点：

1. 大模型在**工具业务入参**中主动输出统一引用（如 `${resultId.path}`），而非编排作者在画布上预置变量。
2. 执行前拦截器查表求值：工作记忆（工具结果）优先，可选叠加语义词典。
3. 解析失败**禁止**将 `${…}` 字面量透传给工具（fail-closed）。
4. 工具无感：不改工具实现与 schema。
5. 送模策略：指针字段可掩码；可见字段仍要求“看了也要引用”（看传分离）。
6. 回填后、调用前可按 Policy 做结构变换。

单点命中“模板替换 / 密钥注入 / 工作流节点引用”**不视为保护点相同**。下文按相近程度排序。

---

## 1. 最接近专利文献（建议代理人精读全文）

### 1.1 US20260111680A1（Shopify）— **最接近专利之一**

| 项 | 内容 |
|----|------|
| 名称 | Methods and systems for managing function calls by a generative language model |
| 公开 | [US20260111680A1](https://patents.google.com/patent/US20260111680A1/en) |
| 优先权 | 2024-10-22（临时申请 63/710,418）；申请 2025-01-07；公开 2026-04-23 |
| 同族 | WO2026085601A1（PCT/CA2025/051315，2025-10-03） |
| 法律状态 | Pending（检索日） |

**公开内容：**  
针对“工具返回值再送回模型容易被改写、且多一次 LLM 调用”的问题：函数执行后，可将**函数响应绕过模型**直接给用户；同时在会话历史中写入 **response placeholder**（通用完成语，或 lookup/URI/索引，用于查表得到更具体描述）或 **response summary**（从函数响应抽取/再生成摘要）。

**相近点：**  
- 工具结果不全量回灌模型，改用占位/摘要。  
- 明确担心模型改写下游所需的结构化结果。  
- 用 lookup / URI 作为会话里的指针。

**区别（建议写入交底）：**

| 本发明 | US20260111680A1 |
|--------|-----------------|
| 模型在**下一轮工具入参**中填写 `${resultId.path}`，由拦截器回填后调用工具 B | 主路径是**绕过模型**把函数结果交给用户/下游，减少二次 prompt |
| 占位符是模型主动发出的**业务引用协议**，且必须在执行前展开 | 占位符主要写入**对话历史**，告诉模型“函数已完成”，不是工具实参协议 |
| 看传分离 + 掩码字段 + 失败不透传 + Policy 结构变换 | 未公开“模型仍要引用不可见指针去调下一工具”的闭环 |
| 工作记忆按 resultId + 字段路径检索 | 查找表用于取“文本描述”，不是 JSON 字段级回填 |

**结论：** 送模侧“摘要/占位代替全文”高度相近，必须在独立权利要求中把**工具入参引用 + 执行前求值回填**写死，避免被该案概括。

---

### 1.2 CN121501258A — 智能体图 + 全局变量值替换

| 项 | 内容 |
|----|------|
| 名称 | 基于全局变量和任意挂接类型的智能体开发系统及方法 |
| 公开 | [CN121501258A](https://patents.google.com/patent/CN121501258A/zh) |
| 申请人 | 北京奇遇信息科技有限公司 |
| 优先权 / 公开 | 优先权约 2026-01-13；公开约 2026-02-10 |
| 法律状态 | 审中 |

**公开内容：**  
构图阶段用全局变量统一注册组件输入/输出；运行构建阶段逐顶点执行，完成**值引用替代**和输出结构变量提取。支持不同类型节点互挂。

**相近点：** 智能体图里的变量注册 + 运行时值替换。

**区别：** 变量由**开发构图**定义，属于编排侧状态机，不是模型在 Function Call 实参中按协议引用“本会话某次工具结果字段”。无送模掩码、无 fail-closed 透传禁令、无语义实体双表。

---

### 1.3 CN120763321A — 任务模板占位符填充

| 项 | 内容 |
|----|------|
| 名称 | 基于大模型的多智能体信息处理方法、装置、电子设备、存储介质及程序产品 |
| 公开 | [CN120763321A](https://patents.google.com/patent/CN120763321A/zh) |
| 申请人 | 口碑（上海）信息技术有限公司 |
| 优先权 | 约 2025-09-11 |
| 法律状态 | 审中 |

**公开内容：**  
按意图从任务模板库取模板；模板含 `{出发城市}` 等占位符；用意图信息填充后生成提示词/任务列表；再按功能描述检索工具、补工具调用参数模板。

**相近点：** 占位符 + 填充 + 再驱动工具。

**区别：** 占位符在**预置任务/提示模板**，由意图解析填槽；不是模型在工具 JSON 实参中输出 `${resultId.path}`。填充发生在“生成给模型的指令”，不是“工具执行前拦截器对实参求值”。

---

### 1.4 CN121331278A — 参数化记忆池（PMP）

| 项 | 内容 |
|----|------|
| 名称 | 基于大模型推理的药物发现任务处理方法、装置及设备 |
| 公开 | [CN121331278A](https://patents.google.com/patent/CN121331278A/zh) |
| 申请人 | 武汉大学 |
| 优先权 | 约 2025-10-13 |
| 领域 | 药物发现 |

**公开内容：**  
PMP 存结构化键值，不存非结构化文本；按指令意图从池中选键，把指令参数映射为工具调用键值，减轻 LLM 负担。

**相近点：** 结构化记忆减轻模型填参负担。

**区别：** 领域专用记忆检索/键选择；模型不在工具实参里发统一引用协议；无跨工具 resultId 字段路径、无掩码/看传分离。不宜作为最接近对比文件，可作“记忆辅助填参”类背景。

---

### 1.5 其他相关但较远的专利

| 文献 | 要点 | 与本发明距离 |
|------|------|----------------|
| [CN121680804A](https://patents.google.com/patent/CN121680804A/zh) | 无代码流程中 `<语义占位符>`，公式引擎词法分析后代入上下文再调 API/SQL | 编排表达式，非 LLM 工具实参协议 |
| [CN112262371B](https://patents.google.com/patent/CN112262371B/zh) | 数字助理用地址模板调用代理功能，模板含输入变量 | 传统数字助理/URI 模板，早于 Agent 工具链 |
| [CN121722461A](https://patents.google.com/patent/CN121722461A/zh) | 调用前按上下文裁剪候选工具集 | 只裁工具列表，不解析入参引用 |
| [CN121278079A](https://patents.google.com/patent/CN121278079A/zh) | LLM 选查询工具并给出参数列表，Agent 再执行 | 标准 function calling，模型直接生成真值参数 |
| [US20260099791A1](https://patents.google.com/patent/US20260099791A1/en) | 生成式 Agent 绑定工作流 API | 管理员绑工具 + LLM 选 API，无引用协议 |

---

## 2. 学术公开（构成在先公开，权重要视同专利）

### 2.1 ReWOO（**最接近论文**）

| 项 | 内容 |
|----|------|
| 文献 | Xu et al., *ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models* |
| 公开 | [arXiv:2305.18323](https://arxiv.org/abs/2305.18323)（2023-05） |
| 代码 | https://github.com/billxbf/ReWOO |
| 产业落地 | NVIDIA NeMo Agent Toolkit 已实现 ReWOO Agent（文档公开 `#E1`/`#E2` 占位替换） |

**公开内容：**  
Planner 一次性写出带证据占位的完整计划（如 `#E1 = Search[…]`，`#E2 = Search[hometown of #E1]`）；Worker 按依赖执行并**把工具输出绑定到占位符**；Solver 再综合。目标是少 token、推理与观察解耦。

**相近点：** 工具结果用符号占位；后续步骤参数依赖前步证据；执行器替换后再调工具。

**区别：**

1. ReWOO 是**一次性规划 DAG**，Planner **看不到**中间观察；本发明是 ReAct 式多轮 Function Calling，模型每轮都可看到（或看到掩码后的）结果并决定下一工具。  
2. 占位符出现在**计划文本**，不是 Function Call JSON 的业务字段。  
3. 无工作记忆 resultId、无送模掩码策略、无“可见也必须引用”、无 Policy 结构变换、无 fail-closed 透传禁令作为系统约束。

### 2.2 LLMCompiler

| 项 | 内容 |
|----|------|
| 文献 | Kim et al., *An LLM Compiler for Parallel Function Calling* |
| 公开 | [arXiv:2312.04511](https://arxiv.org/abs/2312.04511)，ICML 2024 |
| 代码 | https://github.com/SqueezeAILab/LLMCompiler |

**公开内容：** Planner 生成带依赖的任务图；后续任务参数可引用中间结果；Task Fetching Unit 在依赖满足后并行调度。

**区别：** 仍是编译/调度 DAG，优化并行与时延；不是会话工作记忆 + 模型在入参中发 `${resultId.path}` + 掩码/看传分离。

### 2.3 CaMeL / Dual-LLM + 调用前策略

| 项 | 内容 |
|----|------|
| 文献 | Debenedetti et al., *Defeating Prompt Injections by Design*（CaMeL） |
| 公开 | [arXiv:2503.18813](https://arxiv.org/abs/2503.18813)（2025-03） |
| 代码 | https://github.com/google-research/camel-prompt-injection |

**公开内容：** 特权 LLM 规划、隔离 LLM 处理不可信数据；每个值带 capability；**每次工具调用前**策略引擎检查参数来源是否允许。

**相近点：** 工具执行前拦截、按参数做策略。

**区别：** 目标是提示注入与信息流控制，不是引用展开。模型不发业务引用占位符；策略是否决/放行，不是把 `${resultId.path}` 回填为 URI。

### 2.4 PACT（参数级来源监控）

| 项 | 内容 |
|----|------|
| 文献 | *The Granularity Mismatch in Agent Security: Argument-Level Provenance…* |
| 公开 | [arXiv:2605.11039](https://arxiv.org/html/2605.11039v1)（2026） |

**公开内容：** 给工具参数打语义角色（target/command/credential/content），跨步追踪 provenance，调用前检查来源是否满足信任契约。

**区别：** 安全监控，不提供模型侧引用语法，也不做工作记忆字段回填。

---

## 3. 开源 / 产品公开（同样构成在先技术）

### 3.1 工作流节点输出引用（编排作者侧）

| 来源 | 语法 / 机制 | 公开位置 |
|------|-------------|----------|
| Dify | `{{#node_id.output_field#}}`，下游节点引用上游输出 | [Dify 文档 / DeepWiki](https://deepwiki.com/langgenius/dify-docs/4.1-variables-and-data-types) |
| 腾讯云智能体开发平台 | `APP.XXX` / `WF.XXX`，节点输入引用祖先输出；变量赋值节点 | [变量说明](https://cloud.tencent.com/document/product/1759/122457) |
| 华为云智果 AgentArts | 变量赋值：引用上游节点输出或记忆变量 | [变量赋值节点](https://support.huaweicloud.com/usermanual-agentarts0/agentarts_05_0084.html) |
| 蓝鲸标准运维 | `${KEY}` 全局变量，执行时替换 | [variables_engine.md](https://github.com/TencentBlueKing/bk-sops/blob/release_humming_bird/docs/features/variables_engine.md) |
| n8n | `{{ $('Node').item.json.field }}`；工具参数 `$fromAI()` 由模型填，或工作流表达式对模型不可见 | [n8n tools](https://github.com/n8n-io/skills/blob/main/skills/n8n-agents-official/references/TOOLS.md) |
| Amazon Bedrock Agents | 提示模板占位 `$knowledge_base_routing$` 等，由平台配置填充 | [prompt-placeholders](https://docs.aws.amazon.com/zh_cn/bedrock/latest/userguide/prompt-placeholders.html) |

**统一区别：** 引用由**工作流作者/画布**绑定，引擎在节点执行时替换。模型在 Function Call 里通常仍输出**真值**（n8n `$fromAI` 正是让模型填真值）。本发明把引用协议交给**模型在工具实参中书写**，数据源是会话工具结果记忆。

### 3.2 运行时注入、模型不可见参数

| 来源 | 机制 |
|------|------|
| LangChain `InjectedToolArg` / `ToolRuntime` | 参数不进工具 schema，执行时注入 state/config/tool_call_id。[文档](https://docs.langchain.com/oss/python/langchain/tools) |
| Semantic Kernel | 保留名 `kernel`/`service`/`arguments` 自动注入；`IFunctionInvocationFilter` 可改参数 |
| n8n | 非 `$fromAI` 的工具参数由工作流填，**对模型不可见** |
| AWS CloudFormation | `{{resolve:secretsmanager:…}}` 部署时解析密钥，真值尽量不进模板 |

**统一区别：** 解决的是**系统上下文 / 密钥**，模型根本看不到、也不填写该参数位。本发明针对**业务参数**：模型必须填该字段，但填的是引用意图。

### 3.3 调用前 Hook（拦截位置相近）

| 来源 | 机制 |
|------|------|
| Claude Code `PreToolUse` | 工具执行前拦截，可 deny，或 `updatedInput` 改写参数。[官方 hooks](https://code.claude.com/docs/en/hooks.md) |
| Janus | PreToolUse 按 JSON Schema 策略放行/拒绝参数 |
| CrewAI / Docker 等 Agent hook | 同类 pre-tool 中间件（产品文档公开） |

**区别：** Hook 是**通用拦截面**，公开用途是权限、审计、改写危险命令。未公开“扫描 `${resultId.path}` → 工作记忆回填 → 失败短路”的协议。权利要求应把拦截器与**引用语法 + 双源查找 + fail-closed**绑在一起，避免被“任意 PreToolUse”破坏。

### 3.4 工具结果脱敏后再还原（机制形态很近）

| 来源 | 机制 |
|------|------|
| [closemask DESIGN](https://github.com/huilangsh/closemask/blob/main/docs-en/DESIGN.md) | 工具参数里的占位还原 → 执行 → 结果再脱敏回模型；支持 `${…}` 遗留语法 |
| [pi-data-masking](https://github.com/sevten/pi-data-masking/) | LLM 只见格式保持的假值；调用前 unmask；结果回模前再 mask |
| [toolmask-llm](https://pypi.org/project/toolmask-llm/) | 工具输出边界做 PII 掩码 + RBAC |
| [pii-proxy](https://github.com/daslabhq/pii-proxy) | 双向 mask/unmask 双射表 |

**相近点：** “模型侧假值/占位 ↔ 执行侧真值”的往返，与送模掩码 + 执行前回填**同构**。

**区别（必须写清）：**

1. 现有方案多是 **PII/凭证检测 + 代用值**，占位由检测器生成，不是会话 `resultId` + JSON 路径协议。  
2. 模型往往被鼓励把**看起来像真值的 surrogate** 抄回参数，再 unmask；本发明要求模型输出**显式引用语法**，禁止把未展开引用当字面量。  
3. 本发明还有“字段可见仍必须引用”（防抄错长 URI），不是单纯隐私脱敏。  
4. 开源库公开日需代理人核对 Git 首次提交 / PyPI 发布日，评估是否早于申请日。

---

## 4. 现有技术图谱（写交底用）

```
                    ┌─ 提示/任务模板填槽 ──────── CN120763321A, LangChain PromptTemplate, Bedrock placeholders
                    │
  占位符替换 ───────┼─ 工作流节点变量 ────────── Dify, 腾讯云 ADP, 华为 AgentArts, 蓝鲸, n8n 表达式
                    │
                    ├─ 规划 DAG 证据占位 ─────── ReWOO #E1, LLMCompiler
                    │
                    ├─ 密钥/系统参数注入 ─────── AWS {{resolve}}, InjectedToolArg, n8n 对模型隐藏的字段
                    │
                    ├─ 工具结果摘要/绕过模型 ─── US20260111680A1 (Shopify)
                    │
                    └─ PII 掩码往返 ──────────── closemask, pi-data-masking, toolmask
                                                  │
                                                  ▼
                         本发明组合落在空白处：
                         模型在工具业务入参写引用协议
                         + 工作记忆字段级回填
                         + 执行前拦截 / fail-closed
                         + 看传分离（可见也引用 / 掩码指针）
                         + 可选 Policy 结构变换
                         + 工具零改动
```

---

## 5. 建议的区别技术特征（写入独立权利要求时优先保留）

避免只写“占位符替换”或“调用前拦截”。建议独立项至少同时包含：

1. **模型在工具调用参数中输出引用占位符**（参数值为引用态，而非业务真值）；  
2. **引用标识指向本会话工具结果**，并含字段路径；  
3. **工具执行前**由框架解析并回填，工具本身不解析引用；  
4. **解析失败则中止调用且不向工具传递未展开字面量**；  
5.（从属项）送模时对指定字段掩码，模型仍用同一引用形态回填；  
6.（从属项）回填后按策略做结构变换再调用。

语义实体 / 同义词表 / 包名映射建议放**另一独立项或从属项**（用户已将该能力拆到另一页方案），避免与结果引用抢独立项篇幅。

---

## 6. 检索式备查（供智慧芽正式检索）

**中文：**  
`(大模型 OR 智能体 OR 语言模型) AND (工具调用 OR 函数调用) AND (占位符 OR 变量引用 OR 参数替换 OR 回填) AND (执行前 OR 拦截 OR 解析)`  
`(工具结果 OR 工作记忆) AND (掩码 OR 脱敏 OR 占位) AND (工具参数)`  
`(全局变量 OR 节点输出) AND 智能体 AND (值替换 OR 引用替代)`

**英文：**  
`(LLM OR "AI agent") AND ("tool call" OR "function calling") AND (placeholder OR "variable reference" OR resolve) AND (interceptor OR "before invocation" OR "pre-tool")`  
`("tool output" OR "function response") AND (mask OR redact OR placeholder) AND (argument OR parameter) AND (restore OR unmask OR resolve)`  
`ReWOO OR LLMCompiler OR "InjectedToolArg" OR "PreToolUse"`

**分类号提示：** G06F9/44、G06F40/35、G06N3/00 附近；智能体编排类近年公开量大，建议语义检索 + 同族扩展 Shopify/口碑/奇遇三案。

---

## 7. 本轮未覆盖 / 需代理人补做

- 中国专利全文库、美国授权文本、EPO/JPO 的**收费库精检**（本次仅 Google Patents 公开网页）。  
- 开源项目 **Git 首次提交日 / 文档归档日**（closemask、pi-data-masking 等可能非常接近）。  
- 公司内部是否已随产品/对外 PPT 公开本方案（IDEA 表“是否已产品发布”仍待发明人确认）。  
- 智慧芽语义检索与同族、引证、法律状态核对。

---

*本备忘仅供交底与 IDEA 内部使用，不构成法律意见。*
