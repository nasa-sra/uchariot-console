from time import time 
import socket
import select
import json
from threading import Thread

import src.UI.ConsoleOutput as ConsoleOutput

ENABLE_SETTLE_MS = 500

class UnixConnection():
    def __init__(self):
        self.sock = None
        self.connecting = False
        self.running = True
        self.connected = False
        self.enabled = False
        self.heading = False
        self.lastEnableCmdTime = 0
        self.lastHeartBeatTime = 0
        self.receiveThread = None

        self.connectCallback = None
        self.packetCallback = None

        self.state = {}

    def asyncConnect(self, host: str, port: int, callback = None):
        if (not self.connecting):
            self.connecting = True
            self.connectThread = Thread(target=self.connect, args=(host, port, callback))
            self.connectThread.start()

    def connect(self, host: str, port: int, callback = None):
            ConsoleOutput.log(f"Connecting to {host}:{port}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            res = self.sock.connect_ex((host, port))
            self.sock.settimeout(0)

            if callback:
                self.connectCallback = callback

            if (res == 0):
                ConsoleOutput.log(f"Connected")
                self.receiveThread = Thread(target=self.receive)
                self.receiveThread.start()
                self.setController('disabled')
            else:
                ConsoleOutput.log(f"Failed to connect, Error {res}")

            self.connecting = False
            self.connected = res == 0
            if callback:
                callback(res == 0)

    def receive(self):
        while self.running:
            readable, writable, errors = select.select([self.sock], [], [], 1)
            if len(readable) > 0 and readable[0] is self.sock and self.running:
                data = self.sock.recv(2**20)

                if len(data) > 0:
                    self.lastHeartBeatTime = int(time() * 1000) # ms
                    if (not self.connected):
                        self.connected = True
                        if self.connectCallback:
                            self.connectCallback(True)
                    self._cacheState(data)

                if self.packetCallback:
                    self.packetCallback(data)

            if (int(time() * 1000) - self.lastHeartBeatTime > 500 and self.connected):
                ConsoleOutput.log("Disconnected")
                self.connected = False
                # Drop the enabled latch on disconnect so a reconnect requires
                # an explicit Enable before the rover can move again.
                self.enabled = False
                # Clear cached telemetry so stale readings don't linger on the
                # UI after the rover goes away.
                self.state = {}
                self.connectCallback(False)

    def _cacheState(self, data):
        packets = data.decode("utf-8", errors="ignore")
        lastPacketPos = packets.rfind('{"robot":')
        if lastPacketPos < 0:
            return
        try:
            parsed = json.loads(packets[lastPacketPos:])
            self.state = parsed.get("robot", {})
        except (json.JSONDecodeError, ValueError):
            pass

    def _voltageMeterValue(self, key):
        try:
            return float(self.state.get("voltageMeter", {}).get(key, 0.0))
        except (AttributeError, TypeError, ValueError):
            return 0.0

    def getVoltage(self):
        return self._voltageMeterValue("voltage")

    def getCurrent(self):
        return self._voltageMeterValue("current")

    def getPower(self):
        return self._voltageMeterValue("power")

    def robotEnabled(self):
        """The robot's own reported enable state, or None when unknown."""
        if not self.connected:
            return None
        if int(time() * 1000) - self.lastEnableCmdTime < ENABLE_SETTLE_MS:
            return None
        value = self.state.get("enabled")
        if not isinstance(value, bool):
            return None
        return value

    def addPacketCallback(self, callback):
        self.packetCallback = callback

    def sendCommand(self, cmdName, data):
        if self.connected:
            self.sock.sendall(f'[{cmdName}] {json.dumps(data)};'.encode())
            # ConsoleOutput.log(f'[{cmdName}] {json.dumps(data)};')

    def enable(self):
        if not self.connected:
            ConsoleOutput.log("Not connected, cannot enable")
            return False
        self.enabled = True
        self.lastEnableCmdTime = int(time() * 1000)
        self.sendCommand('enable', {})
        ConsoleOutput.log(f"Enabling")
        return True

    def disable(self):
        self.enabled = False
        self.lastEnableCmdTime = int(time() * 1000)
        # Explicitly zero the drive command so the robot's stored motor state
        # cannot keep the rover moving after a disable.
        self.cmdDrive(0.0, 0.0)
        self.sendCommand('disable', {})
        ConsoleOutput.log(f"Disabling")

    def reverseHeading(self):
        self.heading = True
        self.sendCommand('reverse', {})
        ConsoleOutput.log(f"Reverse Heading")


    def resetHeading(self): 
        self.heading = False
        self.sendCommand('reset', {})
        ConsoleOutput.log(f"Reset Heading")

    def setController(self, ctr):
        if self.connected:
            data = {"name": ctr}
            self.sendCommand('set_controller', data)
            ConsoleOutput.log(f"Setting controller to {ctr}")

    def cmdDrive(self, vel, rot):
        data = {"velocity": vel, "rotation": rot}
        self.sendCommand('teleop_drive', data)

    def cmdRunPath(self, path):
        data = {"name": path}
        self.sendCommand('run_path', data)
        ConsoleOutput.log(f"Running path {path}")

    def cmdStopPath(self):
        self.sendCommand('stop_path', {})
        ConsoleOutput.log(f"Stopping path")

    def cmdResetHeading(self):
        self.sendCommand('reset_heading', {})
        ConsoleOutput.log(f"Resetting heading")

    def cmdResetPose(self):
        self.sendCommand('reset_pose', {})
        ConsoleOutput.log(f"Resetting pose")

    def loadConfig(self):
        self.sendCommand('load_config', {})
        ConsoleOutput.log(f"Loading config")

    def summon(self, lat, lon):
        data = {"latitude": lat, "longitude": lon}
        self.sendCommand('summon', data)
        ConsoleOutput.log(f"Summoning to {lat}, {lon}")

    def close(self):
        ConsoleOutput.log("Closing Connection")
        self.running = False
        if self.sock:
            self.sock.close()
        if self.receiveThread and self.receiveThread.ident:
            self.receiveThread.join()
                

networking = UnixConnection()