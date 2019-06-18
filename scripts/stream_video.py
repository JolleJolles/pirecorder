# import opencv and the Videostream package
import cv2
from animrec.videoin import VideoIn

# Open a video stream: cam = "rpi" will open the native raspberry
# pi camera, while cam = 0 will open the natively attached camera or webcam
vid = VideoIn(resolution=(1920, 1080)).start()

# Run videostream until user presses ESC
while True:

    # Get frame from the videostream
    frame = vid.read()

    # Show the frame
    cv2.imshow('window', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Stop the videostream and close the video window
vid.stop()
cv2.destroyAllWindows()
cv2.waitKey(1)
