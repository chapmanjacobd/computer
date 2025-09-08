#!/usr/bin/python3
import argparse
import sys

import evdev
from evdev import UInput
from evdev import ecodes as e


def get_mice():
    mice = []
    for path in evdev.list_devices():
        dev = evdev.InputDevice(path)
        capabilities = dev.capabilities()
        if e.EV_REL in capabilities and e.REL_WHEEL in capabilities[e.EV_REL]:
            mice.append(dev)
    return mice


def select_mouse(mice):
    if not mice:
        print("No mouse wheels found!")
        exit(1)
    elif len(mice) == 1:
        return mice[0]

    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg:
        if arg.isnumeric():
            return mice[int(arg) - 1]
        else:
            return [dev for dev in mice if arg in dev.name][0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select a mouse device with a scroll wheel.")
    parser.add_argument("device", nargs="?", help="Path to the device (e.g., /dev/input/eventX).")
    args = parser.parse_args()

    if args.device:
        try:
            device = evdev.InputDevice(args.device)
        except evdev.EvdevError:
            mice = get_mice()
            device = select_mouse(mice)
    else:
        mice = get_mice()
        print("Available mice:")
        for i, dev in enumerate(mice):
            print(f"{i + 1}: {dev.name} (path: {dev.path})")
        exit(len(mice))

    if not device:
        print("Device could not be activated", args.device)
        exit(1)
    print(f"Listening for events on {device.name}")

    ui = UInput(
        {
            e.EV_KEY: (
                e.KEY_PAGEUP,
                e.KEY_PAGEDOWN,
                e.BTN_LEFT,
                e.BTN_MIDDLE,
                e.BTN_RIGHT,
                e.BTN_WHEEL,
                e.KEY_SCROLLUP,
                e.KEY_SCROLLDOWN,
                e.KEY_LEFTCTRL,
                e.KEY_W,
            ),
            e.EV_REL: (e.REL_X, e.REL_Y, e.REL_WHEEL),
        }
    )

    right_button_pressed = False
    pressed_action = False

    with device.grab_context():  # get exclusive access
        for event in device.read_loop():
            if event.type == e.EV_KEY:
                if event.code == e.BTN_RIGHT:
                    if event.value == 1:  # Right Button Pressed
                        right_button_pressed = True
                        pressed_action = False
                    elif event.value == 0:  # Right Button Released
                        if pressed_action is False:  # Right Button was pressed and released without other actions
                            ui.write(e.EV_KEY, e.BTN_RIGHT, 1)
                            ui.syn()
                            ui.write(e.EV_KEY, e.BTN_RIGHT, 0)
                            ui.syn()
                        right_button_pressed = False
                elif event.code == e.BTN_MIDDLE:
                    if event.value == 1 and right_button_pressed:
                        ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)  # ctrl+w
                        ui.write(e.EV_KEY, e.KEY_W, 1)
                        ui.write(e.EV_KEY, e.KEY_W, 0)
                        ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
                        ui.syn()
                        pressed_action = True
                    else:  # Middle Click
                        ui.write(event.type, event.code, event.value)
                        ui.syn()
                elif event.code == e.BTN_EXTRA:
                    ui.write(e.EV_KEY, e.KEY_PAGEUP, event.value)
                    ui.syn()
                elif event.code == e.BTN_SIDE:
                    ui.write(e.EV_KEY, e.KEY_PAGEDOWN, event.value)
                    ui.syn()
                else:  # other keys
                    ui.write(event.type, event.code, event.value)
                    ui.syn()
            elif event.type == e.EV_REL:
                if right_button_pressed and event.code == e.REL_WHEEL:
                    if event.value == 1:  # Wheel Up
                        ui.write(e.EV_KEY, e.KEY_PAGEUP, 1)
                        ui.write(e.EV_KEY, e.KEY_PAGEUP, 0)
                    elif event.value == -1:  # Wheel Down
                        ui.write(e.EV_KEY, e.KEY_PAGEDOWN, 1)
                        ui.write(e.EV_KEY, e.KEY_PAGEDOWN, 0)
                    ui.syn()
                    pressed_action = True
                else:
                    ui.write(event.type, event.code, event.value)
                    ui.syn()
            else:
                ui.write(event.type, event.code, event.value)
                ui.syn()
