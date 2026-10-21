# 类型 A：类 + 状态模拟

## A1 简易停车场（难度：中）

实现 `ParkingSystem`：

- `__init__(self, slots: int)`：车位总数
- `park(self, car_id: int) -> int`  
  - 有空位则停车，返回当前已停数量  
  - 无空位返回 `-1`
- `leave(self, car_id: int) -> int`  
  - 车在场内则离场，返回剩余车辆数  
  - 车不在场内返回 `-1`
- `status(self) -> List[int]`：返回当前在场 `car_id` 升序列表

规则：同一 `car_id` 已在场内时再 `park` 返回 `-1`（不重复占位）。

### 样例
```text
ParkingSystem(2)
park(101) -> 1
park(102) -> 2
park(103) -> -1
leave(101) -> 1
park(103) -> 2
status() -> [102, 103]
```

---

## A2 消息队列限流（难度：中上，贴近日志题）

实现 `RateLimiter`：

- `__init__(self, window: int, limit: int)`  
  - `window`：时间窗口长度（秒）  
  - `limit`：窗口内最多允许请求次数
- `request(self, t: int, user_id: int) -> bool`  
  - 时刻 `t`（非递减）用户 `user_id` 发来请求  
  - 若该用户在 `(t - window, t]` 内请求数已达 `limit`，拒绝返回 `False`  
  - 否则记录并返回 `True`  
  - 统计时：**只计成功接受的请求**
- `active_users(self) -> List[int]`  
  - 返回「至少成功过 1 次请求」的用户 id，升序

### 样例
```text
RateLimiter(10, 2)
request(1, 7) -> True
request(2, 7) -> True
request(3, 7) -> False
request(12, 7) -> True    # 时刻1已滑出窗口 (12-10, 12] = (2,12]，只剩时刻2一次
active_users() -> [7]
```

---

## A3 文件分卷写入（难度：中上，日志题变体）

实现 `VolumeWriter`：

- `__init__(self, volume_size: int, total_size: int)`
- `write(self, stream_id: int, length: int) -> int`  
  - 每个 `stream_id` 有当前分卷 `index`（从 1 起）和已用大小  
  - 若当前分卷 `used + length <= volume_size`：写入，返回写入后该分卷 `used`  
  - 否则新建下一 `index` 分卷再写；若 `length > volume_size` 返回 `-1`  
  - 系统总大小将超过 `total_size` 时：先按创建顺序删除最旧分卷，直到能写入  
  - 删除后该流若无分卷，新建时的 `index` 仍基于**历史最大 index + 1**（不回收编号）
- `list_volumes(self) -> List[List[int]]`  
  - 按创建顺序返回 `[stream_id, index, used]`

### 样例
```text
VolumeWriter(10, 27)
write(110, 4) -> 4
write(112, 2) -> 2
write(110, 7) -> 7
write(111, 5) -> 5
write(111, 8) -> 8
list_volumes() -> [[110,1,4],[112,1,2],[110,2,7],[111,1,5],[111,2,8]]
write(112, 8) -> 8
list_volumes() -> [[111,1,5],[111,2,8],[112,2,8]]
```

（逻辑与上次日志题同构，换皮重练。）
