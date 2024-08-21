from evdev import InputDevice, UInput, ecodes
import subprocess

right_button_pressed = False

def handle_event(event, ui):
    global right_button_pressed

    if event.type == ecodes.EV_KEY:
        if event.code == ecodes.BTN_RIGHT:
            if event.value == 1:
                # Right Button Pressed
                right_button_pressed = True
            elif event.value == 0:
                # Right Button Released
                if right_button_pressed:
                    # Right Button was pressed and released without other actions
                    ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 1)  # Simulate right button press
                    ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 0)  # Simulate right button release
                    ui.syn()
                right_button_pressed = False
        elif event.code == ecodes.BTN_MIDDLE:
            if event.value == 1 and right_button_pressed:
                # Right Button + XButton2 (RButton & XButton2)
                subprocess.run(["xdotool", "key", "ctrl+w"])
        else:
            # Pass through all other key events
            ui.write(event.type, event.code, event.value)
            ui.syn()
    elif event.type == ecodes.EV_REL:
        if event.code == ecodes.REL_WHEEL:
            if event.value == 1 and right_button_pressed:
                # Right Button + Wheel Up (RButton & WheelUp)
                subprocess.run(["xdotool", "key", "Page_Up"])
            elif event.value == -1 and right_button_pressed:
                # Right Button + Wheel Down (RButton & WheelDown)
                subprocess.run(["xdotool", "key", "Page_Down"])
        else:
            # Pass through all other relative events
            ui.write(event.type, event.code, event.value)
            ui.syn()
    else:
        # Pass through all other events
        ui.write(event.type, event.code, event.value)
        ui.syn()

device = InputDevice('/dev/input/event13')
print(f"Listening for events on {device.name}")

ui = UInput()

with device.grab_context():  # get exclusive access
    for event in device.read_loop():
        handle_event(event, ui)
