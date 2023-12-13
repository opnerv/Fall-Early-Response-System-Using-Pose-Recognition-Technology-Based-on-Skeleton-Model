import cv2	# OPENCV 사용
import mediapipe as mp	# 미디어파이프 사용
from picamera2 import Picamera2	# 카메라 사용을 위하여 사용
from Focuser import Focuser	# Focuser.py을 사용하기 위함
import numpy as np	
import time
import os
import sys
import argparse

cv2.startWindowThread()	# 카메라 화면 창을 스레드
cam = Picamera2()	# Picamera2를 사용해서 카메라 오픈
cam.configure(cam.create_preview_configuration(main={"format" : 'RGB888', "size" : (1280, 720)}))	# 컬러로 출력, 화면은 1280X720 사이즈로 출력
cam.start()	# 화면 오픈

focuser = Focuser(1) # i2c 인터페이스 활성화를 위해서 인자를 1로 줌
step = 90	# 초기, 끝낼 때 모터 값 초기화를 위한 변수
step2 = 60
motor_step = 4	# 좌표 트래킹을 할 때 마다의 모터를 어느 정도 움직이게 할지 정하는 값
motor_step2 = 1
motor_step3 = 5
focuser.set(Focuser.OPT_MOTOR_Y,focuser.get(Focuser.OPT_MOTOR_Y) + step)	# 모터의 초기값 설정

distance = 0.03	# 움직임을 감지할 때 민감하게 반응하게 할지 정하는 값. 값이 낮을수록 움직임에 민감하게 반응함 0.055
distance1 = 0.1
distance2 = 0.15
distance3 = 0.09
LEFT_SHOULDER_X = 0.0	# 왼쪽 어깨의 X좌표를 초기화
LEFT_SHOULDER_Y = 0.0
RIGHT_SHOULDER_Y = 0.0
fall_count = 0
pic_count = 0

mp_drawing = mp.solutions.drawing_utils	# 25~26 : 미디어파이프 포즈 모델을 그리기 위한 준비 작업
mp_pose = mp.solutions.pose

with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
	
	while True:
		im = cam.capture_array()
		image = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
		
		results = pose.process(image)
		IMAGE = image.copy()
		mp_drawing.draw_landmarks(IMAGE, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
		
		if results.pose_landmarks is not None:
			current_shoulder_left = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
			current_shoulder_right = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
			current_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
			current_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
			
			if current_shoulder_left.x < LEFT_SHOULDER_X - distance:	# 왼쪽 방향 트래킹
				focuser.set(Focuser.OPT_MOTOR_X,focuser.get(Focuser.OPT_MOTOR_X) + motor_step)
				cv2.putText(IMAGE, "LEFT-SHOULDER-LEFT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
			
			elif current_shoulder_left.x > LEFT_SHOULDER_X + distance:	# 오른쪽 방향 트래킹
				focuser.set(Focuser.OPT_MOTOR_X,focuser.get(Focuser.OPT_MOTOR_X) - motor_step)
				cv2.putText(IMAGE, "LEFT-SHOULDER-RIGHT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
				
			elif current_shoulder_right.y > RIGHT_SHOULDER_Y + distance2:	# 떨어지는게 빠를 시 작동
				cv2.rectangle(IMAGE, (400, 0), (640, 100), (0, 255, 255), -1)
				fall_count = 1
				start_time = time.localtime().tm_sec
				
			
				
			
					
			elif (abs(current_knee.y - current_hip.y) > distance2) and fall_count == 1:
				end_time = time.localtime().tm_sec
				time_diff = end_time - start_time
				
				if time_diff < 2:
					cv2.rectangle(IMAGE, (400, 0), (640, 100), (0, 0, 255), -1)
					fall_count = 0
					
					cv2.imwrite("image{}.jpg".format(pic_count), IMAGE)
					pic_count += 1
				
				else:
					fall_count = 0
					
			LEFT_SHOULDER_X = current_shoulder_left.x
			LEFT_SHOULDER_Y = current_shoulder_left.y
			RIGHT_SHOULDER_Y = current_shoulder_right.y
			
			cv2.imshow("Camera", IMAGE)
		
			if cv2.waitKey(1) == 27:
				focuser.set(Focuser.OPT_MOTOR_Y,focuser.get(Focuser.OPT_MOTOR_Y) - step2)
				break
	
	cv2.destoryAllWindows()

