# Docs

按主题 / 功能整理的设计与方案文档。各目录自包含（含脚本、素材与产出物）。

| 目录 | 主题 | 入口 |
|------|------|------|
| [工具参数引用/](工具参数引用/) | 工具参数引用机制（顶层设计与开发接入） | [tool-param-ref-mechanism.md](工具参数引用/tool-param-ref-mechanism.md) |
| [工作记忆引用/](工作记忆引用/) | WorkMemory 工具结果引用方案 | [workmemory-ref-scheme.md](工作记忆引用/workmemory-ref-scheme.md) |
| [专利/](专利/) | 参数引用相关专利 IDEA / 交底书 / 现有技术检索 | [patent-idea-agent-param-ref.md](专利/patent-idea-agent-param-ref.md) |
| [Skill工具治理/](Skill工具治理/) | Skill / Tool 配套与版本治理 | [skill-tool-governance-spec.md](Skill工具治理/skill-tool-governance-spec.md) |
| [对话内HTML预览/](对话内HTML预览/) | 对话内 HTML 渲染与预览 | [agent_html_preview_proposal.md](对话内HTML预览/agent_html_preview_proposal.md) |

## 目录说明

### 工具参数引用/

统一的「参数占位符 + 调用前求值」框架：跨工具传参、语义标识符消歧等。含机制说明、一页纸 HTML、示例与 PPT 生成脚本。

### 工作记忆引用/

工具结果经 Runtime 缓存、掩码与 `${resultId.path}` 引用填参的方案、一页纸、逻辑架构图与跨端对齐简报（issue-2520）。

### 专利/

面向智能体工具链的参数引用解析机制：IDEA 稿、交底书分册、现有技术检索表、架构/场景图与生成脚本。

### Skill工具治理/

Skill 与 Tool 配套关系、版本兼容、放量与上架治理规范及一页纸。

### 对话内HTML预览/

会话内 HTML 预览方案、架构视图预览页，以及 PPT / 配图素材。
