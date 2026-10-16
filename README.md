# mecanum_car

메카넘 휠 AGV용 ROS Noetic 패키지. Gazebo 시뮬레이션 환경에서 IR 라인 트레이싱과 초음파 장애물 정지를
수행하고, 키보드 teleop으로 메카넘 특유의 전방향 주행(평행이동·대각선 이동)을 제어한다.

강원대학교 메카트로닉스공학전공 제어시스템설계및응용 과제로 작성.

## 구성

```
mecanum_car/
├── config/line_follower_params.yaml   AGV 물리·제어 파라미터
├── launch/line_tracking.launch        Gazebo + URDF spawn + 주행 노드 일괄 실행
├── scripts/
│   ├── line_tracer.py                 IR 2채널 PID 라인 트레이싱 (메인)
│   ├── obstacle_detector.py           초음파 전/후방 장애물 판정
│   ├── mecanum_controller.py          단발 명령식 키보드 제어
│   └── mecanum_teleop.py              pynput 기반 연속 teleop
├── urdf/agv.urdf                      AGV 모델
└── worlds/agv.world                   라인이 그려진 Gazebo 월드
```

## 노드와 토픽

| 노드 | 구독 | 발행 |
|---|---|---|
| `line_tracer` | `/ir_sensor/L_front/image_raw` (`sensor_msgs/Image`, mono8)<br>`/ir_sensor/R_front/image_raw`<br>`/obstacle_status` (`std_msgs/Bool`) | `/cmd_vel` (`geometry_msgs/Twist`) |
| `obstacle_detector` | `/ultrasonic/front` (`sensor_msgs/Range`)<br>`/ultrasonic/rear` | `/obstacle_status` |
| `mecanum_controller` / `mecanum_teleop` | 키보드 | `/cmd_vel` |

IR 센서는 Gazebo 카메라 플러그인으로 흑백 이미지를 내보내며, `line_tracer` 가 각 이미지의 평균 밝기를
센서값으로 환산한다.

## 제어 로직 (`line_tracer.py`)

- **오차** `error = right_value - left_value` (좌우 IR 평균 밝기 차)
- **PID** `Kp=0.006, Ki=0.000, Kd=0.008`, 적분항 ±1000 anti-windup, 20 Hz
- **속도** `linear.x = max(0.05, 0.35 - |angular.z| * 0.1)` — 조향이 클수록 감속
- **라인 이탈 판정** 좌우 모두 밝기 > 200 이 60틱(약 3초) 지속되면 종료 지점으로 간주
- **종료 동작** `turn_180()` 으로 제자리 180° 회전(`angular.z=0.8`, `π/0.8` 초) 후 복귀 주행
- **장애물** `/obstacle_status` 가 `true` 인 동안 정지, 해제되면 PID 상태 유지한 채 재개

`obstacle_detector` 는 전방 또는 후방 30 cm 이내를 장애물로 판정한다.

## 빌드 · 실행

```bash
cd ~/catkin_ws/src
git clone https://github.com/do-gongil/mecanum-car-ros.git mecanum_car
cd ~/catkin_ws && catkin_make
source devel/setup.bash

roslaunch mecanum_car line_tracking.launch
```

teleop은 별도 터미널에서:

```bash
rosrun mecanum_car mecanum_teleop.py      # 화살표 키 연속 제어 (pynput 필요)
rosrun mecanum_car mecanum_controller.py  # w/s/a/d/q/e/z/c/x 단발 명령
```

### 의존성

`rospy` `roscpp` `std_msgs` `sensor_msgs` `geometry_msgs` `gazebo_ros` `gazebo_plugins`
`robot_state_publisher` `joint_state_publisher` `tf` `cv_bridge`, Python: `numpy` `opencv-python` `pynput`

## 알려진 이슈

- `config/line_follower_params.yaml` 의 PID 게인(`kp=15.0` 등)은 현재 어느 노드에서도 로드하지 않는다.
  `line_tracer.py` 는 게인을 코드에 하드코딩하고 있다.
