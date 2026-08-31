# 小艺 Skill / Tool 配套与版本治理

> 系统性整改方案 & 工具管理规范  
> 目标：**可以有配套关系，但消灭人肉版本配套表；不配套时体验可控；上架靠规则与自动化，不靠加人填表。**

---

## 一、问题定性

| 现状问题 | 后果 |
|----------|------|
| 配套写在每个 Skill 上（ROM/SP、包名、设备类型、API、锁屏、设备 ID…） | 矩阵爆炸；多团队/OD 填错；上架运营成本高 |
| Tool 上架不配 ROM/App 依赖 | 无法从 Tool 推导 Skill 生效范围；Skill 只能继续手填 |
| Skill 多版本与 ROM 绑定叙事混在一起 | 极限情况「一个 ROM 一份 Skill」 |
| 兼容范围与灰度放量共用一套「生效配置」 | 放量像改配套；全量还要改 Skill |
| 工具/CLI/ArkTS 登记不全，契约常写在 Skill 里 | 破坏性变更无扫描、无联动 |
| 多 Skill 联动无正式契约 | 一边升级另一边不知情，体验更难管 |

---

## 二、目标架构（三道门 + 两平台）

```text
                      ┌─────────────────────┐
                      │  工具管理平台 (ToMP) │  契约、版本、引入范围、兼容策略
                      └──────────┬──────────┘
                                 │ 依赖扫描 / 阻断
                      ┌──────────▼──────────┐
                      │  Skill 开放平台      │  requires、多版本、Release 放量
                      └──────────┬──────────┘
                                 │
 Query → skillSearch → skillGate │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ① Compat      ② Rollout    ③ Runtime
              (硬:能力匹配)  (软:灰度)    (执行前再断言)
                    │            │
                    └────┬───────┘
                         ▼
              可 load 的 skill_version（可 fallback 旧全量版）
```

**原则：**

1. **匹配真相** = 端能力（capabilities）⊇ Skill.requires；不是人填的 Skill×ROM 大表。
2. **对外一个 skillName；对内多 skill_version（artifact）**；Gate 选最高可跑版。
3. **灰度独立为 Release**，与兼容配置分离。
4. **Tool 按 2D API 管**；破坏性变更走评审 + major + Skill 联动。
5. **配套可推导后，Skill 上 ROM 范围降级为 legacy/override**，默认禁止新增长期人肉矩阵。

### 核心思路（一句话）

> Skill 显式声明依赖哪些 Tool（及契约版本）→ 用 Tool 元数据推导生效范围；当前 Tool 尚未配置 ROM/App 时，先用端侧 capabilities 做运行时对齐；灰度走独立放量层。

---

## 三、三个问题必须拆开

| 问题 | 本质 | 机制 |
|------|------|------|
| 生效范围 / 兼容 | 这台设备能不能跑 | `requires` ⊇ 端 capabilities；远期从 Tool 元数据推导 ROM/App 范围 |
| 多版本 | 同名技能留几份、选哪份 | 同一 `skillName` 多 `skill_version`；Gate 选最高可跑版 |
| 灰度放量 | 能跑，但先给谁用 | 独立 Release（百分比 / 白名单 / audience），不是改兼容 ROM |

**禁止**用同一个「Skill ROM 生效范围」同时表达兼容和灰度。

---

## 四、整改路线图（分期）

### Phase 0：定规范冻结乱法

- 发文冻结：禁止再把「灰度」写成 Skill 永久 ROM 范围。
- 明确三层配置：`requires`（兼容）/ `env_gates`（环境）/ `rollout`（放量）。
- 工具变更：已上线 tool **原则上不改名、不改语义、不删**；例外进 TMG。
- 不配套体验：Compat 失败 → 拒答/引导升级；禁止长 Loop。

### Phase 1：先跑通「能力匹配」（不依赖 Tool 填 ROM）

> **前提：** 当前 Tool 上架不配 ROM/App，推导链暂断。承认这一点，先用运行时能力对齐。

| 项 | 动作 |
|----|------|
| 端 | 冷启动/升级上报 capabilities 或 `profile_id + overrides`；日常请求带 `capability_hash` |
| Skill | 上架必填 `requires: [{tool, versionRange}]`（存量分批补） |
| skillGate | 增加 Compat：`capabilities ⊇ requires`；同名取最高可跑 version |
| 检索 | skillSearch 可保留粗 env 过滤；精匹配只在 Gate |
| 体验 | Compat 失败与 Rollout 未命中分错误码；后者优先 fallback 旧全量版 |

**交付物：** Gate 能力匹配上线；热门 Skill 完成 requires 标注。

### Phase 2：拆放量（Release）

| 项 | 动作 |
|----|------|
| 平台 | Skill 发布绑定 Release：whitelist → % → full + kill switch |
| 迁移 | 扫描「Skill ROM 下界高于真实能力下界」→ 标疑似灰度 → 迁到 `rollout.audience` |
| 运营 | 放量改 Release，不改 Skill 兼容字段 |

**交付物：** 灰度不再依赖改 Skill ROM 配置。

### Phase 3：建工具管理平台最小闭环

| 项 | 动作 |
|----|------|
| ToMP | 强制登记被 Skill 使用的 tool/CLI/ArkTS 出口（见第七节规范） |
| 联动 | Skill 上架：依赖必须在 ToMP 存在；Tool 变更：扫描受影响 Skill 并阻断/工单 |
| 元数据 | **分期**补 `min_rom` / `min_app` / `packages`（先热门、先被依赖） |

**交付物：** 「改 Tool 必知会影响哪些 Skill」；私有 ArkTS 出口可收编或标 skill-local。

### Phase 4：恢复「从 Tool 推导 Skill 生效范围」

| 项 | 动作 |
|----|------|
| 推导 | `effective_scope = intersect(required tools 的支持范围)` |
| Skill | ROM 范围改为只读展示；新建 Skill 默认禁止手填 ROM（仅 TMG override + 过期） |
| 清理 | 下线 legacy_scope；配套表岗位转为审 override + 破坏性变更 |

**交付物：** 人肉 Skill×ROM 主路径消灭。

### Phase 5：多 Skill 联动契约

- `needs_peer: otherSkill@range` 或共享「协作 contract」。
- Gate 校验 peer 也可 load；失败走降级路径（如只搜索不分享）。

---

## 五、Skill 侧整改规范

### 5.1 配置分层

| 层 | 字段 | 谁改 | 说明 |
|----|------|------|------|
| 身份 | `skill_name`, `skill_version`, `status` | 研发 | 对外名稳定 |
| 兼容 | `requires[]` | 研发 | 主门闩 |
| 环境 | `env_gates`：device_types / packages / lockscreen | 研发 | 薄；与 tool 无关的环境 |
| 推导范围 | `effective_scope`（只读） | 系统 | Phase4 后由 Tool 推 |
| 遗留 | `legacy_scope` | 迁移期 | 有 Tool 推导后废弃 |
| 放量 | Release.rollout | 运营 | 与 Skill 内容解耦 |
| 例外 | override / exclude + `expire_at` | TMG/值班 | 必须过期 |

### 5.2 Skill Manifest 示例

```yaml
skill_name: gallery.search
skill_version: 2.1.0
status: online          # draft | online | deprecated
requires:
  - tool: gallery.search
    version: ">=2.0.0 <3.0.0"
  - tool: device.share
    version: "^1.0.0"
optional:
  - tool: car.hud.display
    version: ">=1.0.0"
env_gates:
  device_types: [phone, pad]
  packages: [com.huawei.xiaoyi]
  lockscreen_executable: false
# effective_scope: 平台自动推导，只读展示（Phase4）
```

### 5.3 多版本策略

| 变更 | 版本动作 |
|------|----------|
| 体验优化，requires 不变 | 覆盖发布或 patch；不必按 ROM 增副本 |
| 新增子技能，requires 变严 | **新 skill_version**；老设备 Gate 选旧版或拒答新能力 |
| Tool major 破坏性变更 | 旧版 requires 封顶；新版依赖新 major；并存至兼容期结束 |

**选型规则：**

1. 用能力/推导范围算出本机可跑版本集合。
2. 集合内取最高 `skill_version`。
3. 新版 Rollout 未命中 → fallback 上一已 `full` 的版本。
4. 集合为空 → 可召回逻辑名，但拒答/引导升级，不 Loop。

**ROM 推演示例（同名多版本）：**

| ROM | 可跑版本 | 实际 load |
|-----|----------|-----------|
| 1.0 | ∅ | 拒答 |
| 2.0 / 3.0 | v1.x | 最高可跑的 v1.x |
| 4.0 | v1.x 且 v2.x | **v2.x**（优先新；未进灰度则 fallback v1） |

> 产品语义上「一个 Skill 支持所有 ROM」；工程上靠多版本 + Gate 选型，不是单份 md 兼容宇宙。

### 5.4 Skill 变更场景（对齐纪要并工程化）

**场景 1：Skill 变更**

1. 技能范围不变、不增 ROM 新 tool → 直接上架更新（走 Release 放量）。
2. 新增子技能依赖新 tool → 新版本；老 ROM/无能力用户问到新能力 → **拒答**，不 Loop。
3. 禁止在旧 SOP 塞「必须新 ROM 新 tool」的分支；例外 → TMG + 新版本。

**场景 2：工具变更**  
见第七节；Skill 不得依赖未登记工具（Phase3 起强制）。

### 5.5 现有 Skill 生效配置迁移

| 原配置意图 | 迁到 |
|------------|------|
| 没这 tool 就不能跑 | 删，改 requires；远期 + Tool 元数据推导 |
| 车机/手机/包名/锁屏 | `env_gates` |
| 先小范围试试 | `rollout`（百分比/白名单/audience） |
| 某 SP 有坑 | `rollout.exclude` 或临时 override（带过期） |
| 定向某 device_id 验证 | `rollout.whitelist` |

迁移扫描：凡「ROM 下界高于 tool/能力真实下界」的，默认标成 **疑似灰度**，负责人确认迁到 Release。

---

## 六、端云匹配、上报与 skillGate

### 6.1 管理逻辑总图

```text
ROM / App 版本
      │ 映射（端适配层 / 平台 Profile）
      ▼
Capabilities（tool + contract_version + status）
      │ 上报 / hash
      ▼
Skill Matching（skillGate）
  ← Skill.requires
  ← Contract Catalog（ToMP）
      │
      ├─ 通过 → Release 放量判断 → load / fallback
      └─ 不通过 → 拒答 / 引导升级
```

### 6.2 端上报

**时机：**

1. 启动 / 登录 — 全量
2. App / ROM 升级后 — 全量刷新
3. 拉 Skill 列表 / 会话开始 — 带 hash，有变化再全量
4. 热更新导致契约变化 — 增量

**推荐模式（平台可配 Profile 基线）：**

- **平台配：**「应该有什么」（ROM/App → 默认 capabilities 剖面）
- **端报：**「我是哪一版 + 实际差在哪」（overrides）
- **Gate 用：** `Profile ⊕ overrides`

端不必每次把全量工具清单塞进 query；日常只带 `capability_hash`。

**关键字段示例：**

```json
{
  "device_id": "d_xxx",
  "app_id": "xiaoyi.phone",
  "app_version": "5.3.1",
  "rom_version": "6.1.0.135(SP17C00E135RP5)",
  "capability_hash": "a1b2c3",
  "capabilities": [
    {
      "tool": "maps.navigate",
      "contract_version": "2.1.0",
      "status": "available",
      "features": ["traffic"]
    },
    {
      "tool": "car.hud.display",
      "contract_version": "1.0.0",
      "status": "unavailable",
      "reason": "not_supported_on_device"
    }
  ]
}
```

| 字段 | 是否必须 | 用途 |
|------|----------|------|
| `tool` | 必须 | 与契约目录一致 |
| `contract_version` | 必须 | 当前契约版本 |
| `status` | 建议 | available / unavailable / degraded |
| `features` | 可选 | 细粒度能力 |
| `schema_digest` | 可选 | 防端云漂移 |

**端侧要感知的版本信息（控制维度数量）：**

| 层级 | 字段 | 用途 |
|------|------|------|
| 环境门闩（粗） | 设备类型、应用包名、锁屏可否执行 | Search 前过滤 |
| 能力契约（主） | capabilities / capability_hash | Gate 唯一真相 |
| 诊断旁路（辅） | 完整 ROM（含 SP）、app_version、Harmony API | 日志、灰度 audience、override |

`device_id`、名称等：仅定向灰度/白名单，不进常规 Skill 上架必填。

### 6.3 谁来判断匹配

**由 skillGate（或 Matching 模块）统一判断**，不是模型，也不是各业务自己写 if ROM。

| 组件 | 职责 |
|------|------|
| Capability Registry / Profile | 收上报、存设备能力或按版本解析剖面 |
| ToMP Contract Catalog | tool 与版本兼容规则 |
| **skillGate** | **唯一做 capabilities ⊇ requires 的裁判** |
| Release / Rollout | 放量软门闩 |
| Agent Runtime | 执行前再断言 tool 仍 available |

模型只负责：在 **已 Gate 通过** 的 TopK 里选最终 load 哪个 Skill。

### 6.4 skillGate 流程

```text
1. skillSearch(query, device_ctx)
     → 语义 TopK（可先用 env_gates 粗滤）

2. Compatibility Gate（硬）
     caps = Profile(rom, app, package) ⊕ device_overrides
     for each candidate version:
       pass_compat = caps ⊇ requires 且 env_gates OK
     同 skill_name 保留「通过 compat 的最高 skill_version」

3. Rollout Gate（软）
     release = 该 version 当前 Release
     if kill_switch or stage=off → reject
     if whitelist hit → pass
     if audience 不匹配 → reject（放量失败，不是「不支持」）
     if percentage: bucket = hash(id + salt) % 100; pass = bucket < percentage
     if stage=full → pass

4. 通过的进模型最终 load
5. 执行前 Runtime 再断言 tool available
```

### 6.5 错误码与体验

| code | 用户侧 | 说明 |
|------|--------|------|
| `incompatible` | 当前系统暂不支持 / 引导升级 | 硬失败 |
| `not_in_rollout` | 尽量 fallback 旧全量版；无旧版再弱提示 | 软失败 |
| `peer_unavailable` | 降级功能说明 | 联动 |
| `tool_runtime_missing` | 短暂失败 + 可重试/降级 | 缓存过期等 |

灰度期最佳体验：**新版未命中放量 → 自动 fallback 到上一已全量版本**，不要和 compat 失败共用「请升级 ROM」。

---

## 七、工具管理规范（ToMP）

### 7.1 范围

纳入管理的出口统一称 **Tool Contract**，包括：

- 意图 / 端侧工具接口
- CLI
- ArkTS 可调用函数 / 脚本出口（含现写在 Skill 内、对外可调的部分）
- 其它 Agent 可 invoke 的端能力

**未登记不得被线上 Skill `requires` 引用（Phase3 起强制）。**

> tools 和 CLI 本质是新接口：OH 开发、Skill 有依赖；版本平时的接口怎么管，这里就怎么管。

### 7.2 必填元数据（最小集）

| 字段 | 必填阶段 | 说明 |
|------|----------|------|
| `tool_id` | P3 | 全局唯一，稳定，禁止随意改名 |
| `contract_version` | P3 | semver |
| `schema`（入参/出参） | P3 | JSON Schema 或等价描述 |
| `owner` / `team` | P3 | 责任田 |
| `status` | P3 | draft / active / deprecated / retired |
| `compatibility_policy` | P3 | 默认 `forward_compatible` |
| `consumers_scan` | P3 | 是否允许被 Skill 依赖 |
| `min_rom` / `introduced_in_rom` | **P4 前热门补齐，P4 强制新 tool** | 推导用 |
| `min_app_version` / `packages[]` | 按需 → P4 常用包强制 | 多包名小艺 |
| `features[]` | 可选 | 细粒度能力，少升 major |
| `deprecate_after` / `replace_by` | 弃用时 | 生命周期 |
| `schema_digest` | 建议 | 防漂移 |

### 7.3 版本与变更分级（对齐 2D API）

| 变更类型 | 版本 | 是否允许 | 流程 |
|----------|------|----------|------|
| 新增 tool | 1.0.0 起 | 允许 | 正常上架 |
| 新增可选字段 / 新 feature / 新能力旁路 | MINOR / feature | 允许 | 常规评审 |
| 文档/描述澄清，行为不变 | PATCH | 允许 | 常规 |
| 改默认值、改错误语义、收紧校验 | **MAJOR** | 限制 | **TMG** |
| 改名、删字段、删 tool、改必填 | **MAJOR / 禁止直接删** | 严格限制 | **TMG**；先 deprecate 双跑 |
| 图库等每 MR 新特性 | 优先 feature / MINOR | 鼓励 | **禁止改旧 contract 行为** |

**默认法则：已 `active` 的 contract 行为冻结；新能力新增，不打补丁改旧语义。**

专家分歧调和：

- 「优先向前兼容」管主路径。
- 「图库狂改」管的是新特性用新契约 / feature，不是每 MR 复制 Skill×ROM。

### 7.4 生命周期

```text
draft → active → deprecated → retired
              ↘（紧急）revoked
```

- `deprecated`：旧 Skill 仍可调用；**新 Skill 上架不得再依赖**（平台阻断）。
- `retired`：端可下线实现；依赖它的 Skill 必须已升级或下架。
- 双跑期：由 TMG 按 ROM 回合 / 存量占比配置（默认 N 个 MR 或固定月数）。

### 7.5 与 Skill 联动（硬规则）

1. **Skill 上架/升级：** `requires` 中每个 tool 必须存在且可引用；version range 可解析。
2. **Tool 提交 MAJOR / deprecate：** 自动列出依赖 Skill → 升级工单；未处理完不得 `retired`。
3. **Tool 改名：** 新 `tool_id` + 旧 id deprecate，禁止原地改 id。
4. **Skill 内联 ArkTS：**
   - 对外可调 → 必须提取为 ToMP 登记 tool；
   - 纯私有 → 标 `skill_local=true`，仍有 `contract_version`，仅该 Skill 可引用。
5. **禁止删除仍被 online Skill requires 的 tool。**

### 7.6 Tool 上架检查清单（门禁）

- [ ] `tool_id` / version / schema / owner 完整
- [ ] 是否破坏现网行为（自动 diff schema）
- [ ] MAJOR 是否有 TMG 单号
- [ ] 是否填写/更新 `min_rom`、`packages`（P4 或热门强制）
- [ ] 影响面：依赖 Skill 列表已确认或已建工单
- [ ] 端实现与契约测试通过（最小：schema 校验 + 冒烟）

### 7.7 端侧实现约束

- 适配层对外暴露稳定 contract；ROM 差异在适配层消化。
- 本机无能力 → capabilities 不声明或 `unavailable`，禁止报了又调挂。
- 新 ROM 只加能力时，旧 contract 必须保持可调用（向前兼容），除非已走 MAJOR 双跑。

### 7.8 当前「Tool 不配 ROM/App」的处理

| 阶段 | 策略 |
|------|------|
| 现在（P1–P2） | **不要假装能从 Tool 推导 Skill 生效范围**；主路径用端 capabilities ⊇ requires |
| P3 | ToMP 登记契约与 Skill 联动扫描（可不依赖 ROM 字段） |
| P3→P4 | 热门/被依赖 tool 补 `min_rom` 等；再切换推导，收回 Skill 人肉 ROM |

三条路并存时的优先级：**正道补 Tool 元数据；立刻可用能力匹配；Skill 手填 ROM 仅作 legacy 过渡。**

---

## 八、放量管理规范（Release）

### 8.1 为何独立

很多人配 Skill「生效 ROM」其实是想控制灰度。兼容与放量混填会导致：

- 放全量还要改 Skill，像在改配套关系；
- 配套表与运营策略缠死，人力上升。

### 8.2 Release 模型

```yaml
release_id: rel_20260831_gallery_2_1
skill_name: gallery.search
skill_version: 2.1.0
kill_switch: false
rollout:
  stage: percentage          # off | whitelist | percentage | full
  percentage: 10             # 0–100
  hash_salt: gallery_2_1
  hash_from: device_id       # device_id | user_id
  whitelist:
    user_ids: []
    device_ids: []
  audience:                  # 可选，缩小放量池，不是兼容
    rom_in: ["4.0.*", "4.1.*"]
    app_version_gte: "5.3.0"
    channels: ["huawei"]
    models: []
  exclude:                   # 临时黑名单，必须带过期
    - rom: "4.0.0.135"
      reason: "SP bug"
      expire_at: "2026-09-15"
```

### 8.3 平台两个面板

| 面板 | 内容 | 角色 |
|------|------|------|
| A 兼容 | requires、env_gates、推导范围只读、TMG override | 研发 / 上架 |
| B 放量 | whitelist → % → full、audience、kill switch | 运营 / 值班 |

产品与校验应拦住：在面板 A 用「ROM ≥ x」表达「先灰度再放」。

### 8.4 百分比稳定性

- `hash(device_id + skill_name + skill_version + salt) % 100`
- 升百分比时 salt 不变，已进组设备保持进组
- 新版本新放量：换 `skill_version` 或 salt
- 白名单优先于百分比

### 8.5 典型操作流

**新版本依赖更高 tool（如 ROM≥4.0 才 compat）：**

1. 上架 `2.1.0`，配好 requires →（P4）推导显示生效范围只读
2. Release：员工白名单 → 5% → 10% → 50% → full
3. 可选 audience 先限某 ROM；**full 后拆除 audience**
4. 旧版标 deprecated 或保留作 fallback 一期

**仅优化话术、requires 不变：** 覆盖发布 + 走放量；不必新开 ROM 条件。

**「先只给 ROM 4.0」：** 先问是跑不了还是先观察——前者进 requires/Tool；后者进 `rollout.audience`。

### 8.6 治理

- Release 展示：曝光、成功率、compat 拒绝率、rollout 未命中率、fallback 率
- 审计：percentage / kill_switch 变更留痕
- `exclude`、兼容 override 必须 `expire_at`
- `stage=full` 仍挂窄 audience → 黄灯「假兼容」

---

## 九、多 Skill 联动（子场景）

不要在 Skill A 的 md 里写死「依赖 Skill B 的某 ROM」。

```text
Skill A declares: needs_peer: share.collab@>=1.2
Gate: peer 也必须可被 load
不满足 → 降级路径（仅搜索不分享 / 明确不支持）
禁止半成功长 Loop
```

联动契约进平台，与 tool 一样可扫描、可阻断。

---

## 十、组织与管控

| 事项 | 建议归属 |
|------|----------|
| Tool MAJOR / 删除 / 改名 | TMG（具体组织名待定） |
| Skill 强塞 ROM 新 tool 分支 | 管控 TMG |
| 日常放量 | 业务运营 + 杀开关值班 |
| requires 与 ToMP 一致性 | 平台自动化 |
| 多团队共建同一 Skill 冲突 | 平台锁版本 + 责任田 / CODEOWNER |

**人力转向：** 原「多人盯上下架 + 人肉看冲突 / 配套表」→ 审异常 override、审破坏性变更、看 Gate 指标与告警。

---

## 十一、开放平台需求列表（摘要）

1. Skill 必填 `requires`；支持多 `skill_version` 并存与选型策略配置。
2. skillGate：Compat ∩ Rollout；错误码分离；fallback 旧全量版。
3. Release 放量：白名单 / 百分比 / full / kill switch / audience / exclude。
4. 端 capabilities 上报与 Capability Registry / Profile。
5. ToMP：工具登记、schema、版本、生命周期、Skill 双向扫描阻断。
6. Tool 元数据补 `min_rom` 等后：Skill `effective_scope` 自动推导只读；legacy ROM 配置迁移与退役。
7. OS/SP、「高于某版本」配置能力：**保留**，定位为推导展示、override、audience，不作长期主填法。
8. 多 Skill `needs_peer` 与降级路径。
9. 上架门禁与共建冲突检测（减少人肉审冲突）。

---

## 十二、验收标准

1. 新建 Skill **无需**填写完整 ROM/SP 矩阵即可上架（P4）；P1 起至少有 requires + 能力匹配。
2. 灰度 **100%** 走 Release；抽查无「用 Skill ROM 当灰度」新案例。
3. 任意 active tool 的依赖 Skill 列表可一键查出；MAJOR 变更有阻断。
4. 同名 Skill 多版本并存时，能力不足设备 **不会** load 新版空转；有拒答或 fallback。
5. 配套相关问题可归因：`incompatible` / `rollout` / `tool_runtime` / `peer`。
6. 高频 MR 业务：新特性以新 feature/MINOR tool 为主；requires 不变则不必出 ROM 副本。

---

## 十三、纪要遗留问题落锤建议

| 遗留 | 决议建议 |
|------|----------|
| Skill 要感知哪些端侧版本 | **粗** env_gates；**主** capabilities；**辅** 完整 ROM/App/API 仅诊断与 rollout/override |
| 开放平台配到 SP、支持「高于某版本」 | 能力保留；定位 **推导展示 + override/audience**，非长期主填法 |
| Tool 哪些必须向前兼容 | **active 行为默认冻结**；新能力新增；破坏走 MAJOR + TMG |
| Tool 与 Skill 怎么联动 | ToMP 登记 + requires 双向扫描阻断 |
| 当前 Tool 不配 ROM/App | **P1–P2 用能力匹配**；**P3–P4 补齐热门再推导**；不假装已能推导 |

---

## 十四、一页执行清单

| 优先级 | 项 | 依赖 |
|--------|----|------|
| P0 | 发规范：三层配置 + Tool 冻结规则 + 拒答/不 Loop | TMG |
| P1 | Skill requires 必填；端 capabilities；skillGate Compat | 端 + 云 Gate |
| P1 | Release 放量；灰度与 ROM 配置脱钩 | 开放平台 |
| P2 | ToMP 最小集 + 上架扫描 + ArkTS 收编策略 | 工具平台 |
| P2 | 多版本选型 + fallback 旧全量版 | Gate |
| P3 | Tool 补 min_rom/app；Skill 范围推导；legacy_scope 退役 | ToMP 元数据 |
| P3 | 联动 needs_peer | Gate + 平台 |

---

## 十五、总纲

**先** Skill 声明依赖 + 端能力门闩 + 独立放量，把配套从「人填 ROM」改为「运行时对齐」；  
**再** 补齐工具平台元数据与变更管控，把生效范围收回自动推导；  
**全程** 用 skillGate 保证不配套也可控（拒答 / 降级 / fallback，禁止长 Loop）。

> 可以有配套关系，但消灭版本配套表的维护；出问题体验落在可接纳范围内；靠规则和自动化让人写对，而不是靠加人。
