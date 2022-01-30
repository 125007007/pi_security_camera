#Import necessary libraries
from flask import Flask, render_template, Response
''' This is the BEST Motion Detection Algoritim I've had yet. Feb 26 2021'''
import os, datetime, shutil, cv2, time, threading, logging, csv
import numpy as np


#Initialize the Flask app
app = Flask(__name__)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


def motion_detection():
    ''' Change sdthresh to suit camera and conditions,
     10 is usually within the threshold range.
     8 seems to work with pi HQ camera'''
    sdThresh = 8
    # Set up cv font
    font = cv2.FONT_HERSHEY_SIMPLEX

    def distMap(frame1, frame2):
        '''outputs pythagorean distance between two frames'''
        frame1_32 = np.float32(frame1)
        frame2_32 = np.float32(frame2)
        diff32 = frame1_32 - frame2_32
        norm32 = np.sqrt(diff32[:,:,0]**2 + diff32[:,:,1]**2 + diff32[:,:,2]**2)/np.sqrt(255**2 + 255**2 + 255**2)
        dist = np.uint8(norm32*255)
        return dist

    def print_date_time():
        '''Updates current date and time on to video'''
        CURR_TIME = time.asctime()
        cv2.putText(frame_save,str(CURR_TIME),(900,25),font, 0.8, (0,255,0),2, cv2.LINE_AA)
        #cv2.putText(frame2,"Enter to pause. Hold ESC to quit.",(10,470), font, 0.6,(255,255,255),1)

    def dt_file_name():
        global file_name
        # sets file name to current date and time to the nearest second
        current_time = datetime.datetime.now().time() # date and time with microseconds
        file_name = current_time #- datetime.timedelta(microseconds=date_and_time.microsecond) # without microseconds
    def file_stuff():
        file_stuff.save_dir = os.getcwd() + '/Snapshots'
        file_name = datetime.datetime.now().time()
        file_stuff.img_name =("Test_1-"+str(file_name)+str(".png"))

    # Capture video stream.
    cap = cv2.VideoCapture(-1)
    # lets camera warm up
    time.sleep(3)

    _, frame1 = cap.read()
    _, frame2 = cap.read()

    while(True):

        try:
            _, frame3 = cap.read()
            rows, cols, _ = np.shape(frame3)
            dist = distMap(frame1, frame3)

        except:
            print("Camera not found.")
            exit(0)

        frame1 = frame2
        frame2 = frame3
        # file name setting
        dt_file_name()
        # Apply Gaussian smoothing.
        mod = cv2.GaussianBlur(dist, (9,9), 0)
        # Apply thresholding.
        _, thresh = cv2.threshold(mod, 100, 255, 0)
        # Calculate st dev test.
        _, stDev = cv2.meanStdDev(mod)

        frame_save = cv2.flip(frame2, -1)
        #frame_save = frame2
        # If motion dectected.
        if stDev > sdThresh:
            print("Motion detected")
            file_stuff()
            cv2.putText(frame_save,"MD", (0,25),font, 0.8, (0,255,0),2, cv2.LINE_AA)
            print_date_time()
            # Save jpg.
            #cv2.imwrite(file_stuff.save_dir + '/{}'.format(file_stuff.img_name), frame_save)
            #print("saved", file_stuff.img_name)
        print_date_time()

        # Live Preview
        cv2.imshow('Live Video', frame_save)
        k = cv2.waitKey(30) & 0xff
        #once you inter Esc capturing will stop
        if k == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

def gen_frames(frame):  
    while True: 
        success, frame = camera.read()  # read the camera frame
        frame = cv2.flip(frame, 0)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
                   # concat frame one by one and sh ow result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    motion_detection()
    app.run(host="0.0.0.0", port='80', debug=False, threaded=True)
