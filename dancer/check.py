"""
https://sourceforge.net/projects/xautomation/
https://github.com/autopilot-rs/autopy
"""
import autopy


def hello_world():
    autopy.alert.alert("Hello, world")
    autopy.mouse.smooth_move(1, 1)


hello_world()
