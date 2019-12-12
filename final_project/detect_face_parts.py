# USAGE
# python detect_face_parts.py --shape-predictor shape_predictor_68_face_landmarks.dat --image images/example_01.jpg 

# import the necessary packages
from imutils import face_utils
import numpy as np
import argparse
import imutils
import dlib
import cv2
import math
import rospy
import json
from std_msgs.msg import Float32MultiArray, Empty, String, Int16

def dist(x1,y1,x2,y2):
	return (math.sqrt((x2-x1)**2+(y2-y1)**2))

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

rospy.init_node('project', anonymous=TRUE)

publisher_camera = rospy.Publisher('/project/camera', Float32MultiArray)

cap = cv2.VideoCapture(-1)
# loop over the face detections
while 1:
	ret, image = cap.read()
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
	rects = detector(gray, 1)
	goodface=0
	center=(0,0)
	leyew=0
	reyew=0
	leyelh=0
	leyerh=0
	reyelh=0
	reyerh=0
	r=(0,0)
	l=(0,0)
	h=image.shape[0]
	w=image.shape[0]
	
	for (i, rect) in enumerate(rects):
		
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)
		
		
		#print(shape)
		# loop over the face parts individually
		for (name, (i, j)) in face_utils.FACIAL_LANDMARKS_IDXS.items():
			
			
			#cv2.putText(image, name, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

			# loop over the subset of facial landmarks, drawing the
			# specific face part
			#print (name)
			if ((name == "left_eye") | (name == "right_eye")):

				for (x, y) in shape[i:j]:
					cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
					#print("eyes")
					#print(x,y)
					#print("done")
					
			if (name == "right_eye"):
				#print("right")
				#print(shape[i:j])
				r=(shape[i:j][5][0],shape[i:j][5][1])
				reyew=dist(shape[i:j][0][0],shape[i:j][0][1],shape[i:j][3][0],shape[i:j][3][1])
				reyelh=dist(shape[i:j][1][0],shape[i:j][1][1],shape[i:j][5][0],shape[i:j][5][1])
				reyerh=dist(shape[i:j][2][0],shape[i:j][2][1],shape[i:j][4][0],shape[i:j][4][1])
			if (name == "left_eye"):
				#print("left")
				#print(shape[i:j])
				#(x,y)=shape[i:j][1]
				#cv2.circle(image, (x, y), 1, (255, 0, 0), -1)
				l=(shape[i:j][0][0],shape[i:j][0][1])
				leyew=dist(shape[i:j][0][0],shape[i:j][0][1],shape[i:j][3][0],shape[i:j][3][1])
				leyelh=dist(shape[i:j][1][0],shape[i:j][1][1],shape[i:j][5][0],shape[i:j][5][1])
				leyerh=dist(shape[i:j][2][0],shape[i:j][2][1],shape[i:j][4][0],shape[i:j][4][1])



		
	#print(l,r)
	#print(r[0],r[1])
	if ((r[0]!=0) & (r[1]!=0) & (l[0]!=0) & (l[1]!=0) ):
		#print(l,r)
		
		center=((r[0]+l[0])/2,(r[1]+l[1])/2)
		
		#print(center)
	if ((leyew*.9 <=reyew<=leyew*1.1) & (leyew!=0) & (leyew!=0)):
		if (leyerh*.9 <=reyerh<=leyerh*1.1):
			if (leyelh*.9 <=reyelh<=leyelh*1.1):
				goodface=1
	if (goodface):
		print("good", center)
		msg = Float32MultiArray()
		msg.data=[0.0,0.0]
		if (h*.45 > center[1]):
			if (w*.45>center[0]):
				print("move up +right")
				msg.data=[1.0,1.0]
				
			elif (w*.55<center[0]):		
				print("move up +left ")
				msg.data=[1.0,-1.0]
			else:
				msg.data=[1.0,0.0]
		elif (h*.55<center[1]):
			if (w*.45>center[0]):
				print("move down +right")
				msg.data=[-1.0,1.0]
			if (w*.55<center[0]):		
				print("move down +left ")
				msg.data=[-1.0,-1.0]
			else:
				msg.data=[-1.0,0.0]
		else:
			msg.data=[0.0,0.0]
		
		publisher_camera.publish(msg)
	cv2.imshow("Image", image)
	#cv2.waitKey(0)
	k = cv2.waitKey(30) & 0xff
	if k == 27:
		break
cap.release()
cv2.destroyAllWindows()
