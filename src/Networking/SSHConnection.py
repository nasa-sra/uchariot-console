# src/Networking/SSHConnection.py
import os
import paramiko

import src.UI.ConsoleOutput as ConsoleOutput

USERNAME = "uchariot"
PASSWORD = "123456"


class SSHConnection:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = "0.0.0.0"
        self.sftp = None  # <- initialize to avoid AttributeError

    def connect(self, host):
        # If transport already active, don't reconnect
        if self.client.get_transport() is not None and self.client.get_transport().is_active():
            return
        ConsoleOutput.log(f"SSH connecting to: {host}")
        self.host = host
        self.client.connect(host, username=USERNAME, password=PASSWORD, banner_timeout=1)
        # do NOT require an SFTP session at connect time; open it lazily in send_path()

    def send_cmd(self, cmd, use_sudo=True, timeout=None):
        """
        Execute a command and return (stdout, stderr).
        Setting use_sudo=True will attempt to run with sudo using the stored PASSWORD.
        """
        prefix = "sudo -S -p '' " if use_sudo else ""
        ConsoleOutput.log(f"(ssh) {USERNAME}@{self.host}:~$ {cmd}")
        _stdin, _stdout, _stderr = self.client.exec_command(prefix + cmd, timeout=timeout)
        if use_sudo:
            # write password and flush for sudo
            _stdin.write(PASSWORD + "\n")
            _stdin.flush()

        out = _stdout.read().decode("utf-8", errors="ignore")
        err = _stderr.read().decode("utf-8", errors="ignore")
        if out:
            ConsoleOutput.log(out.strip())
        if err:
            ConsoleOutput.log(f"(ssh err) {err.strip()}")
        return out, err

    def send_path(self, filePath, remote_dir="/home/uchariot/uchariot-base/build/paths"):
        """
        Upload a file to remote_dir; opens sftp lazily and keeps it open for reuse.
        """
        if self.sftp is None:
            # open a new SFTP session
            self.sftp = self.client.open_sftp()

        remote_path = f"{remote_dir}/{os.path.basename(filePath)}"
        ConsoleOutput.log(f"(sftp) putting {filePath} -> {self.host}:{remote_path}")
        self.sftp.put(filePath, remote_path)
        # do not close sftp here if you expect multiple transfers; close will be handled in close()

    def close(self):
        """
        Close sftp (if it exists) and close the SSH client.
        This guards against AttributeError when sftp was never opened.
        """
        if self.sftp is not None:
            try:
                self.sftp.close()
            except Exception as e:
                ConsoleOutput.log(f"Error closing SFTP: {e}")
            finally:
                self.sftp = None

        try:
            self.client.close()
        except Exception as e:
            ConsoleOutput.log(f"Error closing SSH client: {e}")


# expose a single connection instance (your code expects conn)
conn = SSHConnection()

if __name__ == "__main__":
    conn.connect("10.93.24.5")
    out, err = conn.send_cmd("ls", use_sudo=False)
    print("OUT:", out)
    conn.close()
