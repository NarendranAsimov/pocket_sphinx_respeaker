#!/usr/bin/python

import os

import rospy
import time
from std_msgs.msg import String, Int16
from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *


#for communicating with respeaker

from tuning import Tuning
import usb.core
import usb.util
import numpy as np

class KWSDetection(object):
    """Class to add keyword spotting functionality"""

    def __init__(self):

        # Initializing publisher with buffer size of 10 messages
        self.pub_ = rospy.Publisher("kws_data", String, queue_size=10)
        # Initalizing publisher for continuous ASR
        self.continuous_pub_ = rospy.Publisher(
            "jsgf_audio", String, queue_size=10)
    
        # initialize node
        rospy.init_node("kws_control")
        # Call custom function on node shutdown
        rospy.on_shutdown(self.shutdown)


        # for detect is speech
        self.count_subs = 0
        self.not_speech=0
        self.dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
        if self.dev:
            self.Mic_tuning = Tuning(self.dev)
        self.speech_end_hysteresis = 0
        self.utt_started = 0
        self.previous_data_buf = []
        self.speech = 0
        # Params

        # File containing language model
        _hmm_param = "~hmm"
        # Dictionary
        _dict_param = "~dict"
        # List of keywords to detect
        _kws_param = "~kws"
        """Not necessary to provide the next two if _kws_param is provided
        Single word which needs to be detected
        """
        _keyphrase_param = "~keyphrase"
        # Threshold frequency of above mentioned word
        _threshold_param = "~threshold"
        # Option for continuous
        self._option_param = "~option"
        self.count_recognized = 0
        # Variable to distinguish between kws list and keyphrase.
        # Default is keyword list
        self._list = True

        self.stop_output = False

        # Setting param values
        if rospy.has_param(_hmm_param):
            self.class_hmm = rospy.get_param(_hmm_param)
            if rospy.get_param(_hmm_param) == ":default":
                if os.path.isdir("/usr/local/share/pocketsphinx/model"):
                    rospy.loginfo("Loading the default acoustic model")
                    self.class_hmm = "/usr/local/share/pocketsphinx/model/en-us/en-us"
                    rospy.loginfo("Done loading the default acoustic model")
                else:
                    rospy.logerr(
                        "No language model specified. Couldn't find defaut model.")
                    return
        else:
            rospy.loginfo("Couldn't find lm argument")

        if rospy.has_param(_dict_param) and rospy.get_param(_dict_param) != ":default":
            self.lexicon = rospy.get_param(_dict_param)
        else:
            rospy.logerr(
                'No dictionary found. Please add an appropriate dictionary argument.')
            return

        if rospy.has_param(_kws_param) and rospy.get_param(_kws_param) != ":default":
            self._list = True

            self.kw_list = rospy.get_param(_kws_param)
        elif rospy.has_param(_keyphrase_param) and \
        rospy.has_param(_threshold_param) and \
        rospy.get_param(_keyphrase_param) != ":default" and \
        rospy.get_param(_threshold_param) != ":default":
            self._list = False

            self.keyphrase = rospy.get_param(_keyphrase_param)
            self.kws_threshold = rospy.get_param(_threshold_param)
        else:
            rospy.logerr(
                'kws cant run. Please add an appropriate keyword list.')
            return

        # All params satisfied. Starting recognizer
        self.start_recognizer()

    def start_recognizer(self):
        """Function to handle keyword spotting of audio"""

        self.config = Decoder.default_config()
        rospy.loginfo("Pocketsphinx initialized")

        # Setting configuration of decoder using provided params
        self.config.set_string('-hmm', self.class_hmm)
        self.config.set_string('-dict', self.lexicon)
        self.config.set_string('-dither', "no")
        self.config.set_string('-featparams', os.path.join(self.class_hmm, "feat.params"))

        if self._list:
            # Keyword list file for keyword searching
            self.config.set_string('-kws', self.kw_list)
        else:
            # In case keyphrase is provided
            self.config.set_string('-keyphrase', self.keyphrase)
            self.config.set_float('-kws_threshold', self.kws_threshold)

        # Set required configuration for decoder
        self.decoder = Decoder(self.config)
        print("hi stupid {}".format(self.decoder.get_search()))
        # Start processing input audio
        # self.decoder.start_utt()
        rospy.loginfo("Decoder started successfully")

        # Subscribe to audio topic
        rospy.Subscriber("sphinx_audio", String, self.process_audio)
        rospy.Subscriber("vad", Int16, self.process_speech)
        rospy.spin()

    def process_speech(self,data):
        # print(data.data)
        self.speech= data.data
    def process_audio(self, data):
        """Audio processing based on decoder config"""
        # For continuous mode
        # print("in")
        self.count_subs += 1
        need_continuous = rospy.has_param(self._option_param)
        if self.utt_started == 0:
            self.previous_data_buf.insert(0,data.data)
            if len(self.previous_data_buf) > 5:
                self.previous_data_buf.pop()
        #check if its speech in respeaker
        # speech = self.Mic_tuning.read('SPEECHDETECTED')
        # if speech == 1:
        #     self.not_speech = 0
        # else:
        #     self.not_speech += 1
        
        if self.speech == 1:
            
            if self.speech_end_hysteresis == 0 :
                
                try:
                    self.decoder.start_utt()
                    rev = self.previous_data_buf.reverse()
                    for i in self.previous_data_buf:
                        self.decoder.process_raw(i, False, False)
                    self.previous_data_buf = []
                    # print("got",self.count_subs)
                    self.utt_started = 1
                except :
                    print("error")
            self.speech_end_hysteresis = 5

        # if self.start_utt == 1:
        #     print("started")
        # else:
        #     print("stropped")
        # Check if keyword detected
        
        if not self.stop_output:
            # Actual processing
            
            if self.speech_end_hysteresis > 0:
                
                self.decoder.process_raw(data.data, False, False)
                self.speech_end_hysteresis -= 1
            if self.utt_started == 1 and self.speech_end_hysteresis == 0:
                
                self.utt_started = 0
                self.decoder.end_utt()
                self.speech_end_hysteresis = 0

            if self.decoder.hyp() != None and self.utt_started == 1:
                rospy.loginfo([(seg.word, seg.prob, seg.start_frame, seg.end_frame)
                               for seg in self.decoder.seg()])
                rospy.loginfo("Detected keyphrase, restarting search")
                seg.word = seg.word.lower() #pylint: disable=undefined-loop-variable
                if self.utt_started == 1:
                    self.decoder.end_utt()
                    self.utt_started = 0
                    self.speech_end_hysteresis = 0
                # Publish output to a topic
                self.pub_.publish(seg.word) #pylint: disable=undefined-loop-variable
                # rate.sleep()
                self.count_recognized +=1
                if need_continuous:
                    print ('INSIDE',self.count_recognized)
                    # self.stop_output = True
                # self.decoder.start_utt()
                # self.start_utt = 1
                self.not_speech = 0
        else:
            self.continuous_pub_.publish(data.data)
        # if self.not_speech > 200 :
        #     self.decoder.end_utt()
        #     # self.decoder.reinit(self.config)
        #     print("resstarted utt")
        #     self.not_speech = 0
        #     self.decoder.start_utt()
        if self.count_subs > 500 and self.utt_started == 0:
            if self.utt_started == 1:
                self.decoder.end_utt()
                self.utt_started = 0
                self.speech_end_hysteresis = 0
            self.decoder.reinit(self.config)
            print("resstarted utt")
            self.not_speech = 0
            self.count_subs = 0
            if self.utt_started == 0:
                self.decoder.start_utt()
                self.utt_started = 1

    @staticmethod
    def shutdown():
        """This function is executed on node shutdown."""
        # command executed after Ctrl+C is pressed
        rospy.loginfo("Stop ASRControl")
        rospy.sleep(1)


if __name__ == "__main__":
    KWSDetection()
