from tkinter import DoubleVar, IntVar
import threading
import time
import logging
import customtkinter
import pyglet
from datetime import datetime

import src.Networking.UnixConnection as UnixConnection
import src.UI.ConsoleOutput as ConsoleOutput
from pynput.keyboard import Key, KeyCode
import src.KeystrokeListener as KeystrokeListener
from enum import Enum

logging.basicConfig(level=logging.INFO)
PAD = 10

class CtrlMode(Enum):
    ONE_STICK = "One Stick"
    TWO_STICK = "Two Stick"
    KEYBOARD = "Keyboard"

class TeleopUI:
    def __init__(self, parent: customtkinter.CTkTabview):
        self.ID = "Teleop"
        self.parent = parent

        p_tab = self.parent.tab(self.ID)

        # controller management
        self.controllerManager = pyglet.input.ControllerManager()
        self.controller = None

        # GUI widgets (kept your original layout)
        self.controllerLabel = customtkinter.CTkLabel(
            p_tab,
            text="Controller Disconnected",
            text_color="red"
        )
        self.controllerLabel.grid(row=0, column=0, padx=PAD, pady=PAD, sticky="n")

        self.ctrlMode = CtrlMode.TWO_STICK
        self.ctrlModeBtn = customtkinter.CTkButton(
            master=p_tab, text=self.ctrlMode.value, command=self.toggleCtrlMode
        )
        self.ctrlModeBtn.grid(row=1, column=0, padx=PAD, pady=PAD, sticky="n")

        cmdVelLabel = customtkinter.CTkLabel(p_tab, text="Velocity:")
        cmdVelLabel.grid(row=0, column=2, padx=PAD, pady=PAD, sticky="n")

        self.cmdVelValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdVelValue.grid(row=0, column=3, padx=PAD, pady=PAD, sticky="n")

        cmdRotLabel = customtkinter.CTkLabel(p_tab, text="Rotation:")
        cmdRotLabel.grid(row=1, column=2, padx=PAD, pady=PAD, sticky="n")

        self.cmdRotValue = customtkinter.CTkLabel(p_tab, text="")
        self.cmdRotValue.grid(row=1, column=3, padx=PAD, pady=PAD, sticky="n")

        # keyboard callbacks
        KeystrokeListener.listener.addCallback(KeyCode(char='w'), self.forwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='s'), self.backwardKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='a'), self.leftKeyHandler)
        KeystrokeListener.listener.addCallback(KeyCode(char='d'), self.rightKeyHandler)

        # internal state
        self.vel = 0.0
        self.rot = 0.0

        # run a quick initial scan + start periodic rescans for hotplug detection
        self._initial_scan_and_setup()

        # command thread (daemon so it won't prevent program exit)
        self.cmdThread = threading.Thread(target=self.command, daemon=True)
        self.cmdThread.start()

        # ensure UI reflects initial vel/rot
        self.updateLabel()

    # -------------------------
    # Controller scanning / setup
    # -------------------------
    def _try_open_controller(self, ctrl):
        try:
            # Some pyglet controllers require open(); wrap in try/except
            open_fn = getattr(ctrl, "open", None)
            if callable(open_fn):
                open_fn()
            logging.info("Opened controller: %s", getattr(ctrl, "name", repr(ctrl)))
            return True
        except Exception as e:
            logging.warning("Failed to open controller: %s", e)
            return False

    def _set_controller(self, ctrl):
        # this method must run in Tk main thread to safely update widgets
        def _apply():
            self.controller = ctrl
            state = bool(self.controller)
            self.controllerLabel.configure(
                text="Controller Connected" if state else "Controller Disconnected",
                text_color="green" if state else "red"
            )
            if state:
                self._try_open_controller(self.controller)
        try:
            # schedule immediate on main thread
            self.parent.after(0, _apply)
        except Exception:
            # fallback: call directly (if after not available)
            _apply()

    def _initial_scan_and_setup(self):
        # Quick initial scan (allow a few short retries for delayed enumeration)
        controllers = []
        for attempt in range(6):
            try:
                controllers = self.controllerManager.get_controllers()
            except Exception as e:
                logging.warning("get_controllers() failed: %s", e)
                controllers = []
            if controllers:
                break
            time.sleep(0.1)

        if controllers:
            logging.info("Initial controllers found: %s", [c.name for c in controllers])
            self._set_controller(controllers[0])
        else:
            logging.info("No controllers found on init; scheduling rescans")
            # schedule the periodic rescan loop
            try:
                self.parent.after(500, self._rescan)
            except Exception:
                # If after fails for some reason, start a background thread to rescan
                t = threading.Thread(target=self._rescan_background, daemon=True)
                t.start()

    def _rescan(self):
        # Runs in main thread via .after
        try:
            controllers = self.controllerManager.get_controllers()
        except Exception as e:
            logging.warning("Rescan get_controllers() failed: %s", e)
            controllers = []

        if controllers and self.controller is None:
            logging.info("Rescan: controllers found: %s", [c.name for c in controllers])
            self._set_controller(controllers[0])
        elif not controllers and self.controller is not None:
            # controller no longer enumerated
            logging.info("Rescan: controller no longer enumerated, clearing controller")
            self._set_controller(None)

        # schedule next rescan (500 ms)
        try:
            self.parent.after(500, self._rescan)
        except Exception as e:
            logging.warning("Failed to schedule next rescan: %s", e)

    def _rescan_background(self):
        # Background fallback if `after` isn't available; checks periodically
        while not ConsoleOutput.closing:
            try:
                controllers = self.controllerManager.get_controllers()
                if controllers and self.controller is None:
                    logging.info("Background rescan found controllers, setting controller")
                    self._set_controller(controllers[0])
                elif not controllers and self.controller is not None:
                    logging.info("Background rescan: controller gone, clearing")
                    self._set_controller(None)
            except Exception as e:
                logging.warning("Background rescan error: %s", e)
            time.sleep(0.5)

    # -------------------------
    # Main command loop
    # -------------------------
    def command(self):
        # a simple counter used to occasionally force a rescan from this thread,
        # in case main-thread rescan fails (keeps hotplug robust)
        counter = 0
        while True:
            if self.controller and self.ctrlMode != CtrlMode.KEYBOARD:
                # Prefer direct attributes provided by pyglet XInput device
                lx = getattr(self.controller, "leftx", None)
                ly = getattr(self.controller, "lefty", None)
                rx = getattr(self.controller, "rightx", None)

                # If attributes are absent, try calling poll() if present (e.g., pygame wrapper)
                if lx is None:
                    poll = getattr(self.controller, "poll", None)
                    if callable(poll):
                        try:
                            poll()
                        except Exception as e:
                            logging.info("Controller poll failed: %s", e)
                    lx = getattr(self.controller, "leftx", 0.0)
                    ly = getattr(self.controller, "lefty", 0.0)
                    rx = getattr(self.controller, "rightx", 0.0)

                try:
                    self.vel = -float(ly or 0.0)
                    if self.ctrlMode == CtrlMode.ONE_STICK:
                        self.rot = float(lx or 0.0)
                    else:
                        self.rot = float(rx or 0.0)
                except Exception as e:
                    logging.warning("Error reading controller axes: %s", e)
                    # if reading fails, clear controller to trigger a rescan
                    self._set_controller(None)

                # schedule label update on main thread
                try:
                    self.parent.after(0, self.updateLabel)
                except Exception:
                    # fallback: call directly
                    self.updateLabel()

            # occasionally force a rescan if we have no controller
            counter += 1
            if counter >= 50:  # roughly every 1 second (0.02 * 50)
                counter = 0
                if self.controller is None:
                    try:
                        controllers = self.controllerManager.get_controllers()
                        if controllers:
                            logging.info("Periodic command-loop rescan found controllers")
                            self._set_controller(controllers[0])
                    except Exception as e:
                        logging.warning("Periodic rescan error: %s", e)

            # send drive command
            try:
                UnixConnection.networking.cmdDrive(self.vel, self.rot)
            except Exception as e:
                logging.warning("cmdDrive failed: %s", e)

            if ConsoleOutput.closing:
                break
            time.sleep(0.02)

    # -------------------------
    # UI helpers (thread-safe)
    # -------------------------
    def updateLabel(self):
        # schedule on main thread to avoid Tkinter thread-safety issues
        def _apply():
            try:
                self.cmdVelValue.configure(text=f"{self.vel:.2f}")
                self.cmdRotValue.configure(text=f"{self.rot:.2f}")
            except Exception as e:
                logging.warning("Failed to update labels: %s", e)
        try:
            self.parent.after(0, _apply)
        except Exception:
            # fallback: call directly
            _apply()

    # -------------------------
    # Control mode toggling
    # -------------------------
    def toggleCtrlMode(self):
        if self.ctrlMode == CtrlMode.ONE_STICK:
            self.ctrlMode = CtrlMode.TWO_STICK
        elif self.ctrlMode == CtrlMode.TWO_STICK:
            self.ctrlMode = CtrlMode.KEYBOARD
        else:
            self.ctrlMode = CtrlMode.ONE_STICK

        # update button text on main thread
        try:
            self.parent.after(0, lambda: self.ctrlModeBtn.configure(text=self.ctrlMode.value))
        except Exception:
            self.ctrlModeBtn.configure(text=self.ctrlMode.value)

    # -------------------------
    # Keyboard handlers
    # -------------------------
    def forwardKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.vel = 0.5 if state else 0.0
        self.updateLabel()

    def backwardKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.vel = -2.0 if state else 0.0
        self.updateLabel()

    def leftKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.rot = -1.0 if state else 0.0
        self.updateLabel()

    def rightKeyHandler(self, state):
        if not self.ctrlMode == CtrlMode.KEYBOARD: return
        self.rot = 1.0 if state else 0.0
        self.updateLabel()
