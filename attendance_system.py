import face_recognition
import cv2
import numpy as np
import glob
import time
import csv
import pickle
import mysql.connector
import datetime


del_time=30   #seconds



################################################# makes table of current month if not exixt
m_y = [datetime.datetime.now().strftime("%m_%Y")]    #month year

table_name=["Attendance_"+m_y[0]]

connection = mysql.connector.connect(host='localhost',
											database='ATTENDANCE',
											user='shivam',
											password='555554444')

sql = """CREATE TABLE IF NOT EXISTS %s(
         ref_id VARCHAR(4), 
         name VARCHAR(25),
         time_now VARCHAR(24),
         in_out VARCHAR(3))""" % table_name[0]

cursor = connection.cursor()
result = cursor.execute(sql)
connection.commit()
print("Record inserted successfully")
cursor.close()
##############################################################################  read value from file

f=open("ref_name.pkl","rb")
ref_dictt=pickle.load(f)         #ref_dict=ref vs name
f.close()

f=open("ref_embed.pkl","rb")
embed_dictt=pickle.load(f)      #embed_dict- ref  vs embedding 
f.close()

############################################################################  encodings and ref_ids 
known_face_encodings = []  #encodingd of faces
known_face_names = []	   #ref_id of faces



for ref_id , embed_list in embed_dictt.items():
	for embed in embed_list:
		known_face_encodings +=[embed]
		known_face_names += [ref_id]

#######################################  dict of ref vs (time,in/out)
ref_time=dict()
for i in ref_dictt:
	ref_time[i]=(0,0)    #  time , out->0 or in->1


last_rec=[""]

###################################### Update database
def send(ref,ref_time):


	if m_y[0] != datetime.datetime.now().strftime("%m_%Y"):     #if month changed
		m_y[0]=datetime.datetime.now().strftime("%m_%Y")        #updating variable
		table_name[0]="Attendance_"+m_y[0]                      #updating table name
		connection = mysql.connector.connect(host='localhost',
													database='ATTENDANCE',
													user='shivam',
													password='555554444')

		sql = """CREATE TABLE IF NOT EXISTS %s(					#making new table in database
		         ref_id VARCHAR(4), 
		         name VARCHAR(25),
		         time_now VARCHAR(24),
		         in_out VARCHAR(3))""" % table_name[0]

		cursor = connection.cursor()
		result = cursor.execute(sql)
		connection.commit()
		print("Record inserted successfully")
		cursor.close()
	####################################### when face is recognized 
	if ref!="Unknown"  and time.time()-ref_time[ref][0]>=del_time:    #check for unknown and if time difference is more then del_time

		ref_time[ref]=(time.time(),ref_time[ref][1]^1)               #updating the dict
		name=ref_dictt[ref]
		time_now = time.asctime( time.localtime(time.time()) )
		if ref_time[ref][1]==0:
			in_out="OUT"
		else:
			in_out="IN"
		last_rec[0]=name+" "+in_out+" "+datetime.datetime.now().strftime("%X")
		fields=[ref,name,time_now,in_out]
		with open(r'csv.csv', 'a') as f:
			writer = csv.writer(f)
			writer.writerow(fields)
		fields=tuple(fields)
		connection = mysql.connector.connect(host='localhost',		#updating database
											database='ATTENDANCE',
											user='shivam',
											password='555554444')
		mySql_insert_query = "INSERT INTO "+ table_name[0] +""" (ref_id, name,time_now,in_out) 
							VALUES 
							(%s, %s, %s, %s) """
		cursor = connection.cursor()
		result = cursor.execute(mySql_insert_query,fields)
		connection.commit()
		print("Record inserted successfully")
		cursor.close()

	return ref_time    												#returning database


#############################################################frame capturing from camera and face recognition
video_capture = cv2.VideoCapture(0)
# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True  :
	# Grab a single frame of video
	ret, frame = video_capture.read()

	# Resize frame of video to 1/4 size for faster face recognition processing
	small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

	# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	rgb_small_frame = small_frame[:, :, ::-1]

	# Only process every other frame of video to save time
	if process_this_frame:
		# Find all the faces and face encodings in the current frame of video
		face_locations = face_recognition.face_locations(rgb_small_frame)
		face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

		face_names = []
		for face_encoding in face_encodings:
			# See if the face is a match for the known face(s)
			matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
			name = "Unknown"

			# # If a match was found in known_face_encodings, just use the first one.
			# if True in matches:
			#     first_match_index = matches.index(True)
			#     name = known_face_names[first_match_index]

			# Or instead, use the known face with the smallest distance to the new face
			face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
			best_match_index = np.argmin(face_distances)
			if matches[best_match_index]:
				name = known_face_names[best_match_index]
			face_names.append(name)

	process_this_frame = not process_this_frame


	# Display the results
	for (top, right, bottom, left), name in zip(face_locations, face_names):
		# Scale back up face locations since the frame we detected in was scaled to 1/4 size
		top *= 4
		right *= 4
		bottom *= 4
		left *= 4

		ref_time=send(name,ref_time)              #updating in database

		cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

		# Draw a label with a name below the face
		cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
		font = cv2.FONT_HERSHEY_DUPLEX
		cv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
	font = cv2.FONT_HERSHEY_DUPLEX
	cv2.putText(frame, last_rec[0], (6,20), font, 1.0, (0,0 ,0), 1)

	# Display the resulting imagecv2.putText(frame, ref_dictt[name], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
	cv2.imshow('Video', frame)

	# Hit 'q' on the keyboard to quit!
	if cv2.waitKey(1) & 0xFF == ord('q'):
		# t.cancel()
		break

		# break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()