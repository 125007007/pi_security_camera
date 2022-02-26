#Import necessary libraries
from flask import Flask, render_template, Response, jsonify
import os, datetime, shutil, cv2, time, threading, sys, json
import numpy as np
# import custom modules
from logger import SetupLogger
from fileManagement import FileManager


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
def motion_detection():
    #try:
    nightThres = 40
    global stream_frame, lock, last_motion
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # open json config file and set vars to what is in json file
    f = open("config.json")
    data = json.load(f)
    width = data["resolution"]["width"]
    height = data["resolution"]["height"]
    day_areaThres = data["day_areaThres"]
    night_areaThres = data["night_areaThres"]
    cam_upside_down = data["cam_upside_down"]
    cap.set(3, width)
    cap.set(4, height)

    def print_date_time(frame):
        '''Updates current date and time on to video'''
        CURR_TIME = time.asctime()
        cv2.putText(frame,str(CURR_TIME),(290,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)

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
        file_name = str(datetime.datetime.now().time()) # date and time with microseconds
        file_name = list(file_name)
        if len(file_name) >= 12:
            file_name[2] = '_'
            file_name[5] = '_'
            file_name[8] = '_'
            file_name = ''.join(file_name)
            #infoLog.info(len(file_name))
            return file_name
        else:
            raise Exception(f'Length of file_name - {file_name} not long enough.')
    
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
            #print(areas)

            if light_measurer(frame1) > nightThres:
                areaThres = day_areaThres
                cv2.putText(frame2, "Using Day Thres", (10,55),font, 0.8, (0,255,0),1, cv2.LINE_AA)
            elif light_measurer(frame1) < nightThres:
                areaThres = night_areaThres
                cv2.putText(frame2, "Using Night Thres", (10,55),font, 0.8, (0,255,0),1, cv2.LINE_AA)

            cv2.putText(frame2,"Brightness: {}".format(light_measurer(frame2)), (10,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)

            # only save the largest area of motion
            if len(contours) > 0:
                c = max(contours, key = cv2.contourArea)
                #for c in contours:
                (x, y, w, h) = cv2.boundingRect(c)
                area = cv2.contourArea(c)

                if area < areaThres:
                    continue
                infoLog.info(f'Using - {areaThres}')
                infoLog.info(f'Motion detected - Area: {area}')
                cv2.drawContours(frame2, c, -1, (0, 255, 0), 2)
                #cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 0, 255), 2)
                print_date_time(frame2)
                cv2.putText(frame2, "Area is: {}".format(area), (10,80),font, 0.4, (0,255,0),1, cv2.LINE_AA)
                #cv2.putText(frame2,"Brightness: {}".format(light_measurer(frame2)), (10,25),font, 0.8, (0,255,0),1, cv2.LINE_AA)
                #cv2.putText(frame1,"MD", (0,20),font, 0.8, (0,255,0),2, cv2.LINE_AA)
                img_name =("snapshot-"+str(dt_file_name())+str(".png"))
                #cv2.imwrite(FileManager().currentDateDir + '/{}'.format(img_name), frame2)
                if not cv2.imwrite(os.path.join(FileManager().currentDateDir, img_name), frame2):
                    raise Exception('Could not write image')
                last_motion = datetime.datetime.now()
                infoLog.info(f"saved {img_name}")
            

            print_date_time(frame2)
            with lock:
                stream_frame = frame2
       
        except Exception as e:
                errorLog.exception("Exception occurred")
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


def files():
    while True:
        FileManager().createSnapshotsDir()
        FileManager().createCurrentDateDir()
        FileManager().removeOldDir()
        time.sleep(0.25)

if __name__ == "__main__":
    try:
        # start file manager thread
        fileThread = threading.Thread(target=files)
        fileThread.start()
        infoLog.info("Starting file manager thread")     
    except Exception as e:
        errorLog.exception("Exception occurred")
        sys.exit()
    
    try:
        # start motion detection thread
        motion_thread = threading.Thread(target=motion_detection)
        motion_thread.daemon = True
        motion_thread.start()
        infoLog.info("Starting motion thread")
        app.run(host="0.0.0.0", port='80', debug=False, threaded=True)
        infoLog.info("Starting web server")
    except Exception as e:
        errorLog.exception("Exception occurred")
        sys.exit()


