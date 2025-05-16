# Speed-Vehicle-Detection

to execute code of prototype 1: streamlit run app.py
<br> This should display to QR code after uploading input.mp4 video with the output of protype 2 model which uses Yolo v8 for improvments

The 2nd protype as we mentioned in presentation to better enhance speed detection is in the 2 files:

<br> YOLO_TRAIN.ipynb
<br> YOLOv8.ipynb

<br> You can run these into google colabs - as that is what we created them in. 

<br> However, for the first protype, make sure to have these files: tracker.py, SpeedRadar.py, app.py, and the sample.mp4 videos. Then aftering using "streamlit run app.py" on the command line, it should take you to a streamlit local host page and there you can play around with the speed limit and buffer sliders on the left side, and then drag/upload the "sample.mp4" file in. Then, after processing, it shoukd return the processed video as well as a QR code generated leading to the 2nd protype output - which was created through the 2 google colab files mentioned earlier. 

Link to the full input video of the large file (too big to upload on Github) as an traffic4.mp4 file: https://drive.google.com/file/d/1nxEclEAx0jUsXp8MBQkVgB3j777viYJ6/view?usp=drive_link

