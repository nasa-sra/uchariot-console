import os
import paramiko

import src.UI.ConsoleOutput as ConsoleOutput

USERNAME = "uchariot"
PASSWORD = "123456"


class SSHConnection:

    def __init__(self):
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = "0.0.0.0"

    def connect(self, host):
        if self.client.get_transport() is not None:
            if self.client.get_transport().is_active():
                return
        # ConsoleOutput.log('SSH connecting to: ' + host)
        self.host = host
        self.client.connect(
            host, username=USERNAME, password=PASSWORD, banner_timeout=1
        )
        # self.sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())

    def send_cmd(self, cmd):
        ConsoleOutput.log(f"(ssh) {USERNAME}@{self.host}:~$ {cmd}")
        _stdin, _stdout, _stderr = self.client.exec_command("sudo -S -p '' " + cmd)
        _stdin.write(PASSWORD + "\n")
        _stdin.flush()
        output = _stdout.read().decode("utf-8")
        # ConsoleOutput.log(f'{output}')

    def send_path(self, filePath):
        self.sftp = self.client.open_sftp()
        self.sftp.put(
            filePath,
            f"/home/uchariot/uchariot-base/build/paths/{os.path.basename(filePath)}",
        )
        self.sftp.close()

    def close(self):
        self.sftp.close()
        self.client.close()


conn = SSHConnection()

if __name__ == "__main__":
    conn.connect("10.93.24.5")
    conn.send_cmd("ls")
    conn.close()
