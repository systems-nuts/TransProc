import paramiko
import os
import argparse

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


def sftp_upload_file(sftp, local_file, remote_dir):
    """ Upload a file using SFTP. """
    remote_file = os.path.join(remote_dir, os.path.basename(local_file))
    sftp.put(local_file, remote_file)
    print(f"Uploaded {local_file} -> {remote_file}")


def main(first_server, second_server_port, remote_file_path, local_file_path, password):
    first_server_user = "nikos"
    second_server = "127.0.0.1"
    second_server_user = "ubuntu"

    # Connect to the first server
    ssh1 = paramiko.SSHClient()
    ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect using key-based authentication
        ssh1.connect(first_server, username=first_server_user)
        print(f"Connected to {first_server}")

        # Open a new SSH session to the second server from inside the first server
        transport = ssh1.get_transport().open_channel("direct-tcpip", (second_server, second_server_port), ("", 0))

        # Authenticate with the second server
        ssh2 = paramiko.Transport(transport)
        ssh2.connect(username=second_server_user, password=password)

        # Start SFTP session
        sftp = paramiko.SFTPClient.from_transport(ssh2)

        # Perform the recursive upload
        if os.path.isfile(local_file_path):
            # If it's a file, upload it directly
            sftp_upload_file(sftp, local_file_path, remote_file_path)
        elif os.path.isdir(local_file_path):
            sftp_upload_dir(sftp, local_file_path, remote_file_path)
        else:
            raise ValueError(f"Local path {local_file_path} is neither a file nor a directory.")

        print(f"Directory {local_file_path} transferred successfully to {second_server}:{remote_file_path}")

        # Close SFTP session
        sftp.close()
        ssh2.close()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        ssh1.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transfer directory to a nested remote server over SSH.")
    parser.add_argument("first_server", type=str, help="Hostname or IP of the first server (e.g., 'sole')")
    parser.add_argument("second_server_port", type=int, help="Port of the second server (e.g., 5555)")
    parser.add_argument("remote_file_path", type=str, help="Remote path to upload to on the second server")
    parser.add_argument("local_file_path", type=str, help="Local directory path to upload")
    parser.add_argument("--password-file", type=str, default="pass.txt", help="Path to file containing password")

    args = parser.parse_args()

    try:
        with open(args.password_file, "r") as f:
            password = f.readline().strip()
    except Exception as e:
        print(f"Failed to read password from {args.password_file}: {e}")
        exit(1)

    main(args.first_server, args.second_server_port, args.remote_file_path, args.local_file_path, password)
