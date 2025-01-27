import paramiko
from posixpath import join, split, splitext


class SSH_client():
    def __init__(self,
                 username,
                 password,
                 address,
                 port):
        self.username = username
        self.password = password
        self.address = address
        self.port = port

    def check_connection(self):
        while not self.ftp_t.is_active():
            print("Try to reestablish connection")
            self.connect_to_ftp()

    def connect_to_ftp(self):
        try:
            self.ftp_t = paramiko.Transport(
                (self.address, self.port))
            self.ftp_t.connect(username=self.username, password=self.password)
            self.ftp_sftp = paramiko.SFTPClient.from_transport(self.ftp_t)
            return True
        except:
            print("Connection failed")
            return False

    def CloseConnectionToFTP(self):
        try:
            self.ftp_t.close()
            print("FTP connection closed")
        except:
            print("No FTP to close")

    def connect_to_ssh(self, port=None):
        try:
            self.ssh_c.exec_command('ls')
            return
        except:
            print("no SSH connection")

        if port is None:
            port = self.port

        self.ssh_c = paramiko.SSHClient()
        self.ssh_c.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)
        self.ssh_c.connect(
            self.address,
            port,
            username=self.username,
            password=self.password)

    def send_ssh_command(self, command, sudo=False, max_tries=100):
        success = False
        currtries = 0
        while (not success) and (currtries < max_tries):
            try:
                if sudo:
                    command = "sudo -S -p '' " + command
                stdin, stdout, stderr = self.ssh_c.exec_command(command)
                if sudo:
                    stdin.write(self.pword + "\n")
                    stdin.flush()
                success = True
            except:
                currtries += 1
                self.connect_to_ssh()

        return stdin, stdout, stderr

    def close_connection(self):
        try:
            self.ssh_c.close()
        except:
            pass

    def mkdir_p(self, remote, is_dir=False):
        """
        emulates mkdir_p if required.
        sftp - is a valid sftp object
        remote - remote path to create.
        """
        dirs_ = []
        if is_dir:
            dir_ = remote
        else:
            dir_, basename = split(remote)
        while len(dir_) > 1:
            dirs_.append(dir_)
            dir_, _ = split(dir_)
        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_)  # For a remote path like y/x.txt
        while len(dirs_):
            dir_ = dirs_.pop()
            try:
                self.ftp_sftp.stat(dir_)
            except FileNotFoundError:
                print("making ... dir",  dir_)
                self.ftp_sftp.mkdir(dir_)
