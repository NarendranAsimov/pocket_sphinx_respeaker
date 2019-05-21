import pyaudio
import wave
import numpy as np

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2
# run getDeviceInfo.py to get index
RESPEAKER_INDEX = 6  # refer to input device id
CHUNK = 1024
RECORD_SECONDS = 5


p = pyaudio.PyAudio()

stream = p.open(
            rate=RESPEAKER_RATE,
            format=p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,frames_per_buffer=1024,)
            # input_device_index=RESPEAKER_INDEX,)

print("* recording")

frames0 = []

frames1 = []
frames2 = []
frames3 = []
frames4 = []
frames5 = []
for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    # extract channel 0 data from 6 channels, if you want to extract channel 1, please change to [1::6]
    # for j in range(0,3):
    #     a = np.fromstring(data,dtype=np.int16)[j::6]
    #     # frames[j].append(a.tostring())
    #     frames[j][i]= a.tostring()
    a = np.fromstring(data, dtype=np.int16)[0::6]
    frames0.append(a.tostring())
    a = np.fromstring(data, dtype=np.int16)[1::6]
    frames1.append(a.tostring())
    a = np.fromstring(data, dtype=np.int16)[2::6]
    frames2.append(a.tostring())
    a = np.fromstring(data, dtype=np.int16)[3::6]
    frames3.append(a.tostring())
    a = np.fromstring(data, dtype=np.int16)[4::6]
    frames4.append(a.tostring())
    a = np.fromstring(data, dtype=np.int16)[5::6]
    frames5.append(a.tostring())
print("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

for i in range(0,6):
    WAVE_OUTPUT_FILENAME = "output" + str(i) +".wav"
    print(WAVE_OUTPUT_FILENAME)
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    if i == 0:
        wf.writeframes(b''.join(frames0))
    if i == 1:
        wf.writeframes(b''.join(frames1))
    if i == 2:
        wf.writeframes(b''.join(frames2))
    if i == 3:
        wf.writeframes(b''.join(frames3))
    if i == 4:
        wf.writeframes(b''.join(frames4))
    if i == 5:
        wf.writeframes(b''.join(frames5))
    wf.close()

