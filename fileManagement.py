import os, shutil, json, datetime
from logger import SetupLogger


class FileManager(object):

# Info Logger
    log = SetupLogger.setup_logger('Logger', os.path.join(os.getcwd(), 'fileManagment.log'))

    def __init__(self):
        self.todays_date = datetime.date.today()
        self.f = open("config.json")
        self.data = json.load(self.f)
        self.f.close()
        if self.data["use_usb_drive"] is True:
            self.pwd = self.data["usb_drive_location"]
        elif self.data["use_usb_drive"] is False:
            self.pwd = os.getcwd()
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
            FileManager.log.info("Creating Snapshots Directory")
            os.mkdir(self.fullpath)

    def createCurrentDateDir(self):
        if not os.path.exists(self.currentDateDir):
            FileManager.log.info(f"Creating {self.new_dir_name} Directory")
            os.mkdir(self.currentDateDir)

    def removeOldDir(self):
        # checks if a folder with the name of the date four days ago exists
        if os.path.exists(self.path_to_old_dir) is True:
            FileManager.log.info(f"Removing {self.old_dir_name} Directory")
            # remove old dir
            shutil.rmtree(self.path_to_old_dir)
