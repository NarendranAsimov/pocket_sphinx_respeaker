#!/usr/bin/env python
import rospy
from tuning import Tuning
import usb.core
import usb.util
import time
from std_msgs.msg import Int16,Float32

class send_params:
    def __init__(self):
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if self.dev:
            self.Mic_tuning = Tuning(self.dev)
        self.vad_pub = rospy.Publisher("vad",Int16,queue_size=1)
        self.doa_pub = rospy.Publisher("Doa", Float32, queue_size=1)
        self.publishers()
    def publishers(self):
        while not rospy.is_shutdown():
            doa = self.Mic_tuning.direction
            speech = self.Mic_tuning.read('SPEECHDETECTED')
            time.sleep(0.05)
            self.vad_pub.publish(speech)
            self.doa_pub.publish(doa)


if __name__ == '__main__':
    rospy.init_node('send_vad_doa', anonymous=True)
    voice = send_params()
    rospy.spin()