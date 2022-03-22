#Import necessary libraries
from flask import Flask, render_template, Response, jsonify
import os, cv2, time, threading, sys
import numpy as np
# import custom modules
from logger import SetupLogger

#Initialize the Flask app
app = Flask(__name__)
lock = threading.Lock()
stream_frame = None
last_motion = 'No motion has being detected yet'

# Info Logger
infoLog = SetupLogger.setup_logger('infoLogger', os.path.join(os.getcwd(), 'infoLog.log'))
# Error Logger 
errorLog = SetupLogger.setup_logger('errorLogger', os.path.join(os.getcwd(), 'errorLog.log'))

# Motion Detection Function
def get_frames():
    global stream_frame, lock, last_motion
    # Create a VideoCapture object
    cap = cv2.VideoCapture(3)

    while True:
        ret, frame = cap.read()

        with lock:
            stream_frame = frame
        
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
                
    # Close down the video stream 
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

# Web Server Functions
def gen_frames():  
    # grab global references to the output frame and lock variables
	global stream_frame, lock
	# loop over frames from the output stream
	while True:
		# wait until the lock is acquired
		with lock:
			# check if the output frame is available, otherwise skip
			# the iteration of the loop
			if stream_frame is None:
				continue
			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", stream_frame)
			# ensure the frame was successfully encoded
			if not flag:
				continue
		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n') 

@app.route('/')
def index():
    #global last_motion

    #data = { 'last_motion': last_motion}
    return render_template('index.html')

@app.route('/lastMotion', methods=['POST'])
def lastMotion():
    global last_motion
    return jsonify(last_motion)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == "__main__":
    
    try:
        # start motion detection thread
        motion_thread = threading.Thread(target=get_frames)
        motion_thread.daemon = True
        motion_thread.start()
        infoLog.info("Starting motion thread")
        app.run(host="0.0.0.0", port='80', debug=False, threaded=True)
        infoLog.info("Starting web server")
    except Exception as e:
        errorLog.exception("Exception occurred")
        sys.exit()

