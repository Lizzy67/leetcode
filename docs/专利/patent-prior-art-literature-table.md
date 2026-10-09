# 现有技术文献信息（交底书表格）

检索日：2026-08-27。公开日期以专利公布日或论文首次公开日为准。段落号以 Google Patents / 出版文本可见标题、步骤号、图号为准（正式递交请用官方 PDF 核对段号）。

每条文献占两行四格，对应交底书栏目：

| 国别以及代码给出的文献号（对于专利）或期刊或标准名称（包括卷号或版本号） | 公开日期 |
| 文档来源 | 相关的段落和/或图号和/或页数和/或章节数 |

---

## 专利

| 国别以及代码给出的文献号（对于专利）或期刊或标准名称（包括卷号或版本号） | 公开日期 |
| --- | --- |
| 文档来源 | 相关的段落和/或图号和/或页数和/或章节数 |
| US20260111680A1 | 2026-04-23 |
| Google Patents（美国专利申请公开；同族 WO2026085601A1） | 摘要；说明书关于将函数响应绕过大模型、在会话历史中写入 response placeholder（含 lookup / URI / 索引）及 response summary 的实施例；图3、图4（信令步骤416、420）、图5 |
| CN121501258A | 2026-02-10 |
| Google Patents（中国发明专利申请公布） | 摘要；说明书步骤 S104–S106（全局变量注册、值引用、运行构建阶段的值引用替代）；图1、图3、图4、图5 |
| CN120763321A | 2025-10-10 |
| Google Patents（中国发明专利申请公布） | 摘要；具体实施方式中按意图检索任务模板、以意图信息填充占位符（如｛出发城市｝、｛时间范围｝）并生成提示信息、补充工具调用参数模板、工具结果写回运行时上下文的段落；图2、图3 |
| CN121331278A | 2026-01-13 |
| Google Patents（中国发明专利申请公布） | 摘要；说明书步骤 S102 及参数化记忆池（PMP）键值选取、指令参数映射为目标键值并生成工具调用格式的段落；图1、图2、图3 |
| CN121680804A | 2026-03-17 |
| Google Patents（中国发明专利申请公布） | 摘要；权利要求及说明书步骤 S10、S11（语义占位符库、三元逻辑映射表、运行时延迟绑定、语义占位符动态解析与结果替换）；图1、图2 |
| CN112262371A | 2021-01-22 |
| Google Patents（中国发明专利申请公布；授权公告 CN112262371B，2024-11-22） | 摘要；说明书关于地址模板含输入变量、据模板生成含参数的地址并调用代理功能的段落；图1、图2、图4 |

---

## 期刊 / 预印本

| 国别以及代码给出的文献号（对于专利）或期刊或标准名称（包括卷号或版本号） | 公开日期 |
| --- | --- |
| 文档来源 | 相关的段落和/或图号和/或页数和/或章节数 |
| arXiv:2305.18323，Xu 等，*ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models*，v1 | 2023-05-23 |
| arXiv.org | 第3节方法（Planner 以 #E1、#E2 等证据占位符存储 Worker 工具结果，后续步骤引用占位符）；附录 Planner 提示词及示例计划；图1（框架总图） |
| *Proceedings of the 41st International Conference on Machine Learning*（ICML 2024），PMLR 第235卷，第24370–24391页，Kim 等，*An LLM Compiler for Parallel Function Calling*（arXiv:2312.04511 首次公开于 2023-12-07） | 2024-07-21 |
| PMLR / arXiv.org | 第3–4节（Function Calling Planner、Task Fetching Unit、Executor；后续任务参数依赖中间结果）；图2（系统架构） |
| arXiv:2503.18813，Debenedetti 等，*Defeating Prompt Injections by Design*（CaMeL） | 2025-03-24 |
| arXiv.org | 摘要及关于工具调用前由策略引擎检查参数 capability / 信息流的章节；双 LLM 与调用前策略相关示意图 |

---

## 公开技术文档（非专利，可作公知技术举证）

| 国别以及代码给出的文献号（对于专利）或期刊或标准名称（包括卷号或版本号） | 公开日期 |
| --- | --- |
| 文档来源 | 相关的段落和/或图号和/或页数和/或章节数 |
| 腾讯云智能体开发平台《变量说明》 | 检索日页面现行版（请以文档“最近更新日期”填正式表） |
| https://cloud.tencent.com/document/product/1759/122457 | “应用级变量 / 工作流级变量”章节；APP.XXX、WF.XXX 命名及节点输入引用祖先输出的说明 |
| Dify 文档 *Variables and Data Types* / 工作流变量引用 | 检索日页面现行版 |
| https://docs.dify.ai 及公开说明 {{#node_id.output_field#}} | 节点输出变量命名；Prompt 模板中 {{#node_name.field#}} 引用语法 |
| AWS CloudFormation User Guide，*Using dynamic references to specify secrets* | 检索日页面现行版 |
| https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references-secretsmanager.html | `{{resolve:secretsmanager:…}}` 引用模式及部署时解析说明 |
| LangChain 文档 *Tools*（InjectedToolArg / ToolRuntime） | 检索日页面现行版 |
| https://docs.langchain.com/oss/python/langchain/tools | “Injected arguments” / ToolRuntime 注入、该参数不进入送模工具 schema 的说明 |
| Anthropic Claude Code 文档 *Hooks* | 检索日页面现行版 |
| https://code.claude.com/docs/en/hooks.md | PreToolUse 事件：工具执行前拦截、permissionDecision、updatedInput 改写入参 |
