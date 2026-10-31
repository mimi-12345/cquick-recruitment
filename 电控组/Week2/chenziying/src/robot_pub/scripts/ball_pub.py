#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from robot_pub.msg import BallPos
from rcl_interfaces.msg import SetParametersResult

class BallPublisher(Node):
    def __init__(self):
        super().__init__('ball_publisher')
        self.declare_parameter("timer_period", 0.5)
        self.timer_period = self.get_parameter("timer_period").value

        self.publisher_ = self.create_publisher(BallPos, 'ball_pos', 10)
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.count = 0
        self.add_on_set_parameters_callback(self.param_callback)

    def param_callback(self, params):
        for p in params:
            if p.name == "timer_period":
                self.timer_period = p.value
                self.get_logger().info(f"更新周期：{self.timer_period} s")
                self.timer.cancel()
                self.timer = self.create_timer(self.timer_period, self.timer_callback)
        res = SetParametersResult()
        res.successful = True
        return res

    def timer_callback(self):
        msg = BallPos()
        if self.count % 3 == 0:
            msg.id = 1
            msg.x = 2.0
            msg.y = 3.0
        elif self.count % 3 == 1:
            msg.id = 2
            msg.x = 5.5
            msg.y = 8.0
        else:
            msg.id = 3
            msg.x = 9.0
            msg.y = 4.0
        self.publisher_.publish(msg)
        self.get_logger().info(f'发布：id={msg.id}, x={msg.x}, y={msg.y}')
        self.count += 1

def main(args=None):
    rclpy.init(args=args)
    ball_publisher = BallPublisher()
    rclpy.spin(ball_publisher)
    ball_publisher.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

