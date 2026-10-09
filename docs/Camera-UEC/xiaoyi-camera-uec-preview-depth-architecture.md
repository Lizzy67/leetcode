# 小艺 Camera Tab（UEC）预览流 / 深度 / 稳定帧 — 方案对表稿

> 用途：和相机 / HAL / 框架同事对齐架构与接口。  
> 状态：讨论稿（含待拍板争议点）  
> 范围：小艺 Tab 嵌入相机 App；预览流获取（双 Surface）与分发；实时运动 meta；按需深度；拍摄取图。
> 更新：HAL 侧确认显示路 Surface 由 RS 直接消费，应用层无处理机会，预览须配「显示 + 分析」两路 Output（见 2.0）。

---

## 0. 一句话目标

用户在相机 App 的「小艺」Tab 中看到预览，系统用实时运动状态判定稳定帧并触发端侧模型/AR；用户点击拍摄时，拿到对齐的 RGB + 深度（及运动 meta），用于推荐 / 空间建模 / chips 执行。

---

## 1. 角色与职责

| 角色 | 职责 | 不负责 |
|------|------|--------|
| 小艺 Tab（UEC） | 显示（若能力允许）、稳定帧判定、模型/AR/分发/chips、发起拍摄与深度请求 | 直接调 HAL / HDI |
| 相机 App | 握相机会话、配流、启停小艺输出、转发 Capture/深度请求、资源抢占与交还 | 端侧大模型推理细节 |
| Camera Framework | Session/Output 管理，向 HDI 下发配置与 Capture | 业务规则（chips 等） |
| HDI | 框架 ↔ HAL 的硬件接口通道 | 对小艺直接暴露（通常） |
| Camera HAL | 出预览、出 meta、单次深度计算、停流配合 | UI / UEC 生命周期 |

**原则：摄像头会话通常只有一个主人（默认：相机 App）。小艺是流的消费者 + 业务决策者。**

---

## 2. 总体架构图

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ 相机 App 进程（宿主 / 房东）                                                │
│                                                                          │
│   ┌─────────────┐     Start/Stop/Capture/Depth      ┌────────────────┐  │
│   │ 相机业务逻辑  │◄────────────────────────────────►│ 对接小艺的接口层 │  │
│   └──────┬──────┘                                   └────────▲───────┘  │
│          │ Want / sendData / 自定义 Binder 等                  │          │
│          ▼                                                   │          │
│   ┌─────────────────┐                                        │          │
│   │ Camera Framework │                                        │          │
│   └────────┬────────┘                                        │          │
│            │ HDI                                             │          │
│            ▼                                                 │          │
│   ┌─────────────────┐     预览 Buffer / Capture / Depth       │          │
│   │   Camera HAL    │────────────────────────────────────────┘          │
│   │  Sensor / ISP   │   （深度经 HDI 上行；应用不直连 HDI）                 │
│   └────────┬────────┘                                                    │
│            │ 同一帧同时投两路 Output（timestamp 一致）                       │
│            ├─► Surface A（显示路）──► RS 合成上屏（应用层不经手）             │
│            └─► Surface B（分析路）──► 小艺进程消费者（ImageReceiver）        │
└──────────────────────────────────────────────────────────────────────────┘
                    │ surfaceId ×2 / Buffer / fd·handle / metadata
                    │（跨进程）
                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ 小艺 UEC 进程                                                              │
│                                                                          │
│   Surface A → 显示（XComponent 绑定；放宿主还是 UEC：争议 G）                │
│   Surface B → 分析路消费 ──┬──► 感知 / 端侧大模型（降频，稳定帧触发）         │
│                          └──► AR 空间建模（同进程分发；尺寸不同则第三路）     │
│                                                                          │
│   实时 motion meta ──► StableFrameDetector ──► 推理门控                    │
│                                                                          │
│   拍摄按钮 ──► CaptureDepthAt / CaptureStill ──► RGB + Depth + Meta       │
│                      └──► 分发服务 ──► 规则 ──► chips ──► 点击执行         │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.0 为什么必须两个 Surface（HAL 侧结论）

Surface 本质是**生产者 → 消费者的 Buffer 队列，且一个 Surface 只有一个消费者**。

```text
Camera HAL（生产者）──► Surface（BufferQueue）──► 唯一消费者
```

- 若 Surface 绑在 XComponent 上，消费者就是 **RS（Render Service）**：HAL flush 一帧 → RS 立刻 acquire 合成上屏 → release 还给 HAL。整条链路在 HAL 与 RS 之间闭环，**应用层不在队列上**，小艺既截不到 Buffer，也无法在 RS 之前插入处理。
- 因此「一路预览、小艺 fork 三份」不成立，必须由相机 Session **配两路 Output**：

| 路 | 消费者 | 用途 | 配置建议 |
|----|--------|------|----------|
| Surface A（显示路） | RS | 用户所见预览 | 全分辨率、30fps，谁都不碰 |
| Surface B（分析路） | 小艺进程（ImageReceiver / native 消费者） | 门控、感知、模型、AR | 可降分辨率、降帧率；小艺 acquire/release 自控节奏 |

- 同一帧同时投两路，**timestamp 一致**，对齐天然成立。
- 不推荐「小艺先消费再转发到显示」：多一次拷贝 + 至少一帧延迟，预览拖尾。
- AR 若需不同尺寸/格式，再加第三路 Output；否则与 B 共用，在小艺进程内分发。

### 2.1 和「BT709_FULL」的关系（写进契约）

- **RGB**：像素通道模型（或可转成 RGB 的 YUV）。
- **BT.709 + FULL**：色域/传递特性 + Full range（0～255 类），规定「怎么解释这些数值」。
- 接口必须再写死：**实际 pixel format**（RGB888 / RGBA / NV12…）、位深、stride、旋转/镜像责任方。

---

## 3. 流程图

### 3.1 进 Tab → 起预览流

```text
用户切到小艺 Tab
    │
    ▼
小艺 UEC onSessionCreate / TabShow
    │
    ▼
[争议A] 谁创建 Surface？（两路都要定）
    ├─ Surface A（显示）：XComponent 所在进程创建，消费者 = RS
    └─ Surface B（分析）：小艺创建 ImageReceiver，消费者 = 小艺
    │
    ▼
小艺 → 相机: StartPreviewForXiaoyi([
              {surfaceId=A, size=全分辨率, fps=30, role=DISPLAY},
              {surfaceId=B, size=小图, fps=1~5, role=ANALYSIS, format=BT709_FULL}
            ], needMotionMeta)
    │
    ▼
相机 App 调整 Session（可能让出主预览 / 增加两路 Output）
    │
    ▼
Framework → HDI → HAL 配流并 start
    │
    ▼
相机 → 小艺: OnPreviewStarted(actualConfig)
    │
    ▼
连续: Surface A 直达 RS 上屏；Surface B 出帧到小艺 + OnPreviewMetadata(motion, 同 timestamp)
    │
    ▼
小艺在 Surface B 上 acquire → 门控 / 模型队列 / AR → release —— 处理不过来就丢帧，别堆积
```

### 3.2 稳定帧 → 模型推理（不拍深度也可）

```text
每帧 motion meta（随预览实时）
    │
    ▼
StableFrameDetector
  - |gyro|/accel 低于阈值，连续 K 帧或持续 M ms
  - 可选: 对焦稳、曝光稳、帧差小
    │
    ├─ 不稳 → 丢弃 / 取消进行中的推理
    └─ 稳定 → OnStableFrame(ts)
              │
              ▼
         取 ts 对应预览帧（或最近稳帧）→ 模型 / 轻量检测
              │
              ▼
         结果 → 分发服务 → 规则 → chips（可带冷却与去重）
```

### 3.3 用户点击「拍摄」→ RGB + 深度（对表重点）

> 默认理解：**不是在旧预览水管里「挖」深度**，而是用当前/指定 timestamp 触发一次 Capture（RGB + 按需深度）。

```text
用户点击拍摄
    │
    ▼
小艺（可选）确认当前为稳定帧 / 记录 targetTimestamp=T
    │
    ▼
小艺 → 相机: CaptureAt({
          targetTimestamp: T | CURRENT,
          needRgb: true,
          needDepth: true,
          allowPausePreview: true/false,   // 争议C
          timeoutMs
        })
    │
    ▼
相机 App → Framework → HDI → HAL
    ├─ 抓取接近 T 的 RGB（预览级或拍照级 —— 争议D）
    ├─ 单次深度计算（HAL 已口头可支持）
    ├─ 附带 motion 等 metadata，timestamp 对齐
    └─ 可选短暂停预览 / 降负载
    │
    ▼
回传（示意）:
    - rgb: Surface / PixelMap / fd
    - depth: fd 或 handle + width/height/stride/单位(米)/置信度
    - meta: 与同一 timestamp 绑定的运动等
    │
    ▼
小艺 map(fd/handle) 读深度 → 与 RGB 对齐校验
    → 模型加强分析 / AR 建模 / 落业务结果
    → 释放 fd/handle
    → 若曾 Pause，则 ResumePreview
```

**fd 是什么：** 跨进程共享大块内存的「取货号」。小艺拿到 fd/handle + 描述信息后，在本进程 map 成可读写内存，用完释放。  
**HDI：** 深度从 HAL 经 HDI 到框架；小艺只调相机 App（或系统 Camera API），**不直接调 HDI**。

### 3.4 出 Tab / 后台

```text
TabHide / onBackground / 宿主抢占
    │
    ▼
小艺停推理/AR/chips 更新
    │
    ▼
小艺 → 相机: StopPreviewForXiaoyi / ReleaseAll
    │
    ▼
相机停小艺 Output，恢复主预览（若需要）
    │
    ▼
OnPreviewStopped → 小艺可销毁 Surface
```

### 3.5 （可选）从本 Tab 跳到小艺另一个「相机能力」UEC

```text
推荐（争议E）:
  小艺按钮 → 通知相机宿主切换/拉起 UEC2
  → 先 Stop 当前预览与感知
  → 再 Start UEC2
  → 禁止 UEC1 内直接嵌套 UEC2 握相机（易抢流 + 双跨进程）
```

---

## 4. 接口清单（小艺 ↔ 相机 App）

> 命名可改，**语义建议保留**。方向以小艺视角。

### 4.1 能力协商

| # | 接口 | 方向 | 关键参数 / 返回 | 说明 |
|---|------|------|-----------------|------|
| C1 | `QueryCameraCapability` | 小艺→相机 | — | 进 Tab 前或首次连接 |
| C2 | `QueryCameraCapabilityResult` | 相机→小艺 | 预览 sizes；formats（是否 BT709_FULL）；fps；**最大并发 Output 数及允许的分辨率组合**；实时 motion meta；按需深度；深度类型；能否 Pause；热限流策略 | 能力位 |

### 4.2 预览会话（B 类）

| # | 接口 | 方向 | 关键字段 | 说明 |
|---|------|------|----------|------|
| P1 | `ProvideSurfaces` | 双向之一 | `[{surfaceId, role: DISPLAY \| ANALYSIS}]` | **两路 Surface**；显示路消费者为 RS，分析路消费者为小艺（争议 A：各由谁创建） |
| P2 | `StartPreviewForXiaoyi` | 小艺→相机 | `outputs: [{surfaceId, size, format, fps, role}]`, needMotionMeta, rotation | 一次请求配多路 Output；同一帧 timestamp 一致 |
| P3 | `OnPreviewStarted` | 相机→小艺 | actual size/format/fps | 以实配为准 |
| P4 | `StopPreviewForXiaoyi` | 小艺→相机 | reason | Tab 切走等 |
| P5 | `OnPreviewStopped` | 相机→小艺 | — | 确认可拆 Surface |
| P6 | `UpdatePreviewConfig` | 小艺→相机 | size/fps… | 可选 |
| P7 | `PausePreview` / `ResumePreview` | 小艺→相机 或相机内建 | reason | 拍摄/深度时 |
| P8 | `OnPreviewPaused` / `OnPreviewResumed` | 相机→小艺 | — | 同步 UI |

**若「小艺自己预览」= 画面画在 UEC，但 Session 仍在相机 App：B 类仍需要。**  
**仅当小艺进程自己 openCamera 握会话时，才可能弱化对「相机 App」的 B 类，改调系统 Camera API，并单独做资源交还（争议F）。**

### 4.3 帧与实时运动 Meta

| # | 接口 | 方向 | 关键字段 | 说明 |
|---|------|------|----------|------|
| M1 | `OnPreviewFrame` | 相机→小艺 | timestamp, buffer/fence, transform | 或仅 Surface 隐式出帧 |
| M2 | `OnPreviewMetadata` | 相机→小艺 | **同一 timestamp**；gyro/accel/姿态；对焦；曝光；moving 标记等 | **随预览实时**，供稳定帧 |
| M3 | （小艺内）`OnStableFrame` | 内部 | timestamp | 推理门控事件 |

**对齐硬约束：** `metadata.timestamp` 与 `frame.timestamp` 必须可对齐（同一时钟域或有明确换算）。meta 缺失则不得标稳定。

### 4.4 拍摄 / 按需深度

| # | 接口 | 方向 | 关键字段 | 说明 |
|---|------|------|----------|------|
| D1 | `CaptureAt` | 小艺→相机 | targetTimestamp / CURRENT；needRgb；needDepth；allowPausePreview；timeoutMs | 用户点击拍摄 |
| D2 | `OnCaptureResult` | 相机→小艺 | timestamp；rgb（PixelMap/fd/…）；depthFd 或 depthHandle；depth 宽高 stride 单位 置信度；motionMeta | 成功 |
| D3 | `OnCaptureFailed` | 相机→小艺 | code, message | 超时/对不齐/HAL忙等 |
| D4 | `CancelCapture` | 小艺→相机 | — | 取消进行中 |

**深度路径说明（对 HAL 同事确认）：** HAL 算深 → **HDI** → Framework → 相机 App → `OnCaptureResult`。小艺不直连 HDI。

### 4.5 生命周期与抢占

| # | 接口 | 方向 | 说明 |
|---|------|------|------|
| L1 | `OnXiaoyiTabShow` / `OnXiaoyiTabHide` | 相机→小艺 | Hide 停推理/AR |
| L2 | `OnHostCameraBusy` | 相机→小艺 | 宿主拍照/录像要回主预览 |
| L3 | `ReleaseAll` | 双向 | 断链、进程异常 |

### 4.6 建议错误码

`OK` · `NO_PERMISSION` · `CAMERA_IN_USE` · `SURFACE_INVALID` · `FORMAT_UNSUPPORTED` · `TIMEOUT` · `DEPTH_UNAVAILABLE` · `TIMESTAMP_MISMATCH` · `DEVICE_THERMAL` · `UEC_DISPLAY_UNSUPPORTED`

---

## 5. 数据对象（建议）

### 5.1 PreviewConfig

```text
width, height
pixelFormat          // 例: RGBA_8888 / NV12 —— 必须写实
colorStandard        // BT709
colorRange           // FULL
fps
needMotionMeta: bool
```

### 5.2 MotionMetadata（每帧或与帧绑定）

```text
timestamp
gyro: {x,y,z}
accel: {x,y,z}
optional: orientation / angularSpeedNorm / isMoving
optional: afState, aeExposureNs
```

### 5.3 DepthBuffer

```text
timestamp            // 必须与 RGB 对齐策略写清
fd 或 handle
width, height, stride
dataType             // uint16 depth_mm / float meters / ...
unit
confidenceFd?        // 可选
```

### 5.4 CaptureResult

```text
timestamp
rgb: { type: PIXELMAP|FD|SURFACE_STILL, ... }
depth?: DepthBuffer
motionMeta?
```

---

## 6. 待讨论 / 有争议的点（开会用）

| ID | 议题 | 选项 / 问题 | 影响 |
|----|------|-------------|------|
| **A** | Surface 谁创建？ | 小艺创建并交 surfaceId vs 相机创建再下发 | 生命周期、销毁顺序、黑屏责任 |
| **B** | 「fork 三份」怎么做？ | **已收敛：Session 多 Output 为基线**（显示路 A 消费者是 RS，应用层截不到帧，单路 fork 不成立）。待定：AR 是否需第三路 Output，还是与分析路 B 共用后在小艺进程内分发 | HAL 并发 Output 上限、带宽、功耗 |
| **C** | 拍深度时是否停预览？ | 允许短暂停 vs 不停只降帧 vs 并行 | 体感闪一下 vs 深度质量/算力 |
| **D** | 拍摄 RGB 用预览帧还是高质量 Still？ | 预览级抓帧 vs 正式拍照输出 | 画质、时延、与深度对齐难度 |
| **E** | 第二个小艺相机 UEC 怎么跳？ | 宿主切换 vs UEC 内嵌套拉起 | 嵌套跨进程、抢摄像头 |
| **F** | 「小艺自己预览」含义？ | 仅 UI 在 UEC 显示（Session 仍在相机）vs 小艺自己 openCamera | 是否还要 B 类对相机 App 接口 |
| **G** | UEC 内显示是否可用 XComponent？ | 文档曾列不支持；需目标版本实测 | 显示放 UEC 还是宿主画、小艺只分析 |
| **H** | 深度与 RGB 对齐时钟 | 同一 timestamp 强制 vs 允许 δt + 外参补偿 | AR/模型精度 |
| **I** | motion meta 字段集 | HAL 能出哪些；是否每帧；丢失策略 | 稳定帧误判率 |
| **J** | BT709_FULL 落地格式 | 到底 RGB 还是 YUV；stride/旋转谁做 | 偏色、模型输入错 |
| **K** | 深度 fd 所有权与释放 | 谁 close；超时未释是否泄漏 | 稳定性 |
| **L** | 稳定帧阈值 | K 帧 / M ms / 光流辅助是否要 | 推理频率与发热 |
| **M** | 主预览与小艺预览互斥策略 | 进 Tab 停主预览 vs 双 Output 共存 | 产品体验 + HAL 能力 |
| **N** | 安全与隐私 | 预览/深度是否落盘；端侧模型是否出域 | 合规 |

---

## 7. 建议拍板顺序（会议议程）

1. **F + M**：会话主人是谁；进 Tab 后主预览怎么处理。  
2. **A + G**：Surface 与显示链路（UEC 能否 XComponent）。  
3. **J + I**：预览 format + 实时 motion meta 字段与时钟。  
4. **B + L**：三路分发与稳定帧门控。  
5. **D + C + H + K**：拍摄瞬间 RGB/深度路径、停流、对齐、fd 生命周期。  
6. **E**：是否支持跳第二个相机向 UEC。  

---

## 8. 非目标 / 暂不纳入本草案

- chips 具体 UI 规范与规则 DSL 细节  
- 端侧大模型选型与量化  
- 与第二个 UEC 的完整产品交互稿（仅保留跳转原则 E）

---

## 9. 术语速查

| 术语 | 含义 |
|------|------|
| UEC | UIExtension 嵌入组件/页面，小艺 Tab 的载体 |
| Surface / surfaceId | 收图像 Buffer 的管道及 ID |
| fd | file descriptor，跨进程访问共享内存的取货号 |
| handle | 指向 Buffer 的凭证（实现可能包着 fd） |
| HDI | Hardware Driver Interface，框架↔HAL；应用通常不直连 |
| BT709_FULL | BT.709 色域语义 + Full range |
| 稳定帧 | 运动 meta（等）判定足够稳，才触发重推理 |

---

*文档结束。可将本节直接贴进评审纪要，争议表按 ID 逐项勾选结论。*
