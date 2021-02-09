import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys
import pathlib
import time
sys.path.append(str(pathlib.Path(__file__).parent.absolute()))
import ComHandler
class SBL23XX(Node):
    def __init__(self):
        super().__init__('SBL23XX')
        self.roboteq = ComHandler.SerialHandler()
        if self.roboteq.connect('/dev/ttyACM0'):
            print("Connected!")
        else:
            print("Not Connected!!")

        self.cmdVel = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmdVelCallback,
            10
        )
        self.cmdVel
        self.robotLength = 398.89
        self.wheelRadius = 92.5

    def cmdVelCallback(self, msg):
        LV = msg.linear.x
        AV = msg.angular.z
        Vl = ((2*LV)+(AV*self.robotLength))/(self.wheelRadius*2)
        Vr = ((2*LV)-(AV*self.robotLength))/(self.wheelRadius*2)
        self.roboteq.dualMotorControl(Vl*300000, Vr*300000)
        print("Left Speed = ", Vl*300000, "\tRight Speed = ", Vr*300000)

def main(args=None):
    rclpy.init(args=args)
    print('Hi from roboteq.')
    sbl = SBL23XX()
    try:
        while True:
            time.sleep(0.1)
            rclpy.spin(sbl)
    except KeyboardInterrupt:
        print("Exiting")

    sbl.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()
