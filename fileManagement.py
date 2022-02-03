import os, shutil
import datetime

class FileManager():

    def __init__(self):
        self.pwd = os.getcwd()
        self.todays_date = datetime.date.today()
        self.new_dir_name = str(self.todays_date)
        # sets the date four days ago
        self.four_days_ago = self.todays_date - datetime.timedelta(days=3)
        self.old_dir_name = str(self.four_days_ago)
        self.fullpath = os.path.join(self.pwd, 'Snapshots')
        # sets path to respective dirs
        self.path_to_old_dir = os.path.join(self.fullpath, self.old_dir_name)
        self.currentDateDir = os.path.join(self.fullpath, self.new_dir_name)

    def createSnapshotsDir(self):
        if not os.path.exists(self.fullpath):
            os.mkdir(self.fullpath)

    def createCurrentDateDir(self):
        if not os.path.exists(self.currentDateDir):
            os.mkdir(self.currentDateDir)

    def removeOldDir(self):
        # checks if a folder with the name of the date four days ago exists
        if os.path.exists(self.path_to_old_dir):
            # remove old dir
            shutil.rmtree(self.path_to_old_dir)