cmake_minimum_required(VERSION 3.0.2)
project(mecanum_car)

find_package(catkin REQUIRED COMPONENTS
  rospy
  sensor_msgs
  roscpp
  std_msgs
  geometry_msgs
  gazebo_ros
  gazebo_plugins
  robot_state_publisher
  joint_state_publisher
  tf
)

catkin_package(
  CATKIN_DEPENDS 
    rospy 
    roscpp 
    std_msgs 
    geometry_msgs 
    gazebo_ros
    gazebo_plugins
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

# Python scripts install
catkin_install_python(PROGRAMS
  scripts/mecanum_controller.py
  scripts/mecanum_teleop.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# Launch file install
install(DIRECTORY launch/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/launch
)

# URDF file install
install(DIRECTORY urdf/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/urdf
)

# Mesh file install
install(DIRECTORY meshes/
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}/meshes
)
