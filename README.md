# LeRobot · PiPER / PiPER-X 接入版

> 本仓库是 [huggingface/lerobot](https://github.com/huggingface/lerobot) 的二次开发分支，在原版基础上**新增了对 AgileX PiPER 与 PiPER-X 机械臂（单臂 / 双臂）的完整支持**。
>
> 原版 LeRobot 的完整说明请见 **[README_LEROBOT.md](./README_LEROBOT.md)**（即上游原始 README）。本文件只描述「我在原版上做了什么」以及如何使用 PiPER。

---

## TL;DR — 相对原版多了什么

- **4 个机器人类型**：`piper_follower`、`piperx_follower`、`bi_piper_follower`、`bi_piperx_follower`（通过 CAN 总线控制）。
- **4 个遥操作类型**：`piper_leader`、`piperx_leader`、`bi_piper_leader`、`bi_piperx_leader`，含**重力补偿（gravity compensation）**手动牵引示教。
- **PiPER SDK 封装**：[src/lerobot/utils/piper_sdk.py](src/lerobot/utils/piper_sdk.py)，统一关节名 / 动作键 / 单位换算。
- **打通主流程**：teleoperate / record / replay / rollout / calibrate 五个脚本都已接入 PiPER。
- **异步推理支持**：把 PiPER 加进 `SUPPORTED_ROBOTS`。
- **新增依赖 extra**：`lerobot[piper]`（`piper_sdk`、`can-dep`）。
- **机械臂模型资产**：`piper_description` / `piper_x_description` 的 URDF + 网格（用于重力补偿，Git LFS 存储）。
- **环境文件**：[environment.yml](environment.yml)（conda 环境 `lerobot-piperx`，Python 3.12）。
- **命令速查**：[PIPERX_COMMANDS.md](PIPERX_COMMANDS.md)。
- **注册测试**：[tests/test_piperx_registration.py](tests/test_piperx_registration.py)。

---

## 新增的设备类型

| 类别 | 类型名（`--robot.type` / `--teleop.type`） | 实现类 | 说明 |
| --- | --- | --- | --- |
| 机器人 | `piper_follower` | `PiperFollower` | 单臂 PiPER 从臂 |
| 机器人 | `piperx_follower` | `PiperXFollower` | 单臂 PiPER-X 从臂 |
| 机器人 | `bi_piper_follower` | `BiPiperFollower` | 双臂 PiPER 从臂 |
| 机器人 | `bi_piperx_follower` | `BiPiperXFollower` | 双臂 PiPER-X 从臂 |
| 遥操作 | `piper_leader` | `PiperLeader` | 单臂 PiPER 主臂 |
| 遥操作 | `piperx_leader` | `PiperXLeader` | 单臂 PiPER-X 主臂 |
| 遥操作 | `bi_piper_leader` | `BiPiperLeader` | 双臂 PiPER 主臂 |
| 遥操作 | `bi_piperx_leader` | `BiPiperXLeader` | 双臂 PiPER-X 主臂 |

> PiPER 与 PiPER-X 共享同一套逻辑，主要差别在重力补偿系数（`gravity_comp_tx_ratio`，见下文）和绑定的 URDF。

---

## 安装

### 1) 克隆并拉取 LFS 资产

机械臂网格/URDF 以 **Git LFS** 形式存放，克隆后需要单独拉取：

```bash
git clone git@github.com:heliang-pu/lerobot-piperx.git
cd lerobot-piperx
git lfs install
# 仅拉取 PiPER 资产（也可直接 git lfs pull 拉全部）
git lfs pull --include="src/lerobot/assets/piper_description/**,src/lerobot/assets/piper_x_description/**" --exclude="*"
git lfs checkout src/lerobot/assets/piper_description src/lerobot/assets/piper_x_description
```

> ⚠️ **重要**：本仓库 push 时，这些网格的 LFS 二进制对象在源机器上缺失（仅有指针），因此远端 LFS 里**暂时没有实际网格数据**。需要从原始资产来源补齐后再 `git lfs push`。在补齐之前，PiPER（非 X）的重力补偿会因 URDF 仍是 LFS 指针而报明确错误；纯收发数据 / 录制不受影响。

### 2) 用 conda 环境复现（推荐）

```bash
conda env create -f environment.yml      # 创建名为 lerobot-piperx 的环境（Python 3.12）
conda activate lerobot-piperx
```

### 3) 或用 pip extra 安装 PiPER 依赖

```bash
pip install -e ".[piper]"                 # 安装 piper_sdk + python-can 等
```

---

## CAN 总线准备

PiPER 通过 CAN 通信，命令里的 `--robot.port` / `--teleop.port` 填的是 **CAN 接口名**（例如 `can0`，或重命名后的 `can_follower` / `can_leader` / `can_left_follower` 等）。使用前请先把对应 CAN 接口拉起来，例如：

```bash
sudo ip link set can0 up type can bitrate 1000000
```

双臂场景需要为左右臂各自准备一个 CAN 接口。

---

## 快速开始

完整命令见 **[PIPERX_COMMANDS.md](PIPERX_COMMANDS.md)**（含录制带相机、replay、rollout、双臂等）。最小遥操作示例：

```bash
python -m lerobot.scripts.lerobot_teleoperate \
  --robot.type=piperx_follower \
  --robot.port=can_follower \
  --robot.id=my_piperx_follower \
  --robot.require_calibration=false \
  --robot.speed_ratio=20 \
  --teleop.type=piperx_leader \
  --teleop.port=can_leader \
  --teleop.id=my_piperx_leader \
  --teleop.require_calibration=false \
  --teleop.manual_control=false \
  --teleop.allow_missing_ctrl_mode_on_connect=true \
  --teleop.first_action_timeout_s=60
```

---

## 关键配置项

### 从臂（follower）— [config_piper_follower.py](src/lerobot/robots/piper_follower/config_piper_follower.py)

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `port` | （必填） | CAN 接口名 |
| `speed_ratio` | `100` | 跟随速度比例（0–100），手动牵引/调试时建议调小，如 `20` |
| `require_calibration` | `true` | 无标定文件时是否强制标定，可设 `false` 跳过 |
| `high_follow` | `true` | 高跟随模式 |
| `sync_gripper` | `true` | 是否同步夹爪 |
| `enable_on_connect` | `true` | 连接时自动使能 |
| `cameras` | `{}` | 录制时配置相机（见 PIPERX_COMMANDS.md） |
| `disable_on_disconnect` | `false` | 断开时是否下电 |

### 主臂 / 遥操作（leader）— [config_piper_leader.py](src/lerobot/teleoperators/piper_leader/config_piper_leader.py)

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `port` | （必填） | CAN 接口名 |
| `manual_control` | `true` | 手动牵引示教模式（启用重力补偿） |
| `allow_missing_ctrl_mode_on_connect` | `false` | 部分硬件仅在运动时才发 CAN 帧，置 `true` 容忍连接时缺失 |
| `first_action_timeout_s` | `30.0` | 首个动作等待超时 |
| `prefer_ctrl_messages` / `fallback_to_feedback` | `true` / `true` | 优先读控制帧，缺失则回退反馈状态 |
| `gravity_comp_*` | 见下 | 重力补偿参数（仅 `manual_control=true` 时生效） |
| `require_calibration` | `true` | 同上 |

### 重力补偿（gravity compensation）

实现见 [gravity_compensation.py](src/lerobot/teleoperators/piper_leader/gravity_compensation.py)，依赖对应 URDF：

- PiPER：`assets/piper_description/urdf/piper_no_gripper_description.urdf`
- PiPER-X：`assets/piper_x_description/urdf/piper_x_description_no_gripper.urdf`

关键参数：`gravity_comp_control_hz`（默认 200Hz）、`gravity_comp_torque_limit`（默认 8.0）、`gravity_comp_tx_ratio`（PiPER 默认 `0.2×6`，PiPER-X 默认 `1.0×6`）、`gravity_comp_base_rpy_deg`（底座姿态修正）。

---

## 相对原版改动一览

### 修改的上游文件

| 文件 | 改动 |
| --- | --- |
| [pyproject.toml](pyproject.toml) | 新增 `lerobot[piper]` extra（`piper_sdk`、`can-dep`）；`hardware` extra 引入 piper；`package-data` 打包 piper 资产 |
| [robots/utils.py](src/lerobot/robots/utils.py) | `make_robot_from_config` 注册 4 个 piper follower |
| [teleoperators/utils.py](src/lerobot/teleoperators/utils.py) | `make_teleoperator_from_config` 注册 4 个 piper leader |
| [utils/import_utils.py](src/lerobot/utils/import_utils.py) | 第三方插件加载：用内置实现替代 `lerobot_robot_piper`，并优雅跳过重复注册 |
| [async_inference/constants.py](src/lerobot/async_inference/constants.py) | `SUPPORTED_ROBOTS` 增加 4 个 piper 类型 |
| [async_inference/robot_client.py](src/lerobot/async_inference/robot_client.py) | 导入 piper 模块以触发注册 |
| [common/control_utils.py](src/lerobot/common/control_utils.py) | `policies` 改为延迟导入，避免可选依赖下的导入问题 |
| scripts: [calibrate](src/lerobot/scripts/lerobot_calibrate.py) / [record](src/lerobot/scripts/lerobot_record.py) / [replay](src/lerobot/scripts/lerobot_replay.py) / [rollout](src/lerobot/scripts/lerobot_rollout.py) / [teleoperate](src/lerobot/scripts/lerobot_teleoperate.py) | 导入 piper 模块以注册类型 |

### 新增文件

| 路径 | 内容 |
| --- | --- |
| [robots/piper_follower/](src/lerobot/robots/piper_follower/) | `PiperFollower` / `PiperXFollower` 及配置 |
| [robots/bi_piper_follower/](src/lerobot/robots/bi_piper_follower/) | `BiPiperFollower` / `BiPiperXFollower` 及配置 |
| [teleoperators/piper_leader/](src/lerobot/teleoperators/piper_leader/) | `PiperLeader` / `PiperXLeader`、配置、重力补偿 |
| [teleoperators/bi_piper_leader/](src/lerobot/teleoperators/bi_piper_leader/) | `BiPiperLeader` / `BiPiperXLeader` 及配置 |
| [utils/piper_sdk.py](src/lerobot/utils/piper_sdk.py) | PiPER SDK 封装、关节名 / 动作键 / 单位换算 |
| [assets/piper_description/](src/lerobot/assets/piper_description/) · [assets/piper_x_description/](src/lerobot/assets/piper_x_description/) | URDF + 网格（Git LFS） |
| [PIPERX_COMMANDS.md](PIPERX_COMMANDS.md) | 命令速查 |
| [environment.yml](environment.yml) | conda 环境定义 |
| [tests/test_piperx_registration.py](tests/test_piperx_registration.py) | 类型注册与第三方插件冲突测试 |

---

## 测试

```bash
pytest tests/test_piperx_registration.py -v
```

覆盖：单臂 / 双臂 PiPER-X 的类型注册与工厂构造、第三方 `lerobot_robot_piper` 插件与内置实现的冲突处理。

---

## 致谢与许可

基于 [huggingface/lerobot](https://github.com/huggingface/lerobot)，遵循上游 Apache-2.0 许可。PiPER 相关硬件接口基于 AgileX `piper_sdk`。原版完整文档见 [README_LEROBOT.md](./README_LEROBOT.md)。
