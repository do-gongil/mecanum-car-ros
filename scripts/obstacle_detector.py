#!/usr/bin/env python3.8

import rospy
from sensor_msgs.msg import Range
from std_msgs.msg import Bool

class ObstacleDetector:
    def __init__(self):
        rospy.init_node('obstacle_detector', anonymous=True)
        
        # 초음파 센서 구독
        self.front_sub = rospy.Subscriber('/ultrasonic/front', Range, self.front_callback)
        self.rear_sub = rospy.Subscriber('/ultrasonic/rear', Range, self.rear_callback)
        
        # 장애물 상태 퍼블리셔
        self.obstacle_pub = rospy.Publisher('/obstacle_status', Bool, queue_size=10)
        
        self.front_distance = float('inf')
        self.rear_distance = float('inf')
        
        self.detection_threshold = 0.30  # 30cm
        
        self.rate = rospy.Rate(10)  # 10Hz
        
    def front_callback(self, msg):
        self.front_distance = msg.range
    
    def rear_callback(self, msg):
        self.rear_distance = msg.range
    
    def run(self):
        while not rospy.is_shutdown():
            obstacle_msg = Bool()
            
            # 전방 또는 후방 30cm 이내 장애물 감지
            if self.front_distance < self.detection_threshold or \
               self.rear_distance < self.detection_threshold:
                obstacle_msg.data = True
                rospy.logwarn(f"Obstacle! Front: {self.front_distance:.2f}m, Rear: {self.rear_distance:.2f}m")
            else:
                obstacle_msg.data = False
            
            self.obstacle_pub.publish(obstacle_msg)
            self.rate.sleep()

if __name__ == '__main__':
    try:
        detector = ObstacleDetector()
        detector.run()
    except rospy.ROSInterruptException:
        pass