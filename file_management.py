import os, time, shutil
import datetime
from time import sleep

def init():
    init.pwd = os.getcwd()
    init.todays_date = datetime.date.today()
    init.new_dir_name = str(init.todays_date)
    # sets the date four days ago
    init.four_days_ago = init.todays_date - datetime.timedelta(days=4)
    init.old_dir_name = str(init.four_days_ago)
    #print(init.old_dir_name) # for dev perposes
    init.fullpath = os.path.join(init.pwd, 'Snapshots')
    # sets path to respective dirs
    init.path_to_old_dir = os.path.join(init.fullpath, init.old_dir_name)
    init.new_dir_path = os.path.join(init.fullpath, init.new_dir_name)


def create_snapshots_dir():
    if not os.path.exists(init.fullpath):
        print("Creating: {}".format(init.fullpath))
        os.mkdir(init.fullpath)
        if os.path.exists(init.fullpath):
            print("The path - {} is a directory".format(init.fullpath))
    elif os.path.exists(init.fullpath):
        print("The path - {} is a directory".format(init.fullpath))

def create_current_date_dir():
    if not os.path.exists(init.new_dir_path):
        print("Creating: {}".format(init.new_dir_path))
        os.mkdir(init.new_dir_path)
        if os.path.exists(init.new_dir_path):
            print("The path - {} is a directory".format(init.new_dir_path))
    elif os.path.exists(init.new_dir_path):
        print("The path - {} is a directory".format(init.new_dir_path))

while True:

    init()
    create_snapshots_dir()
    create_current_date_dir()


def file_management():
    
	def current_date_dir():

		if os.path.exists(init.fullpath):

			os.chdir(init.fullpath)
			if not os.path.exists(init.new_dir_path):
				os.mkdir(init.new_dir_name)
				#save clips here
			elif os.path.exists(init.new_dir_path):
				os.chdir(init.new_dir_path)

	def old_dir():
		# checks if a folder with the name of the date four days ago exists
		if os.path.exists(init.path_to_old_dir):
			print("Removing old dir")
			shutil.rmtree(init.fullpath + '/{}'.format(init.old_dir_name))

	def check_snapshots_dir():
		#print(os.getcwd()) # dev perposes
		if not os.path.exists(init.fullpath):
			#time.sleep(1)
			#print("Snapshots is Not a dir")
			os.mkdir(init.fullpath)
			#print(os.getcwd()) # dev perposes
		elif os.path.exists(init.fullpath):
			os.chdir(init.fullpath)

	def restart_dir_checking():
		if os.getcwd() != init.pwd:
			os.chdir(init.pwd)