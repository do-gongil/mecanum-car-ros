#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist
from pynput import keyboard

class MecanumTeleop:
    def __init__(self):
        rospy.init_node('mecanum_teleop')
        self.pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        
        self.speed = 0.3
        self.turn = 1.0
        
        print("메카넘 휠 제어 시작")
        print("화살표 키: 이동, Shift+화살표: 회전, Space: 정지")
        
    def on_press(self, key):
        try:
            if key == keyboard.Key.up:
                self.vx = self.speed
            elif key == keyboard.Key.down:
                self.vx = -self.speed
            elif key == keyboard.Key.left:
                self.vy = self.speed
            elif key == keyboard.Key.right:
                self.vy = -self.speed
            elif key == keyboard.Key.space:
                self.vx = 0.0
                self.vy = 0.0
                self.vz = 0.0
        except:
            pass
            
        # Shift + 화살표로 회전
        if hasattr(key, 'char'):
            if key.char == 'q':
                self.vz = self.turn
            elif key.char == 'e':
                self.vz = -self.turn
                
        self.publish_cmd()
        
    def on_release(self, key):
        if key in [keyboard.Key.up, keyboard.Key.down]:
            self.vx = 0.0
        elif key in [keyboard.Key.left, keyboard.Key.right]:
            self.vy = 0.0
        elif key == keyboard.Key.esc:
            return False
            
        self.publish_cmd()
        
    def publish_cmd(self):
        twist = Twist()
        twist.linear.x = self.vx
        twist.linear.y = self.vy
        twist.angular.z = self.vz
        self.pub.publish(twist)
        
    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()

if __name__ == '__main__':
    try:
        teleop = MecanumTeleop()
        teleop.run()
    except rospy.ROSInterruptException:
        pass