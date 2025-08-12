# debug_pyglet_controllers.py
import pyglet
import time

mgr = pyglet.input.ControllerManager()
print("Initial controllers:", mgr.get_controllers())

# Try enumerating a few times (hotplug)
for i in range(10):
    controllers = mgr.get_controllers()
    print(f"[{i}] controllers len={len(controllers)}")
    for c in controllers:
        print(" -", c.name, vars(c))
    time.sleep(0.5)
