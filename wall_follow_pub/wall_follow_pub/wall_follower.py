import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
        self.pub = self.create_publisher(Twist, '/diff_drive/cmd_vel', 10)
        self.sub = self.create_subscription(
            LaserScan, '/diff_drive/scan', self.cb_scan, 10)

        self.DESIRED_DISTANCE = 3.0
        self.TOLERANCE = 0.3
        self.TURN_SPEED = 0.3
        self.FORWARD_SPEED = 0.5
        self.CORNER_LEFT_TRIGGER = 1.9

        self.in_corner_turn = False
        self.corner_timer = None

    def cb_scan(self, scan: LaserScan):
        if self.in_corner_turn:
            return

        front_scanner = len(scan.ranges) // 2
        front = scan.ranges[front_scanner]

        if math.isnan(front) or front > scan.range_max or front == float('inf'):
            self.get_logger().warn(f"Out of range: {front}")
            return

        cmd = Twist()

        if front < self.CORNER_LEFT_TRIGGER:
            self.in_corner_turn = True
            self.phase = "reverse"
            self.phase_end_time = self.get_clock().now().seconds_nanoseconds()[
                0] + 8  # reverse for 7 secs
            self.corner_timer = self.create_timer(
                0.1, self.perform_corner_maneuver)
            self.get_logger().info(f"CORNER AVOID")
            return

        if front < self.DESIRED_DISTANCE - self.TOLERANCE:
            # Too close = go right
            cmd.linear.x = self.FORWARD_SPEED / 2
            cmd.angular.z = -self.TURN_SPEED
            self.get_logger().info(f"Too close ({front:.2f}), turning RIGHT")
        elif front > self.DESIRED_DISTANCE + self.TOLERANCE:
            # Too far = go left
            cmd.linear.x = self.FORWARD_SPEED / 2
            cmd.angular.z = self.TURN_SPEED / 3
            self.get_logger().info(f"Too far ({front:.2f}), turning LEFT")
        else:
            # Go forward
            cmd.linear.x = self.FORWARD_SPEED
            cmd.angular.z = 0.0
            self.get_logger().info(
                f"Good distance ({front:.2f}), going STRAIGHT")

        self.pub.publish(cmd)

    def perform_corner_maneuver(self):
        now = self.get_clock().now().seconds_nanoseconds()[0]
        cmd = Twist()

        if self.phase == "reverse":
            if now >= self.phase_end_time:
                self.phase = "forward"
                self.phase_end_time = now + 5
                self.get_logger().info("Finished reversing, now driving FORWARD")
                return
            cmd.linear.x = -self.FORWARD_SPEED
            cmd.angular.z = -self.TURN_SPEED
            self.get_logger().info("Reversing right during corner escape")

        elif self.phase == "forward":
            if now >= self.phase_end_time:
                self.get_logger().info("Corner complete")
                self.in_corner_turn = False
                self.corner_timer.cancel()
                return
            cmd.linear.x = self.FORWARD_SPEED / 2
            cmd.angular.z = -self.TURN_SPEED
            self.get_logger().info("Driving forward after corner escape")

        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = WallFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
