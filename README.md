# UChariot Console
A GUI driver console for microchariot

## Running
After cloning the repo, install the dependencies with
`pip install customtkinter pyglet pynput`  
Then start the console with
`python main.py`  
> For some laptops, using controller may not be supported. If you get errors about joysticks or the console app doesn't respond, try commenting out lines 32-37 in TeleopUI.py

## Usage
To connect, enter the pi's IP and click connect. You should then receive telemetry from the robot, note that the runtime should be incrementing, indicating a stable connection. The tabs represent different controllers, switching to another tab will change the robot controller. That controller will then be running, but no motors will be commanded until the robot is enabled.  

### Disabled
This is mostly a placeholder controller for when the robot is disabled.  
* Load Config Button - Reloads the configuration file from uchariot-base/config/robotConfig.xml

### Teleop
This is used for manually driving the robot.
* Controller Connection Status - Tells whether a game controller is connected. The controller must have been connected before starting the driver console.
* Input Method Selector - This can be toggled between controller arcade (one stick), split arcade (two stick), and keyboard (WASD keys).

### Pathing
This is used to run paths on the robot.
> To run a path, copy the path file to the robot, set the robot facing north, reset the heading, set the robot in its starting position and heading, reset pose, start path, check telemetry for expected commands, then enable. 
* Path Name Box - The file name of the path on the robot to run.
* Start Button - Starts path.
* Stop Button - Stops path.
* Reset Pose - Sets localization origin to the current position.
* Reset Heading - Sets applies offset to gyro to zero heading.
* Select File - Allows for selecting local file for transfer.
* Deploy - Copies file to robot.

### Following
This is used to follow a target, like a person.

## Summon
This is used to summon the robot to a person.
* Target latitude/longitude - Input the target's approximate GPS location.
* Summon - Command the robot to move to the target.

