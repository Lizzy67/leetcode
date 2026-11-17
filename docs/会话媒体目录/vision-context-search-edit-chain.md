# visionContext：搜索选图 → 修图/剪辑完整链路

> 状态：设计建议（承接 `session-media-catalog-for-fusion.md`）  
> 关联：workmemory 引用、工具参数 `${…}` / beforeHook  
> 业务主路径：**搜图 → 指代选图 → AI 修图 / 视频剪辑**；返回地址须可被后续任意多模工具访问

---

## 1. 对你提案的判断

**加 `visionContext` 作为 Runtime 会话媒体目录：正确，建议定为一等结构。**

`userUploadImg`、`lastToolReturnImg` 作为**快捷视图**有用，但**不够**单独撑起主路径：

| 能力 | 仅 lastToolReturnImg | 需要补的 |
|------|----------------------|----------|
| 「第 x 张」 | 能（若 batch 还在） | 跨轮 / 跨工具后 batch 被覆盖会丢 |
| 「有太阳的那张」 | 不能只靠 URI 列表 | 要 vision 投影或选图 Tool 回写 `selection` |
| 「刚才上传的 + 搜索第 3 张」 | 两个槽位可拼 | 需要统一 `items[]` 与跨来源引用 |
| 下游多模可访问 | URI 异构 | 需要 **Resolve / Materialize** 层 |

推荐形态：

```text
visionContext
├── items[]              ← 权威有序目录（所有来源入册）
├── userUploadImg[]      ← 视图：本会话用户上传
├── lastToolReturnImg[]  ← 视图：最近一次产图 Tool 的 batch
├── lastSearchBatch      ← 视图：最近一次搜索（支撑「搜索结果里…」）
├── selection            ← 当前选中（「这张/这些」消歧锚点）
└── accessCache          ← 已物化的可拉取地址（签名 URL / 沙箱副本）
```

模型与 Skill 主要操作 **`items` / `selection` / 引用**；两个快捷数组是给 Prompt 与默认指代用的糖，不是唯一真相。

---

## 2. visionContext 数据结构

### 2.1 单条媒体（统一异构来源）

```json
{
  "mediaId": "m7f3a91c",
  "sessionOrdinal": 12,
  "batchOrdinal": 2,
  "source": "upload | gallery | t2i | web | edit | clip",
  "locator": {
    "type": "gallery_id | sandbox_uri | http_url | obs_id | obs_uri",
    "value": "…"
  },
  "access": {
    "status": "raw | signed | materialized",
    "pullUrl": null,
    "expiresAt": null,
    "localPath": null,
    "reachableBy": ["on_device", "cloud_http", "obs"]
  },
  "meta": {
    "mime": "image/jpeg",
    "width": 4032,
    "height": 3024,
    "capturedAt": "2025-06-01T18:20:00+08:00",
    "caption": null,
    "tags": [],
    "thumbHash": null
  },
  "provenance": {
    "resultId": "a1b2c3d4",
    "toolName": "gallery.search",
    "turnIndex": 5
  }
}
```

**locator 覆盖你点名的来源：**

| locator.type | 含义 | 典型来源 |
|--------------|------|----------|
| `gallery_id` | 本地媒体库 ID | 搜图 / 图库 |
| `sandbox_uri` | App 沙箱文件 URI | 修图中间态、下载缓存 |
| `http_url` | 公网图 | 网搜、文生图 CDN |
| `obs_id` / `obs_uri` | 云对象 | 用户上传、云侧落盘 |

`access` 与 `locator` 分离：locator 是**身份**；access 是**当前谁能拉到像素**。下游工具要的是可访问形态，不一定是原始 locator。

### 2.2 容器字段

```json
{
  "visionContext": {
    "schemaVersion": 1,
    "items": ["/* MediaItem[] 权威列表 */"],
    "userUploadImg": ["m…", "m…"],
    "lastToolReturnImg": {
      "resultId": "a1b2c3d4",
      "toolName": "gallery.search",
      "mediaIds": ["m…", "m…"],
      "summary": "找到 48 张去年拍的照片"
    },
    "lastSearchBatch": {
      "query": "去年拍的照片",
      "mediaIds": ["m…"],
      "total": 48,
      "visionProjected": ["m…前30…"]
    },
    "selection": {
      "mediaIds": ["m7f3a91c"],
      "reason": "user_ordinal | user_semantic | model_pick | explicit",
      "utterance": "有太阳的那张"
    },
    "accessCache": {}
  }
}
```

约定：

1. **所有产图通道必须 `ingest → items`**，再更新快捷视图。  
2. `userUploadImg` / `lastToolReturnImg.mediaIds` 只存 `mediaId`，细节查 `items`。  
3. 新 Tool 返回覆盖 `lastToolReturnImg`，但**不删除**旧 `items`（否则「再修刚才那张」会断）。  
4. 与 workmemory 关系：`resultDataList` 仍存工具全量 JSON；`visionContext` 是媒体特化索引，`provenance.resultId` 反查 workmemory。

---

## 3. 完整业务链路

### 3.1 总览

```text
① 搜索「去年拍的照片」
        │
        ▼
  gallery.search → resultDataList + ingest(visionContext.items)
        │
        ├─ lastToolReturnImg / lastSearchBatch 更新
        ├─ 送模：summary + 前 N 张缩略图（vision 投影）
        └─ 全集 mediaId 可引用（窗口外也可被选）
        │
②a 序数选图「第 3 张」     ②b 语义选图「有太阳的那张」
        │                           │
        ▼                           ▼
  解析 batchOrdinal=3         模型看投影 / 或 vision.select
  → selection = [m…]          → 回写 selection = [m…]
        │                           │
        └─────────────┬─────────────┘
                      ▼
③ 修图 / 剪辑工具
   args.images = ${vision.selection}
        │
        ▼
  Pre-call: resolve mediaId → MediaItem
        │
        ▼
  Access Resolver / Materializer
   （gallery_id → 可拉 URL 或转存 OBS；过期签名刷新）
        │
        ▼
  beforeHook → 工具协议入参 → invoke
        │
        ▼
④ 输出新图再次 ingest（source=edit|clip）
   → 成为下轮任意多模工具的合法输入
```

### 3.2 步骤①：搜索入册

Tool 返回示例（业务 JSON）：

```json
{
  "summary": "找到 48 张去年拍的照片",
  "total": 48,
  "items": [
    { "galleryId": "10081", "thumbUri": "…", "capturedAt": "…" },
    { "galleryId": "10082", "thumbUri": "…" }
  ]
}
```

Runtime Ingest：

1. 每条 → `MediaItem`（`locator.type=gallery_id`）。  
2. 追加进 `items`，分配 `sessionOrdinal`；本批内 `batchOrdinal` 从 0/1 起。  
3. 更新 `lastToolReturnImg`、`lastSearchBatch`。  
4. Mask 长 URI / id 列表；模型见 summary + `${a1b2c3d4.mediaIds}` 或投影列表。  
5. Vision 投影：默认前 30（可配）写入多模态消息；**投影集合记在 `lastSearchBatch.visionProjected`**，便于解释「模型看见了谁」。

### 3.3 步骤②a：序数选图「第 x 张」

解析优先级（Skill / Runtime 约定，勿全丢 Prompt）：

```text
「第 x 张」默认锚点 = lastSearchBatch ?? lastToolReturnImg
  → items 中 batchOrdinal == x（或 x-1，产品统一一种）
  → 写入 selection.mediaIds
```

模型输出（推荐只出引用）：

```json
{
  "tool": "image.edit",
  "args": {
    "images": "${vision.selection}",
    "instruction": "提亮，保留太阳轮廓"
  }
}
```

或显式：

```json
{ "images": "${vision.lastSearch[2]}" }
```

**不要**让模型抄 galleryId。窗口外的第 35 张：只要在 `items` 里，序数引用仍可命中。

### 3.4 步骤②b：语义选图「有太阳的那张」

两条实现路径（可并存）：

| 路径 | 做法 | 适用 |
|------|------|------|
| **A. 对话模型看图** | 投影内缩略图 + caption；模型选出 `mediaId` 写入 selection | 候选已在前 N 张 |
| **B. 选图 Tool** | `vision.select(batch=${lastSearch}, query="有太阳")` 端侧/云侧打分，返回 `mediaIds` 并 ingest selection | 候选多、或不在投影窗 |

路径 B 更稳：选图与修图解耦，且不依赖「太阳那张恰好在前 30」。

选图 Tool 返回也必须进 `visionContext`（更新 `selection`，可选写 `meta.caption`）。

### 3.5 步骤③：修图 / 视频剪辑

统一入参约定（工具零改或最小改）：

```text
模型:  images = ${vision.selection} | ${vision.lastSearch[2]} | ${vision.userUpload[-1]}
         ↓ Pre-call resolve
Runtime: MediaItem[]
         ↓ Access Resolver
       每条得到 tool-facing handle（见 §4）
         ↓ beforeHook（按工具 policy）
       [{ "uri": "https://…" }, …] 或 [{ "file_id": "…" }, …]
         ↓ invoke edit / video.clip
```

视频剪辑同构：时间线素材列表仍是 `mediaId[]`；Resolve 层按工具要图片帧还是视频文件做物化。

### 3.6 步骤④：结果回写，供任意后续多模工具

修图/剪辑成功后：

1. 新产物 `ingest`（`source=edit|clip`，locator 多为 `obs_*` 或 `sandbox_uri`）。  
2. 更新 `lastToolReturnImg`。  
3. **默认把新图加入 `selection`**（「再淡一点」指代不断）。  
4. 同步写 workmemory `resultId`，支持 `${resultId.outputUri}` 与 `${vision.selection}` 等价路径。

这样链路可无限续：搜 → 选 → 修 → 再修 → 丢进剪辑时间线。

---

## 4. 「返回地址可被后续任意多模工具访问」

### 4.1 问题本质

「可访问」≠「永远甩同一个公网 URL 字符串」。

| 原始形态 | 云侧修图工具 | 端侧剪辑工具 |
|----------|--------------|--------------|
| `gallery_id` | 通常不可直达 | 可直达 |
| `sandbox_uri` | 不可达 | 同 App 可达 |
| `http_url` | 可达（防盗链/过期风险） | 需下载 |
| `obs_id` | 需签名 | 需下载或 SDK |

因此 Runtime 必须有 **Access Resolver（解析）+ Materializer（物化）**：

```text
MediaItem
   │
   ├─ 若工具声明 accepts ∋ locator.type 且同侧可达 → 直接传 locator
   ├─ 若需要 http → 签名 / 临时网关 pullUrl（写入 access + accessCache）
   ├─ 若需要云侧持有 → 上传/转存 OBS，更新 locator 或旁路 materialization
   └─ 失败 → fail-closed，提示换端或授权，禁止把不可达 URI 塞给工具
```

### 4.2 工具侧能力声明（建议挂 Capability / Tool schema）

```json
{
  "image.edit": {
    "inputMedia": {
      "accepts": ["http_url", "obs_uri", "obs_id"],
      "maxItems": 6,
      "prefer": "obs_uri"
    }
  },
  "video.clip": {
    "inputMedia": {
      "accepts": ["gallery_id", "sandbox_uri", "obs_uri"],
      "execSide": "on_device"
    }
  }
}
```

Resolve 时按 `accepts` × `MediaItem.access.reachableBy` 做适配；**模型无感**。

### 4.3 稳定性约定

1. **对外引用只用 `mediaId` / `${vision…}`**，不用易过期的 signed URL。  
2. 每次 Pre-call 可刷新 `pullUrl`；`accessCache` 按 `expiresAt` 失效。  
3. 物化副本（转存 OBS）可记 `materializedFrom`，避免重复上传。  
4. 文生图 / Markdown 嵌图：展示 URL 只是副本；权威条目在 `items`，后续工具只走 Resolve。

### 4.4 与 `${}` 管道对齐的引用语法（建议）

| 引用 | 含义 |
|------|------|
| `${vision.selection}` | 当前选中 MediaItem[] |
| `${vision.userUpload}` / `${vision.userUpload[-1]}` | 上传列表 / 最近一张 |
| `${vision.lastToolReturn}` | 最近产图 batch |
| `${vision.lastSearch}` / `${vision.lastSearch[2]}` | 最近搜索 / 第 3 张 |
| `${vision.m7f3a91c}` | 单 mediaId |
| `${a1b2c3d4.mediaIds}` | 兼容纯 workmemory 路径 |

解析失败 fail-closed，与现有参数引用一致。

---

## 5. 和「只加两个数组」的差异（落地时注意）

| 做法 | 风险 |
|------|------|
| 只有 `userUploadImg` + `lastToolReturnImg` | 搜索 batch 被文生图覆盖后，「搜索里第 x 张」丢失 |
| 不设 `selection` | 「这张」「有太阳的那张」无法跨一句工具调用稳定指代 |
| 不设 Access Resolver | gallery_id 丢给云修图 → 运行失败；公网 URL 过期 → 第二次调用挂 |
| 把 vision 投影当目录 | >N 或「最后两张」必挂 |
| Markdown URI 当权威 | 异步文生图链路与多模工具脱节 |

**最小够用集合：** `items` + `lastSearchBatch` + `selection` + Access Resolver；`userUploadImg` / `lastToolReturnImg` 作为视图保留。

---

## 6. 验收话术（主路径）

| # | 话术 | 通过标准 |
|---|------|----------|
| 1 | 「搜索去年拍的照片」 | 48 张入 `items`；`lastSearchBatch` 完整；投影 ≤N |
| 2 | 「选第 3 张去修图」 | `selection` = batch 第 3；云修图收到可访问 URI/OBS，非裸 gallery_id（若工具在云） |
| 3 | 「有太阳的那张」 | 经模型或 `vision.select` 命中正确 `mediaId`；可在投影外靠选图 Tool |
| 4 | 「再和刚上传的自拍融合」 | `userUpload` + `selection` 组合 resolve 成功 |
| 5 | 「把修完的图丢进视频剪辑」 | edit 产物已 ingest；端侧工具拿到可达 locator |
| 6 | 搜索后穿插文生图再问「刚才搜索的第 2 张」 | `lastSearchBatch` 仍在；不被 `lastToolReturnImg` 覆盖毁掉 |

---

## 7. 实施切片建议

**P0**

1. Runtime 挂载 `visionContext.items` + ingest 钩子（上传 / Tool 成功 / 异步回调）。  
2. `lastSearchBatch` + `selection` + `${vision.*}` 解析。  
3. Access Resolver 最小集：`gallery_id→可拉`、`obs→签名`、`http→校验`。  
4. 修图工具走引用 + beforeHook。

**P1**

5. `vision.select` 语义选图。  
6. 物化转存 OBS（云工具 prefer）。  
7. 剪辑工具同构接入。  
8. 投影窗与 Catalog 解耦的指标与日志（命中率、resolve 失败原因）。

**P2**

9. 跨端 `referenceBundle` 携带 media 摘要。  
10. SubAgent 回传 selection / mediaIds。

---

## 8. 一句话

把 `visionContext` 建成 Runtime 的**有序媒体账本**：搜索结果全量入册，用序数/语义写入 `selection`，工具侧只收 `${vision…}`；真正「可被任意多模工具访问」靠 **Resolve/Materialize**，而不是假设所有来源天生是一张永不过期的公网图。
