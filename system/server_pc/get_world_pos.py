#pip install imutils
#pip install opencv-contrib-python
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import sys
import numpy as np

ACTUAL_MARKER_LENGTH = 53 #mm of actual length of marker
CENTER_OFFSET_X = 10
CENTER_OFFSET_Y = 22

def get_world_pos():
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-t", "--type", type=str,
					default="DICT_ARUCO_ORIGINAL",
					help="type of ArUCo tag to detect")
	args = vars(ap.parse_args())

	# define names of each possible ArUco tag OpenCV supports
	ARUCO_DICT = {
		"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
		"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
		"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
		"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
		"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
		"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
		"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
		"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
		"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
		"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
		"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
		"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
		"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
		"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
		"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
		"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
		"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
		"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
		"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
		"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
		"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
	}

	# verify that the supplied ArUCo tag exists and is supported by OpenCV
	if ARUCO_DICT.get(args["type"], None) is None:
		print("[INFO] ArUCo tag of '{}' is not supported".format(
			args["type"]))
		sys.exit(0)

	# load the ArUCo dictionary and grab the ArUCo parameters
	print("[INFO] detecting '{}' tags...".format(args["type"]))
	arucoDict = cv2.aruco.Dictionary_get(ARUCO_DICT[args["type"]])
	arucoParams = cv2.aruco.DetectorParameters_create()

	# initialize the video stream and allow the camera sensor to warm up
	print("[INFO] starting video stream...")
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

	x=[]
	for i in range(8):
		line=[]
		line.append(0)
		x.append(line)

	y=[]
	for i in range(8):
		line = []
		line.append(0)
		y.append(line)

	square_length=[]

	# loop over the frames from the video stream
	while True:
		# grab the frame from the threaded video stream and resize it
		# to have a maximum width of 1000 pixels
		frame = vs.read()
		frame = imutils.resize(frame, width=1000)
		# detect ArUco markers in the input frame
		(corners, ids, rejected) = cv2.aruco.detectMarkers(frame,
														arucoDict, parameters=arucoParams)

		# verify *at least* one ArUco marker was detected
		if len(corners) > 0 :
			# flatten the ArUco IDs list
			ids = ids.flatten()

			# loop over the detected ArUCo corners
			for (markerCorner, markerID) in zip(corners, ids):
				# extract the marker corners (which are always returned
				# in top-left, top-right, bottom-right, and bottom-left
				# order)
				corners = markerCorner.reshape((4, 2))
				(topLeft, topRight, bottomRight, bottomLeft) = corners
				# convert each of the (x, y)-coordinate pairs to integers
				topRight = (int(topRight[0]), int(topRight[1]))
				bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
				bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
				topLeft = (int(topLeft[0]), int(topLeft[1]))

				# draw the bounding box of the ArUCo detection
				cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
				cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
				cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
				cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)
				# compute and draw the center (x, y)-coordinates of the
				# ArUco marker
				cX = int((topLeft[0] + bottomRight[0]) / 2.0)
				cY = int((topLeft[1] + bottomRight[1]) / 2.0)
				cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
				# draw the ArUco marker ID on the frame
				cv2.putText(frame, str(markerID),
								(topLeft[0], topLeft[1] - 15),
								cv2.FONT_HERSHEY_SIMPLEX,
								0.5, (0, 255, 0), 2)

				#print('id' ,markerID, topRight)

				x[markerID-1].append(topRight[0])
				y[markerID-1].append(topRight[1])

				square_length.append(abs(topRight[0]-topLeft[0]))

			if min(len(x[0]), len(x[1]), len(x[2]), len(x[3]), len(x[4]), len(x[5]),
				len(x[6]), len(x[7])) > 10 and min(len(y[0]), len(y[1]), len(y[2]), 
				len(y[3]), len(y[4]), len(y[5]),len(y[6]), len(y[7])) > 10 :
				break
		
		# show the output frame
		cv2.imshow("Frame", frame)

		key = cv2.waitKey(1) & 0xFF

		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break 

	x1 = np.mean(x[0][1:])
	x2 = np.mean(x[1][1:])
	x3 = np.mean(x[2][1:])
	x4 = np.mean(x[3][1:])
	x5 = np.mean(x[4][1:])
	x6 = np.mean(x[5][1:])
	x7 = np.mean(x[6][1:])

	y1 = np.mean(y[0][1:])
	y2 = np.mean(y[1][1:])
	y3 = np.mean(y[2][1:])
	y4 = np.mean(y[3][1:])
	y5 = np.mean(y[4][1:])
	y6 = np.mean(y[5][1:])
	y7 = np.mean(y[6][1:])

	mean_sq_length = np.mean(square_length)
	actual_sq_length = ACTUAL_MARKER_LENGTH

	scale_coef = actual_sq_length / mean_sq_length

	#scale adjust & offset to center
	x_result = [x1, x2, x3, x4 ,x5, x6, x7]
	for i in range(len(x_result)):
		x_result[i] = int(x_result[i]*scale_coef - CENTER_OFFSET_X )


	y_result = [y1, y2, y3, y4, y5, y6, y7]
	for i in range(len(y_result)):
		y_result[i] = int(y_result[i]*scale_coef - CENTER_OFFSET_Y)


	#the distnce btw x s should be 82
	print(x_result)
	print(y_result)

	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()

	return x_result, y_result