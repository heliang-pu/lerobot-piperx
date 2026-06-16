# PiperX Commands

Use the Python 3.12 environment for this repository:

```bash
cd /home/phl/workspace/lerobot
export PYTHONPATH=src
PY=/home/phl/miniconda3/envs/lerobot-piperx/bin/python
```

## Single-Arm Teleoperation

```bash
$PY -m lerobot.scripts.lerobot_teleoperate \
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

## Single-Arm Record With Cameras

Replace camera indexes with the current `/dev/video*` or `/dev/v4l/by-id/*` paths.

```bash
$PY -m lerobot.scripts.lerobot_record \
  --robot.type=piperx_follower \
  --robot.port=can_follower \
  --robot.id=my_piperx_follower \
  --robot.require_calibration=false \
  --robot.speed_ratio=20 \
  --robot.cameras='{top: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}' \
  --teleop.type=piperx_leader \
  --teleop.port=can_leader \
  --teleop.id=my_piperx_leader \
  --teleop.require_calibration=false \
  --teleop.manual_control=false \
  --teleop.allow_missing_ctrl_mode_on_connect=true \
  --teleop.first_action_timeout_s=60 \
  --dataset.repo_id=phl/piperx_single_test \
  --dataset.root=/home/phl/workspace/dataset/Robot/piperx \
  --dataset.single_task="Move the phone from the source slot to the target slot" \
  --dataset.num_episodes=10 \
  --dataset.episode_time_s=60 \
  --dataset.reset_time_s=15 \
  --dataset.fps=30 \
  --dataset.push_to_hub=false \
  --dataset.camera_encoder.vcodec=h264 \
  --dataset.camera_encoder.preset=fast
```

## Replay

```bash
$PY -m lerobot.scripts.lerobot_replay \
  --robot.type=piperx_follower \
  --robot.port=can_follower \
  --robot.id=my_piperx_follower \
  --robot.require_calibration=false \
  --robot.speed_ratio=20 \
  --dataset.repo_id=phl/piperx_single_test \
  --dataset.root=/home/phl/workspace/dataset/Robot/piperx \
  --dataset.episode=0
```

## Single-Arm Policy Rollout

```bash
$PY -m lerobot.scripts.lerobot_rollout \
  --strategy.type=base \
  --policy.path=/path/to/pretrained_policy \
  --robot.type=piperx_follower \
  --robot.port=can_follower \
  --robot.id=my_piperx_follower \
  --robot.require_calibration=false \
  --robot.speed_ratio=20 \
  --robot.cameras='{top: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}' \
  --task="Move the phone from the source slot to the target slot" \
  --duration=60
```

## Bimanual Teleoperation

```bash
$PY -m lerobot.scripts.lerobot_teleoperate \
  --robot.type=bi_piperx_follower \
  --robot.id=my_bi_piperx_follower \
  --robot.left_arm_config.port=can_left_follower \
  --robot.left_arm_config.require_calibration=false \
  --robot.left_arm_config.speed_ratio=20 \
  --robot.right_arm_config.port=can_right_follower \
  --robot.right_arm_config.require_calibration=false \
  --robot.right_arm_config.speed_ratio=20 \
  --teleop.type=bi_piperx_leader \
  --teleop.id=my_bi_piperx_leader \
  --teleop.left_arm_config.port=can_left_leader \
  --teleop.left_arm_config.require_calibration=false \
  --teleop.left_arm_config.manual_control=false \
  --teleop.left_arm_config.allow_missing_ctrl_mode_on_connect=true \
  --teleop.right_arm_config.port=can_right_leader \
  --teleop.right_arm_config.require_calibration=false \
  --teleop.right_arm_config.manual_control=false \
  --teleop.right_arm_config.allow_missing_ctrl_mode_on_connect=true
```
