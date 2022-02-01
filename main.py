#Import necessary libraries
from flask import Flask, render_template, Response, jsonify
''' This is the BEST Motion Detection Algoritim I've had yet. Feb 26 2021'''
import os, datetime, shutil, cv2, time, threading, sys
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


def motion_detection():
    #try:
    nightThres = 40
    global stream_frame, lock, last_motion
    # Create a VideoCapture object
    #cap = cv2.VideoCapture('rtsp://admin:"Hmit2eyrlic9+%q@192.168.20.103:554//h264Preview_01_sub')
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # uncomment when run on pi
    # set to True if camera is upside down
    cam_upside_down = False
    cap.set(3, 1280)
    cap.set(4, 720)

    def print_date_time(frame):
        '''Updates current date and time on to video'''
        CURR_TIME = time.asctime()
        cv2.putText(frame,str(CURR_TIME),(290,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)			#cv2.putText(frame2,"Enter to pause. Hold ESC to quit.",(10,470), font, 0.6,(255,255,255),1)

    def light_measurer(frame):
        #global image_brightness
        light_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        H, S, V = cv2.split(light_frame)
        image_brightness = round(V.mean(), 1)
        #print(image_brightness)
        #cv2.putText(frame1,"Brightness: {}".format(image_brightness), (10,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)
        return image_brightness


    def dt_file_name():
        #global file_name
        # sets file name to current date and time to the nearest second
        file_name = datetime.datetime.now().time() # date and time with microseconds
        return file_name
    
    while(True):

        # Capture frame-by-frame
        # This method returns True/False as well
        # as the video frame.
        try:
            ret, frame1_upside_down = cap.read()
            ret, frame2_upside_down = cap.read()

            # Filps camera if upside down
            if cam_upside_down is True:
                frame1 = cv2.flip(frame1_upside_down, -1)
                frame2 = cv2.flip(frame2_upside_down, -1)

            elif cam_upside_down is False:
                frame1 = frame1_upside_down
                frame2 = frame2_upside_down

            
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5,5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            #edged = cv2.Canny(dilated, 30, 200)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            #contours, hierarchy = cv2.findContours(fg_mask_bb,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)[-2:]
            areas = [cv2.contourArea(c) for c in contours]


            if light_measurer(frame1) > nightThres:
                areaThres = 4000
                cv2.putText(frame1, "Using Day Thres", (20,55),font, 0.8, (0,255,0),1, cv2.LINE_AA)
            elif light_measurer(frame1) < nightThres:
                areaThres = 450
                cv2.putText(frame1, "Using Night Thres", (20,55),font, 0.8, (0,255,0),1, cv2.LINE_AA)

            for c in contours:
                area = cv2.contourArea(c)

                if area > areaThres:
                    infoLog.info(f'Motion detected - Area: {area}')
                    cv2.drawContours(frame1, c, -1, (0, 255, 0), 2)
                    (x, y, w, h) = cv2.boundingRect(c)
                    #cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    print_date_time(frame2)
                    #light_measurer()
                    # initial time of motion Detected
                    init_time = time.time()
                    # Find the largest moving object in the image
                    max_index = np.argmax(areas)

                    # Draw the bounding box
                    cnt = contours[max_index]
                    area_real = cv2.contourArea(cnt)
                    cv2.putText(frame2, "Area is: {}".format(area_real), (20,80),font, 0.4, (0,255,0),1, cv2.LINE_AA)
                    cv2.putText(frame2,"Brightness: {}".format(light_measurer(frame2)), (10,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)
                    #cv2.putText(frame1,"MD", (0,20),font, 0.8, (0,255,0),2, cv2.LINE_AA)
                    
                    img_name =("snapshot-"+str(dt_file_name())+str(".png"))
                    #print(save_dir)
                    #cv2.imwrite(init.todays_dir_path + '/{}'.format(img_name), frame1)
                    last_motion = datetime.datetime.now()
                    infoLog.info(f"saved {img_name}")
                    with lock:
                        stream_frame = frame2.copy()
            print_date_time(frame2)
            with lock:
                stream_frame = frame2.copy()
            # Display the resulting frame
            #cv2.imshow('frame',frame1)
            #cv2.imshow('diff',diff)
            #cv2.imshow('gray',gray)
            #cv2.imshow('blur',blur)
            #cv2.imshow('thresh',thresh)
            #cv2.imshow('dilated',dilated)

            # If "q" is pressed on the keyboard,
            # exit this loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
       
        except Exception as e:
                errorLog.exception("Exception occurred")
                sys.exit()
# Close down the video stream
    cap.release()
    cv2.destroyAllWindows()

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
        motion_thread = threading.Thread(target=motion_detection)
        #motion_thread.daemon = True
        motion_thread.start()
        infoLog.info("Starting motion thread")
        app.run(host="0.0.0.0", port='80', debug=False, threaded=True)
        infoLog.info("Starting web server")
    except Exception as e:
        errorLog.exception("Exception occurred")
        sys.exit()


    
