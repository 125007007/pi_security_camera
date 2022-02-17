import os, shutil
import datetime
from logger import SetupLogger

class FileManager(object):

    pwd = os.getcwd()
    # Info Logger
    log = SetupLogger.setup_logger('Logger', os.path.join(os.getcwd(), 'fileManagment.log'))
    todays_date = datetime.date.today()
    new_dir_name = str(todays_date)
    # sets the date four days ago
    four_days_ago = todays_date - datetime.timedelta(days=3)
    old_dir_name = str(four_days_ago)
    fullpath = os.path.join(pwd, 'Snapshots')
    # sets path to respective dirs
    path_to_old_dir = os.path.join(fullpath, old_dir_name)
    currentDateDir = os.path.join(fullpath, new_dir_name)

    def createSnapshotsDir():
        if not os.path.exists(FileManager.fullpath):
            FileManager.log.info("Creating Snapshots Directory")
            os.mkdir(FileManager.fullpath)

    def createCurrentDateDir():
        if not os.path.exists(FileManager.currentDateDir):
            FileManager.log.info(f"Creating {FileManager.new_dir_name} Directory")
            os.mkdir(FileManager.currentDateDir)

    def removeOldDir():
        # checks if a folder with the name of the date four days ago exists
        if os.path.exists(FileManager.path_to_old_dir) is True:
            FileManager.log.info(f"Removing {FileManager.old_dir_name} Directory")
            # remove old dir
            shutil.rmtree(FileManager.path_to_old_dir)
