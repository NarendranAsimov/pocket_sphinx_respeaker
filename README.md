# pocket_sphinx_respeaker
to get data (vad, doa ) from respeaker and publish in ros topics


this will also publish audio data in sphinx_data topic   
``` 
roslaunch pocketsphinx continuous.launch dict:=/home/asimov/IRA_V2_ws/src/pocketsphinx/demo/voice_cmd.dic gram:=/home/asimov/IRA_V2_ws/src/pocketsphinx/demo/voice_cmd rule:=move2 kws:=/home/asimov/IRA_V2_ws/src/pocketsphinx/demo/heysaya.kwlist grammar:=voice_cmd   
```

this package will give audio as string of specified buffer size in ros topic ...(audio node)

and it also detects keyword and then its gives audio for voice control speech recognition. (kws node) based on kwlist

asr node will give the voice commands based on grammar model 




automatic speech threshold tuninig for kwlist 
https://medium.com/@PankajB96/automatic-tuning-of-keyword-spotting-thresholds-a27256869d31

```
python set_kws_threshold.py /home/asimov/IRA_V2_ws/src/pocketsphinx/demo/voice_cmd.dic /home/asimov/IRA_V2_ws/src/pocketsphinx/demo/voice_cmd.kwlist
```
