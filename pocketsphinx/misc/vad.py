from tuning import Tuning
import usb.core
import usb.util
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
#print dev
if dev:
    Mic_tuning = Tuning(dev)
    print Mic_tuning.is_voice()
    Mic_tuning.set_vad_threshold(15.0)
    while True:
        try:
            # print Mic_tuning.read('GAMMAVAD_SR')
            print(Mic_tuning.read('SPEECHDETECTED'),Mic_tuning.is_voice())
            # print Mic_tuning.is_voice()
            time.sleep(0.05)
        except KeyboardInterrupt:
            break
