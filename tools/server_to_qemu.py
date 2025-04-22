import paramiko
import os
import argparse

FIRST_SERVER_USER = "nikos"
SECOND_SERVER = "127.0.0.1"
SECOND_SERVER_USER = "ubuntu"


def log(message):
    """Log messages to the console."""
    print(f"[TransportWrapper] {message}")


class TransportWrapper:
    """
    A wrapper around a paramiko.Transport object to handle SSH connections from a local server, to a remote server, using an intermediate server as a jump host.
    """

    def __init__(self, first_server, second_server_port, password):
        log("Initializing...")
        # Connect to the first server
        ssh1 = paramiko.SSHClient()
        ssh1.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect using key-based authentication
            ssh1.connect(first_server, username=FIRST_SERVER_USER)
            log(f"Connected to {first_server}")

            # Open a new SSH session to the second server from inside the first server
            transport = ssh1.get_transport().open_channel(
                "direct-tcpip", (SECOND_SERVER, second_server_port), ("", 0)
            )

            # Authenticate with the second server
            ssh2 = paramiko.Transport(transport)
            ssh2.connect(username=SECOND_SERVER_USER, password=password)

            # Create a command executor for the second server
            self.executor = TransportCommandExecutor(ssh2)

            # Start SFTP session
            self.sftp = paramiko.SFTPClient.from_transport(ssh2)

            self.ssh1 = ssh1
            self.ssh2 = ssh2
            log("Successful initialization.")

        except Exception as e:
            print(f"Transport initialization error: {e}")

    def run(self, remote_file_path, local_file_path):
        try:
            log(
                f"Running with remote path: {remote_file_path} and local path: {local_file_path}"
            )
            # Perform the recursive upload
            if os.path.isfile(local_file_path):
                # If it's a file, upload it directly
                sftp_upload_file(self.sftp, local_file_path, remote_file_path)
            elif os.path.isdir(local_file_path):
                # If it's a directory, upload it recursively but remove the image files first
                self.executor.exec(f"rm -f {remote_file_path}/*.img")
                sftp_upload_dir(self.sftp, local_file_path, remote_file_path)
            else:
                raise ValueError(
                    f"Local path {local_file_path} is neither a file nor a directory."
                )

            log(
                f"Directory {local_file_path} transferred successfully to {SECOND_SERVER}:{remote_file_path}"
            )

        except Exception as e:
            print(f"Transfer error: {e}")

    def close(self):
        """Close the SFTP session and transport."""
        log("Closing connections.")
        if hasattr(self, "sftp"):
            self.sftp.close()
        self.ssh2.close()
        self.ssh1.close()


class TransportCommandExecutor:
    def __init__(self, transport: paramiko.Transport):
        self.transport = transport

    def exec(self, command: str, timeout=None):
        """
        Execute a command over the transport and return (stdout, stderr, exit_status).
        """
        channel = self.transport.open_session()
        if timeout:
            channel.settimeout(timeout)

        log(f"Executing command:{command}")
        channel.exec_command(command)

        exit_status = channel.recv_exit_status()
        stdout = channel.makefile("rb", -1).read().decode()
        stderr = channel.makefile_stderr("rb", -1).read().decode()
        log(f"Exit code: {exit_status}")
        log(f"STDOUT:{stdout}\n")
        log(f"STDERR:{stderr}\n")

        channel.close()
        return stdout, stderr, exit_status


def sftp_upload_dir(sftp, local_dir, remote_dir):
    """Recursively upload a directory using SFTP."""
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
            # Get original file's permission bits
            original_mode = (
                os.stat(local_path).st_mode & 0o777
            )  # mask to get just the permission bits
            sftp.put(local_path, remote_path)
            # Apply the same mode to the remote file
            sftp.chmod(remote_path, original_mode)
            log(f"Uploaded {local_path} -> {remote_path}")


def sftp_upload_file(sftp, local_file, remote_dir):
    """Upload a file using SFTP."""
    remote_file = os.path.join(remote_dir, os.path.basename(local_file))
    # Get original file's permission bits
    original_mode = (
        os.stat(local_file).st_mode & 0o777
    )  # mask to get just the permission bits
    sftp.put(local_file, remote_file)
    # Apply the same mode to the remote file
    sftp.chmod(remote_file, original_mode)
    log(f"Uploaded {local_file} -> {remote_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Transfer directory to a nested remote server over SSH."
    )
    parser.add_argument(
        "first_server",
        type=str,
        help="Hostname or IP of the first server (e.g., 'sole')",
    )
    parser.add_argument(
        "second_server_port", type=int, help="Port of the second server (e.g., 5555)"
    )
    parser.add_argument(
        "remote_file_path",
        type=str,
        help="Remote path to upload to on the second server",
    )
    parser.add_argument(
        "local_file_path", type=str, help="Local directory path to upload"
    )
    parser.add_argument(
        "--password-file",
        type=str,
        default="pass.txt",
        help="Path to file containing password",
    )

    args = parser.parse_args()

    try:
        with open(args.password_file, "r") as f:
            password = f.readline().strip()
    except Exception as e:
        print(f"Failed to read password from {args.password_file}: {e}")
        exit(1)

    transport_wrapper = TransportWrapper(
        args.first_server, args.second_server_port, password
    )
    transport_wrapper.run(args.remote_file_path, args.local_file_path)
    transport_wrapper.close()
