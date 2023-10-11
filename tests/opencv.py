import cv2

print(cv2.__version__)


camera = cv2.VideoCapture(0)
print("Setting camera mode")

exp_val = 0

codec = 0x47504A4D # MJPG
camera.set(cv2.CAP_PROP_FPS, 30.0)
camera.set(cv2.CAP_PROP_FOURCC, codec)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
camera.set(cv2.CAP_PROP_EXPOSURE, exp_val)

print("Starting capture")
while(1):
	camera.grab()
	_, im = camera.retrieve(0)
	cv2.imshow(str(cv2.__version__), im)

	k = cv2.waitKey(1) & 0xff
	if k == 27:
		print("exit")
		break

camera.release()
cv2.destroyAllWindows()
