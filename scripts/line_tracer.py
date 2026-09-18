#!/usr/bin/env python3.8

import rospy
from std_msgs.msg import Bool
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class LineTracer:
    def __init__(self):
        rospy.init_node('line_tracer', anonymous=True)
        
        self.bridge = CvBridge()
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        
        self.ir_left_sub = rospy.Subscriber('/ir_sensor/L_front/image_raw', Image, self.ir_left_callback)
        self.ir_right_sub = rospy.Subscriber('/ir_sensor/R_front/image_raw', Image, self.ir_right_callback)
        # self.ir_left_sub = rospy.Subscriber('/ir_sensor/L_front/image_raw', Image, self.ir_left_callback)     #L_rear 수정 예정
        # self.ir_right_sub = rospy.Subscriber('/ir_sensor/R_front/image_raw', Image, self.ir_right_callback)   #R_rear 수정 예정
        
        # ir sensor값 init
        self.left_value = 255
        self.right_value = 255
        

        # [PID 제어 파라미터]
        self.base_speed = 0.35
        
        self.Kp = 0.006
        self.Ki = 0.000
        self.Kd = 0.008
        
        self.prev_error = 0
        self.integral = 0
        # ==========================================
        
        self.obstacle_detected = False
        rospy.Subscriber('/obstacle_status', Bool, self.obstacle_callback)
        
        self.end_point_reached = False
        self.return_mode = False
        self.line_lost_counter = 0
        self.line_lost_limit = 60 # 6000은 너무 길어서 60(약 3초)으로 조정함
        
        self.rate = rospy.Rate(20)

    def ir_left_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "mono8")
            # [수정 3] 오타 수정
            self.left_value = np.mean(cv_image)
        except Exception as e:
            pass
    
    def ir_right_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "mono8")
            self.right_value = np.mean(cv_image)
        except Exception as e:
            pass
    
    def obstacle_callback(self, msg):
        self.obstacle_detected = msg.data
    
    def turn_180(self):
        rospy.loginfo("=== End Point Reached! Turning 180 ===")
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        rospy.sleep(2.0)
        
        twist.angular.z = 0.8
        rotation_time = np.pi / 0.8
        
        start_time = rospy.Time.now()
        while (rospy.Time.now() - start_time).to_sec() < rotation_time:
            self.cmd_vel_pub.publish(twist)
            self.rate.sleep()
            
        twist.angular.z = 0
        self.cmd_vel_pub.publish(twist)
        
        self.return_mode = True
        self.end_point_reached = False
        self.line_lost_counter = 0
        self.prev_error = 0
        self.integral = 0

    def run(self):
        while not rospy.is_shutdown():
            twist = Twist()
            
            # 1. 장애물 감지
            if self.obstacle_detected:
                twist.linear.x = 0
                twist.angular.z = 0
                self.cmd_vel_pub.publish(twist)
                self.rate.sleep()
                continue

            # 2. 종료 지점 도달
            if self.end_point_reached:
                self.turn_180()
                continue
            
            # ----------------------------------------------
            # [PID 제어 로직]
            # ----------------------------------------------
            
            error = self.right_value - self.left_value
            
            # 라인 이탈/종료 체크 (Threshold 200)
            if self.left_value > 200 and self.right_value > 200:
                if not self.return_mode:
                    self.line_lost_counter += 1
                    if self.line_lost_counter > self.line_lost_limit:
                        self.end_point_reached = True
                error = 0 
            else:
                self.line_lost_counter = 0

            # PID 계산
            p_out = self.Kp * error
            
            self.integral += error
            # Anti-windup
            if self.integral > 1000: self.integral = 1000
            if self.integral < -1000: self.integral = -1000
            i_out = self.Ki * self.integral
            
            d_out = self.Kd * (error - self.prev_error)
            
            output_angular = p_out + i_out + d_out
            self.prev_error = error

            # 명령 발행
            twist.angular.z = output_angular
            twist.linear.x = max(0.05, self.base_speed - abs(output_angular) * 0.1)

            self.cmd_vel_pub.publish(twist)
            
            # rospy.loginfo(f"Err:{error:.0f} Ang:{output_angular:.2f} v:{twist.linear.x:.2f}")
            
            self.rate.sleep()

if __name__ == '__main__':
    try:
        tracer = LineTracer()
        tracer.run()
    except rospy.ROSInterruptException:
        pass