# 业界怎么处理「先搜图，再选一张去修」

> 调研结论，用来对照 `vision-context-search-edit-chain.md`。  
> 日期：2026-11-17。

## 结论

业界把这件事拆成两层，和你们现在的分法一致：

- **给模型看的**：一段说明，外加少量图片。图片用 `file_id`、URL 或小缩略图，不把原图字节反复塞进每一轮。
- **给程序留的**：原图放在会话旁边的文件库里。后面的工具拿短号去取，不从对话原文里抠 URL。

没有一家把「图库 id、沙箱路径、公网 URL、云对象」合成一个叫 visionContext 的账本，再加「第 3 张 / 有太阳的那张」。那一层是产品自己做的。模型厂商只保证「这张图有一个稳定 id，后面还能再交给模型或工具」。

## 各家实际怎么做

### 1. 模型厂商：原图换成 file_id，多轮继续引用

OpenAI 的工具结果可以是图片或文件。图片要么带 URL，要么带已经上传过的 `file_id`。图像生成的多轮修改不靠模型记住像素，靠上一轮的 `previous_response_id`，或那次 `image_generation_call` 的 id。下一句「改得写实一点」时，服务端自己找到上一张图。

Anthropic 同样有 Files API。多轮对话每次都会重发历史；如果历史里是 base64，图片越大越慢。官方建议上传一次，后面的消息和 tool_result 都写 `file_id`。模型能接着问「和前两张像吗」，应用不用把字节再贴一遍。

这对应你们的 `ref`：真正要传的是短号，不是整张图。他们没有「第 35 张」这种序号，因为他们假设需要看的那几张已经在对话里。

来源：

- OpenAI Function calling：工具输出可以是 image / file，用 `file_id`。https://developers.openai.com/API/docs/guides/function-calling
- OpenAI Image generation：多轮用 `previous_response_id` 或 image call id。https://developers.openai.com/api/docs/guides/tools-image-generation
- Anthropic Vision：多轮用 `file_id`，避免每轮重传 base64。https://platform.claude.com/docs/en/build-with-claude/vision
- Anthropic Files API。https://platform.claude.com/docs/en/build-with-claude/files

### 2. Agent 框架：模型看摘要，程序留原件

LangChain 的工具可以返回两份：`content` 进模型，`artifact` 不进模型。文档写明 artifact 是给程序用的，例如大图的 base64、文档 id。Deep Agents 更直接：大图存到文件系统或对象存储，消息里只留路径或 URL。

Google ADK 有独立的 Artifact Service，和会话状态分开。工具里 `save_artifact("chart.png", 图片)`，另一个工具 `load_artifact("chart.png")`。还有内置的 `LoadArtifactsTool`：模型需要看某张图时再加载，加载结果只在这一轮临时出现，不写回永久历史。

这就是你们的 workmemory + visionContext。ADK 用文件名当短号；你们用「哪一次搜索的第几张」（文档举例里的 `m12` 只是会话短号，不是既有字段）。ADK 要工具自己调用 `save_artifact`。你们不改旧工具返回，所以改成「工具策略里写 listPath / refPath，Runtime 代为入账」。新工具则直接按约定字段返回，Runtime 认那个固定字段。

来源：

- LangChain ToolMessage.artifact。https://docs.langchain.com/oss/python/langchain/messages
- Deep Agents 多模态：大图存后端，消息里传路径。https://docs.langchain.com/oss/python/deepagents/multimodal
- Google ADK Artifacts，含 LoadArtifactsTool。https://adk.dev/artifacts/

### 3. MCP：要看的图内联，不看的图给链接

MCP 工具结果里，图片有两种：

- `image`：base64 直接放进结果，给模型马上看。适合一张小图。
- `resource_link`：只给 URI、名字、说明。客户端或下一步真要用时再 `resources/read`。适合很多张、很大、或者只是给用户看。

一篇实践说明写得很直白：十二张缩略图应该回十二个链接，不要回十二段 base64。链接旁边要有一句文字，否则模型不知道这张图值不值得打开。

这对应你们的「前 30 张可以给模型看，48 张的 id 留在账本」。MCP 没有统一的选图工具，打开哪张由客户端或模型再发一次读资源。

来源：

- MCP Tools：image 与 resource_link。https://modelcontextprotocol.io/specification/draft/server/tools
- 何时内联、何时给链接。https://mcporbit.com/blog/return-an-image-from-an-mcp-tool

### 4. 相册产品：先搜，用户点开，再修

Google Photos 的 Ask Photos 用自然语言搜库，复杂问题会在后台继续收窄结果。编辑是另一条路：先打开某一张，再在这张上说「去掉背景的车」。帮助文档写明，Ask Photos 只处理已经备份到云端的照片。端上没上传的图，云侧编辑用不了。

也就是说，消费级产品通常不让模型在 48 张里口头点「第 3 张」或「有太阳的那张」然后直接修。它们把选择交给用户点击，把「图必须在云上」交给备份。你们要的语音连续操作（不点开、直接说第几张）比这条产品路径更进一步，所以才需要 `picked` 和调用前上传。

来源：

- Ask Photos 搜索与编辑。https://support.google.com/photos/answer/15318661
- 对话式编辑先落在当前打开的那张上。https://blog.google/products-and-platforms/products/photos/ai-photo-editing-google-photos/

## 和我们方案的对照

| 我们现在的做法 | 业界对应 | 差别 |
|----------------|----------|------|
| 账本不进模型，只给摘要和少量缩略图 | LangChain artifact、ADK artifact、MCP resource_link | 一致 |
| 短号 `m12`，不让模型抄 URL | OpenAI / Anthropic `file_id` | 一致。他们的短号是文件服务发的，你们的短号是会话里发的 |
| 旧工具不改返回，用 `listPath` / `refPath` 入账 | 新工具更常直接返回标准图片块，或自己调用 `save_artifact` | 配置抽取是为了兼容已经上线的搜索。新工具也可以直接返回标准图片块，Runtime 看见就入账 |
| `vision.select` 在模型没看见的那批里选 | 相册产品用用户点选；框架用「再加载这张」 | 内置选图是语音场景补上的。业界没有一个通用的「四种选法」工具 |
| 云修图前把图库图上传，端剪辑前把公网图下载 | Google Photos 要求先备份；模型 API 只认 file_id / URL | 一致，而且都只搬即将使用的那张，不搬整次搜索结果 |

## 可以借鉴的两点

1. 新工具如果愿意改返回，直接带标准图片引用（短号或 URL），比再写一份 `listPath` 更接近 OpenAI、Claude、MCP。`listPath` 留给改不动的旧工具。
2. 模型要「看」某一张时再加载，看完不写进永久历史。ADK 的 LoadArtifactsTool 就是这样。你们前 30 张投影可以同样处理：超出窗口的图，只有选中之后才补进下一轮，不把 48 张都留在上下文里。
