# Script for verifying local files in Pepper's memory

import pysftp

myHostname = "192.168.1.91"
myUsername = "nao"
myPassword = "Pepper"


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

with pysftp.Connection(host = myHostname, username = myUsername, password = myPassword, cnopts = cnopts) as sftp:
    print "Connection succesfully established ... "

    # Switch to a remote directory
    sftp.cwd('/var/www/vhosts/')

    # Obtain structure of the remote directory '/var/www/vhosts'
    directory_structure = sftp.listdir_attr()
    # print(directory_structure)
    for attr in directory_structure:
        print attr.filename, attr

    if sftp.exists("/home/nao/med.png"):
        print("image exists")
    elif sftp.exists("/home/nao/med.png"):
        print("image does exist")
    else:
        print("image does not exist")
