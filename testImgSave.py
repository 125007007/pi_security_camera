#Import necessary libraries
import os, datetime, cv2, sys
# import custom modules
from fileManagement import FileManager

# test
def dt_file_name():
    #global file_name
    # sets file name to current date and time to the nearest second
    file_name = str(datetime.datetime.now().time()) # date and time with microseconds
    print(file_name)
    file_name = list(file_name)
    file_name[2] = '_'
    file_name[5] = '_'
    file_name[8] = '_'
    file_name = ''.join(file_name)
    print(len(file_name))
    return file_name
    

FileManager().createSnapshotsDir()
FileManager().createCurrentDateDir()
FileManager().removeOldDir()
cap = cv2.VideoCapture(0)
# set to True if camera is upside down
#cam_upside_down = True
#cap.set(3, 1280)
#cap.set(4, 720)


sucess, frame1 = cap.read()

img_name =("snapshot-"+str(dt_file_name())+str(".png"))
#print(save_dir)
#cv2.imwrite(FileManager().currentDateDir + '/{}'.format(img_name), frame2)
cv2.imwrite(os.path.join(FileManager().currentDateDir, img_name), frame1)
    

# Close down the video stream
cap.release()
cv2.destroyAllWindows()
sys.exit()


