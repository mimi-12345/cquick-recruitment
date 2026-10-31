#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from robot_pub.msg import BallPos
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class TurtleFollowBall(Node):
    def __init__(self):
        super().__init__('turtle_follow_ball')
        # 发布速度
        self.pub_twist = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # 订阅球位置
        self.sub_ball = self.create_subscription(
            BallPos, 'ball_pos', self.ball_callback, 10)
        # 订阅乌龟自身pose
        self.sub_pose = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

        self.turtle_pose = None
        self.ball_dict = {}
        self.target_list = [1,2,3]
        self.current_target_idx = 0
        self.arrive_threshold = 0.5

    def ball_callback(self, msg):
        self.ball_dict[msg.id] = (msg.x, msg.y)

    def pose_callback(self, msg):
        self.turtle_pose = msg
        self.control_logic()

    def control_logic(self):
        if self.turtle_pose is None:
            return
        # 必须集齐3个球坐标才开始运动
        if len(self.ball_dict) < 3:
            return

        target_id = self.target_list[self.current_target_idx]
        tar_x, tar_y = self.ball_dict[target_id]
        cur_x = self.turtle_pose.x
        cur_y = self.turtle_pose.y
        cur_theta = self.turtle_pose.theta

        dx = tar_x - cur_x
        dy = tar_y - cur_y
        distance = math.hypot(dx, dy)
        target_angle = math.atan2(dy, dx)
        angle_diff = target_angle - cur_theta
        # 角度归一化 -pi ~ pi
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))

        twist = Twist()
        if distance < self.arrive_threshold:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.pub_twist.publish(twist)
            self.get_logger().info(f"✅到达球{target_id}，实际坐标({cur_x:.2f},{cur_y:.2f})，误差:{distance:.2f}")
            self.current_target_idx += 1
            if self.current_target_idx >= len(self.target_list):
                self.get_logger().info("🏁全部三个点走完！")
                return
        else:
            # 先转角度，角度小了再前进
            if abs(angle_diff) > 0.2:
                twist.angular.z = 0.6 * angle_diff
                twist.linear.x = 0.0
            else:
                twist.angular.z = 0.3 * angle_diff
                twist.linear.x = 0.8 * distance
        self.pub_twist.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = TurtleFollowBall()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
