# 会话媒体目录：多图融合如何稳定拿到前置 Skill 图片

> 状态：设计建议（可直接对齐现有 workmemory / `${resultId}` 管道）  
> 关联：`tool-param-ref-mechanism.md`、`workmemory-ref-scheme.md`、拼图示例 `tool-param-ref-example.html`

---

## 1. 结论先说

**不要指望「模型上下文里碰巧有图」。**

多图融合（拼图 / 修图 / 风格融合）的入参，必须来自 **Runtime 侧的会话媒体目录（Session Media Catalog）**，通过已有的 `${…}` 引用在 Pre-call 展开；模型只表达「选哪几张 / 什么意图」，**永不**负责搬运 URI、OBS Key、图库 ID。

你们已有「结果进 workmemory → mask → 模型回引用 → Runtime 还原」的管道。缺口是：

| 缺口 | 表现 |
|------|------|
| 入口不统一 | 上传 / 图库搜 / 文生图 / 网搜，返回形态各异 |
| 投递层 ≠ 记忆层 | 流式 Markdown 里嵌了图，但没进 workmemory |
| 可见窗口 ≠ 全集 | 前 30 张进多模态上下文；「最后两张」可能落在窗口外 |
| 序数消歧无锚点 | 「最后两张 / 第二张 / 刘若英那张」缺少稳定索引 |

补上 **会话媒体目录 + 统一入册契约**，融合 Skill 即可稳定消费任意前置结果。

---

## 2. 四类来源为什么会丢图

```text
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ 手动上传 OBS     │  │ 图库搜索         │  │ 文生图（异步）    │  │ 在线搜图         │
│ 客户端直传       │  │ gallery.search  │  │ tool → markdown │  │ web.search      │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                    │                    │
         ▼                    ▼                    ▼                    ▼
   OBS uri / objectKey   gallery id[] + uri   网络 uri（嵌回复）    网页图 url[]
         │                    │                    │                    │
         └──────────┬─────────┴──────────┬─────────┴──────────┬─────────┘
                    │                    │                    │
                    ▼                    ▼                    ▼
           有的进 tool result      有的只进 UI/TTS      有的进多模态前 30
                    │                    │                    │
                    └────────────────────┴────────────────────┘
                                      ▼
                         模型上下文：残缺、异构、不可引用
                                      ▼
                         融合工具：拿不到 / 抄错 / 指错
```

典型失败：

1. **「把最后两张融合」**：搜到 80 张，只有前 30 进模型；「最后两张」在目录里存在，在上下文里不存在。  
2. **「把刚才生成的漫画狗和上传的自拍融合」**：文生图 URI 只在流式 Markdown，上传在 OBS；两边都没变成可引用 handle。  
3. **「把刘若英剧照和昨天那张融合」**：网搜 url 与图库 id 类型不同，融合工具只认一种。

根因同一句：**媒体生命周期挂在「展示通道」上，而不是挂在「可引用资产」上。**

---

## 3. 目标架构：Session Media Catalog

在现有 workmemory 之上（或作为其特化视图），维护本会话的 **有序媒体目录**：

```text
User / Skill / Tool / 上传通道
        │
        ▼
  Media Ingest（统一入册）
        │
        ▼
  Session Media Catalog  ←── 真值：uri / id / bytes 指针
        │
        ├─→ 送模投影：摘要 + 可选缩略图（≤N，如 30）+ 稳定 mediaId
        ├─→ UI/TTS：summary、封面、Markdown（展示用副本）
        └─→ 融合工具入参：${media.xxx} / ${resultId.items} → Pre-call 展开
```

### 3.1 统一媒体条目（MediaItem）

无论来源，入册后都长成同构对象：

```json
{
  "mediaId": "m7f3a91c",
  "source": "gallery | upload | t2i | web | collage | edit",
  "kind": "image",
  "locator": {
    "type": "gallery_id | obs_uri | http_url | cloud_object",
    "value": "…"
  },
  "access": {
    "signedUrl": "…",
    "expiresAt": 0,
    "fetchHint": "device | cloud | http"
  },
  "meta": {
    "width": 0,
    "height": 0,
    "mime": "image/jpeg",
    "capturedAt": "…",
    "title": "…",
    "caption": "…"
  },
  "provenance": {
    "resultId": "a1b2c3d4",
    "toolName": "gallery.search",
    "turnIndex": 12,
    "ordinalInBatch": 79
  },
  "sessionOrdinal": 79
}
```

要点：

- **`mediaId`**：会话内稳定短 ID；送模、指代、入参一律用它（或 `${m7f3a91c}`）。  
- **`locator`**：融合 Tool 真正拉像素时用；默认 **mask**，不进模型。  
- **`sessionOrdinal`**：本会话「第几张图」的全局序（跨来源累计），支撑「最后两张 / 第 3 张」。  
- **`provenance`**：回溯到哪次 tool result，便于 `${a1b2c3d4.items[-2:]}` 类路径。

### 3.2 批次结果仍进 workmemory

单次 Skill/Tool 返回继续写 `resultDataList`，并额外挂目录索引：

```json
{
  "summary": "找到 80 张昨天拍的照片",
  "total": 80,
  "items": "${masked}",
  "mediaBatchId": "b9e2…",
  "mediaIds": ["m…", "m…", "…"],
  "sessionOrdinalRange": [0, 79]
}
```

模型可见：`summary`、`total`、`mediaIds`（或 mask 后的 `${resultId.mediaIds}`）、序数范围。  
模型不可见：长 URI、大 ID 列表真值（按现有 mask policy）。

---

## 4. 各入口如何「必须入册」

### 4.1 手动上传 OBS

| 步骤 | 谁做 | 要求 |
|------|------|------|
| 客户端上传完成 | App / DM | 发 `media.uploaded` 事件（或伪 tool result） |
| Ingest | Runtime | 写入 Catalog + 一条 workmemory 结果 |
| 送模 | Runtime | 摘要「用户上传了 1 张图」+ `${mediaId}`；像素按策略是否进多模态 |

**禁止**：只更新 UI 缩略图、不写 Catalog。上传与搜图在目录里地位相同。

### 4.2 图库搜索（含 >30 / 全量）

| 步骤 | 要求 |
|------|------|
| Tool 返回 | 全量（或本页）id/uri **整包进** `resultDataList` |
| Ingest | 逐条入 Catalog，分配连续 `sessionOrdinal` |
| 送模投影 | 最多 N 张（如 30）缩略图/描述；**全集索引**仍可用引用表达 |
| 全量场景 | 优先 Skill 内 `fetch_all` 收成一个 `mediaIds`，避免 r1…r40 碎片 |

「最后两张」解析：

```text
用户：把最后两张做融合修图
模型：fuse(images=${media.session[-2:]})   // 或显式 mediaId
Runtime：对 Catalog 按 sessionOrdinal 取尾 2 条 → 展开 locator → 调融合 Tool
```

**与多模态窗口解耦**：窗口外的图仍然可被引用选中。

### 4.3 文生图（异步 + 流式 Markdown）

这是最容易丢的一类。约束：

```text
文生图 Tool 完成
   ├─ ① 业务结果写入 workmemory（含最终 imageUri）     ← 记忆层（必须）
   ├─ ② Media Ingest → Catalog                         ← 记忆层（必须）
   └─ ③ 流式 Markdown 嵌入 ![](展示用 url)              ← 投递层（可选副本）
```

规则：

1. **Markdown 里的 URL 不是权威来源**；权威来源是 Catalog / workmemory。  
2. 若产品只能从回复通道吐图：投递层解析 `![](url)` 时 **同步 Ingest**（或 Runtime 在拼回复前已入册）。  
3. 异步任务完成回调必须走与同步 Tool 相同的「写 result → mask → ingest」路径，禁止只 push 一条 UI 卡片。

### 4.4 在线搜索（剧照等）

与图库同构：每张图入 Catalog，`source=web`，`locator.type=http_url`。  
融合 Tool 的 beforeHook 负责把 `http_url` / `gallery_id` / `obs_uri` **适配**成工具协议（下载中转、转存 OBS、或传远端可拉取地址），模型无感知。

---

## 5. 融合 Skill 怎么取图（对齐现有 `${}` 管道）

沿用 `tool-param-ref-mechanism.md` 的 Pre-call + beforeHook，扩展 **媒体引用命名空间**：

| 引用 | 含义 |
|------|------|
| `${<resultId>.mediaIds}` | 某次工具返回的整批 |
| `${<resultId>.mediaIds[-2:]}` | 该批最后两张（路径能力可二期） |
| `${media.session[-2:]}` | 会话目录最后两张（跨来源） |
| `${media.m7f3a91c}` | 单张 |
| `${media.upload.last}` | 最近一次上传批次 |
| `${media.t2i.last}` | 最近一次文生图 |
| `${r3}` 短句柄 | 映射到某批 `mediaIds` |

模型侧示例（融合修图）：

```json
{
  "tool": "image.fuseEdit",
  "args": {
    "images": "${media.session[-2:]}",
    "instruction": "融合修图，漫画风"
  }
}
```

或跨来源显式组合：

```json
{
  "images": ["${media.t2i.last}", "${media.upload.last[0]}"]
}
```

Pre-call：

```text
① resolve ${…} → MediaItem[]（含 locator）
② beforeHook：统一成工具入参
   例 JSONata: $map($, function($v) {{ "uri": $v.access.signedUrl, "id": $v.mediaId }})
③ 签名过期则刷新 signedUrl（目录内更新，模型无感）
④ invoke fuseEdit
⑤ 输出新图再次 Ingest（source=edit），可继续被下一轮引用
```

与现有拼图链一致：`search → createCollage` 只是 Catalog 的一个特例；融合修图是同一管道上的新消费者。

---

## 6. 「看」与「传」分离（含 30 张窗口）

| 通道 | 内容 | 用途 |
|------|------|------|
| **Vision 窗口（≤30）** | 缩略图 / 选中子集像素 | 让模型理解内容、挑图 |
| **文本索引** | `sessionOrdinal`、caption、`mediaId`、summary | 指代与排序 |
| **引用传参** | `${media…}` / `${resultId…}` | 融合 / 发布 / 再编辑 |
| **UI Markdown** | 展示用 url | 用户看见，不作为唯一真相 |

策略建议：

1. 默认：大结果只投递 summary + 前 N 张缩略图进多模态；**全量只在 Catalog**。  
2. 用户说「最后两张 / 第 35 张」：模型出引用；Runtime 从 Catalog 取，必要时 **按需把这 2 张补进下一轮 vision**（可选），但融合调用不必等模型「看见」。  
3. 若融合 Tool 本身是视觉模型：像素由 Tool 侧按 locator 拉取，**不经过对话模型上下文**。

---

## 7. 落地清单（按优先级）

### P0 — 没有就不保证融合

1. **Media Ingest 统一入口**：所有产图通道（Tool 成功、上传事件、异步文生图回调、Markdown 吐图）必须调用。  
2. **Session Media Catalog** 挂在 Runtime / workmemory，会话级有序。  
3. **融合工具只收引用**：fail-closed，禁止模型粘贴长 URL。  
4. **文生图 / 流式回复双写**：workmemory + Catalog 与 Markdown 同步。

### P1 — 指代体验

5. 媒体命名空间：`media.session` / `media.<source>.last` / `media.<mediaId>`。  
6. beforeHook：异构 locator → 融合协议。  
7. 图库全量 `fetch_all` 收成单 batch，避免分页碎片。  
8. 签名 URL 刷新挂在 resolve 阶段。

### P2 — 边界

9. SubAgent / 快慢系统：出边界带 `mediaBatch` 摘要或 `referenceBundle`，与 issue-2520 对齐。  
10. 跨端：Catalog 可序列进 `Message.extendData`（只存 locator + meta，不存像素）。

---

## 8. 验收场景（必须过）

| # | 用户话术 | 期望 |
|---|----------|------|
| 1 | 搜昨天照片（>30）→「最后两张融合」 | Catalog 尾 2 条入融合；不依赖 vision 窗口 |
| 2 | 上传自拍 → 文生漫画狗 →「两张融合」 | upload + t2i 两条均在 Catalog，引用可组合 |
| 3 | 搜「刘若英剧照」→「和刚才生成的狗融合」 | web + t2i 异构 locator，beforeHook 适配成功 |
| 4 | 仅流式 Markdown 出图、未入册 | **失败可观测**；禁止静默用 Markdown url 凑合（或自动 Ingest 后成功） |
| 5 | 融合结果再「加点亮度」 | 新 `source=edit` 入册，可继续被引用 |

---

## 9. 和现有设计的关系

| 已有能力 | 本方案用法 |
|----------|------------|
| workmemory `resultDataList` | 继续存工具全量 JSON；Catalog 是媒体特化索引 |
| mask + `${resultId.path}` | 保留；媒体字段默认 mask |
| beforeHook / JSONata | 融合入参适配的主战场 |
| createCollage 示例 | 证明「列表引用 → 变换 → 多图工具」已通；融合是同构扩展 |
| Skill→Skill 暂无 | 不依赖 Skill 互调；靠 Runtime 目录 + 模型引用即可跨 Skill 传图 |

**一句话**：把「前置 Skill 的结果图」从「碰巧出现在上下文/Markdown 里的副作用」提升为「会话内一等公民媒体资产」；融合只消费 Catalog 引用，来源差异收敛在 Ingest 与 beforeHook。
