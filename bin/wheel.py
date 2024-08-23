import evdev
from evdev import UInput
from evdev import ecodes as e

device = None
for path in evdev.list_devices():
    dev = evdev.InputDevice(path)
    if 'mouse' in dev.name.lower():
        capabilities = dev.capabilities()
        if e.REL_WHEEL in capabilities.get(e.EV_REL, []):
            device = dev
            break
if device is None:
    raise RuntimeError("No mouse found that has a wheel.")
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
