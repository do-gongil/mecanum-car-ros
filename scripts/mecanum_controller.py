#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
import sys
import tty
import termios

class MecanumController:
    def __init__(self):
        rospy.init_node('mecanum_controller', anonymous=True)
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.rate = rospy.Rate(10)
        
        # 속도 설정
        self.linear_speed = 0.3  # m/s
        self.angular_speed = 1.0  # rad/s
        
    def move_forward(self):
        """전진"""
        vel = Twist()
        vel.linear.x = self.linear_speed
        self.pub.publish(vel)
        
    def move_backward(self):
        """후진"""
        vel = Twist()
        vel.linear.x = -self.linear_speed
        self.pub.publish(vel)
        
    def move_left(self):
        """왼쪽으로 평행 이동 (메카넘 특성)"""
        vel = Twist()
        vel.linear.y = self.linear_speed
        self.pub.publish(vel)
        
    def move_right(self):
        """오른쪽으로 평행 이동 (메카넘 특성)"""
        vel = Twist()
        vel.linear.y = -self.linear_speed
        self.pub.publish(vel)
        
    def rotate_left(self):
        """제자리 좌회전"""
        vel = Twist()
        vel.angular.z = self.angular_speed
        self.pub.publish(vel)
        
    def rotate_right(self):
        """제자리 우회전"""
        vel = Twist()
        vel.angular.z = -self.angular_speed
        self.pub.publish(vel)
        
    def diagonal_forward_left(self):
        """대각선 전진 좌측"""
        vel = Twist()
        vel.linear.x = self.linear_speed
        vel.linear.y = self.linear_speed
        self.pub.publish(vel)
        
    def diagonal_forward_right(self):
        """대각선 전진 우측"""
        vel = Twist()
        vel.linear.x = self.linear_speed
        vel.linear.y = -self.linear_speed
        self.pub.publish(vel)
        
    def stop(self):
        """정지"""
        vel = Twist()
        self.pub.publish(vel)

def get_key():
    """키 입력 받기"""
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
    return key

def main():
    controller = MecanumController()
    
    print("\n=== 메카넘 휠 제어 ===")
    print("w: 전진")
    print("s: 후진")
    print("a: 좌측 평행이동")
    print("d: 우측 평행이동")
    print("q: 좌회전")
    print("e: 우회전")
    print("z: 대각선 전진 좌")
    print("c: 대각선 전진 우")
    print("x: 정지")
    print("Ctrl+C: 종료\n")
    
    try:
        while not rospy.is_shutdown():
            key = input("명령 입력: ")
            
            if key == 'w':
                controller.move_forward()
                print("전진")
            elif key == 's':
                controller.move_backward()
                print("후진")
            elif key == 'a':
                controller.move_left()
                print("좌측 평행이동")
            elif key == 'd':
                controller.move_right()
                print("우측 평행이동")
            elif key == 'q':
                controller.rotate_left()
                print("좌회전")
            elif key == 'e':
                controller.rotate_right()
                print("우회전")
            elif key == 'z':
                controller.diagonal_forward_left()
                print("대각선 좌")
            elif key == 'c':
                controller.diagonal_forward_right()
                print("대각선 우")
            elif key == 'x':
                controller.stop()
                print("정지")
            elif key == '\x03':  # Ctrl+C
                break
                
            rospy.sleep(0.5)
            controller.stop()  # 자동 정지
            
    except KeyboardInterrupt:
        controller.stop()
        print("\n종료")

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass