import paramiko
import os

def sftp_upload_dir(sftp, local_dir, remote_dir):
    """ Recursively upload a directory using SFTP. """
    try:
        sftp.mkdir(remote_dir)  # Create remote directory
    except IOError:
        pass  # Ignore if the directory already exists

    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = remote_dir + "/" + item

        if os.path.isdir(local_path):  # If it's a directory, recurse
            sftp_upload_dir(sftp, local_path, remote_path)
        else:  # If it's a file, upload
            sftp.put(local_path, remote_path)
            print(f"Uploaded {local_path} -> {remote_path}")

# Define server details
first_server = "sole"
first_server_user = "nikos"

second_server = "127.0.0.1"
second_server_user = "ubuntu"
remote_file_path = "/home/ubuntu/TransProc/test/unifico-loop"
local_file_path = "aarch64/"

# Connect to the first server
ssh1 = paramiko.SSHClient()
ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
	# Connect using key-based authentication
    ssh1.connect(first_server, username=first_server_user)
    print(f"Connected to {first_server}")

    # Open a new SSH session to the second server from inside the first server
    transport = ssh1.get_transport().open_channel("direct-tcpip", (second_server, 5556), ("", 0))

    # Authenticate with the second server
    ssh2 = paramiko.Transport(transport)
    ssh2.connect(username=second_server_user, password='asdfqwer')

	# Start SFTP session
    sftp = paramiko.SFTPClient.from_transport(ssh2)

	# Perform the recursive upload
    sftp_upload_dir(sftp, local_file_path, remote_file_path)

    print(f"Directory {local_file_path} transferred successfully to {second_server}:{remote_file_path}")

    # Close SFTP session
    sftp.close()
    ssh2.close()

except Exception as e:
        print(f"Error: {e}")

finally:
        ssh1.close()
