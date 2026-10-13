# 智能小车 · 车道保持与路标识别 · Smart Car (Lane Keeping & Sign Recognition)

> 基于**摄像头 + STM32 串口**的智能小车控制框架：使用 OpenCV 做车道线检测与路标模板匹配，通过串口控制电机与舵机。

## 功能

| 功能 | 实现 | 入口脚本 |
|------|------|----------|
| 车道保持 | HSV 阈值提取黄色车道线 → Canny → ROI → Hough 直线拟合 → 按偏移分段转向 | `lane.py` |
| 路标 / 道路标识识别 | 模板匹配（`matchTemplate`）+ NMS，识别 `left` / `right` / `turnaround` | `ctr_template_match.py` |
| 键盘手动控制 | `w/a/s/d` 前进转弯、`q/e` 原地旋转、`r/t` 平移、`z/x` 斜行、方向键调速、`c` 拍照 | `keyboard_ctr_car.py` |
| 动作序列演示 | 前进/后退、左右平移、原地旋转等固定动作序列 | `ctr_adv_bp.py`、`ctr_L_R.py`、`ctr_rotate.py`、`ctr_shift.py` |
| 车道线偏移计算 | 由拟合直线计算 `x0` 偏移，用于转向决策 | `get_X0.py` |

## 目录结构

```
.
├── lane.py                     # 车道保持主程序
├── ctr_template_match.py       # 路标模板匹配主程序
├── keyboard_ctr_car.py         # 键盘手动控制
├── ctr_adv_bp.py               # 前进+后退演示
├── ctr_L_R.py                  # 左转+右转演示
├── ctr_rotate.py               # 原地旋转演示
├── ctr_shift.py                # 平移演示
├── get_X0.py                   # 车道线偏移计算
└── src/
    ├── actions/                # 动作定义（base_action / complex_actions）
    ├── scenes/                 # 场景（manual / lane_following_threshold / helper_template_match / logo_match）
    │   └── templates/          # 路标模板图片
    └── utils/                  # 控制器 / 摄像头共享内存 / 日志 / 工具
```

## 运行环境

- 运行平台：Linux（本框架面向树莓派 / 嵌入式设备，使用 `/dev/ttyACM0` 串口与 V4L2 摄像头）
- 依赖：

```bash
pip install opencv-python numpy pyserial filelock
```

## 运行方法

```bash
python lane.py                # 车道保持
python ctr_template_match.py  # 路标识别
python keyboard_ctr_car.py    # 键盘手动控制
```

> 按 `Esc` 退出。

## 注意事项

- 代码中的串口名（`/dev/ttyACM0`）与模板目录路径为**机器相关路径**，换设备后需按实际调整。
- `src/utils` 中的控制器/相机/日志框架若为课程提供，请确认是否允许公开后再上传。
- 硬件相关代码需在真实小车上运行，无硬件时无法直接执行。

## 说明

- 本项目为《软件工程学期实训》课程实训作业。
