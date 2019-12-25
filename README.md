# facerecognition_based_AttendanceSystem
This project is an easy implementation of face recognition application to identify people and mark their in and out enties through a camera frame into database.
<br />Python's dlib model, Face_Recognition is a simple command line tool used to make face embeddings (a 128 dimensional vector space where images of
the same person are near to each other).
<br />
<br />
![alt text](https://github.com/Shivam0403/facerecognition_based_AttendanceSystem/blob/master/exe.jpeg)
<br />
## Requirements & Installation:
* python3
* python virtual environment
  * pip3 intall virtualenv
* python face_recognition
  * pip3 intall face_recognition
* mysql connector*
  * pip3 install mysql-connector-python
* OpenCV
  * pip3 install opencv-python
* numpy
  * pip3 install numpy
<br />

## File Description:
* capture_faceEncodings.py:
  * this file take 10 images of person in front of frame, q is to be pressed to capture image.
  * It takes name and 4 digit ref_id of person.
  * face embedding of each image is save in pickle file.
* attendance_system.py:
  * this file compares each frame and outputs frame with rectangle box and identified face.
  * if face is not identified it outputs "unknown".
  * Database is updated for in and out of identified person after 30 sec interval.
  * For each month new database is created.
