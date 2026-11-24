#!/usr/bin/python3
import argparse
import errno
import sys
import time

import evdev
from evdev import UInput
from evdev import ecodes as e

# Unique phys so we can tell our own uinput device apart from real mice.  The
# device name and IDs are copied from the source device so compositors such as
# KWin keep applying the user's per-device pointer settings to it.
VIRTUAL_PHYS = "wheel-remap/virtual"

# Keys we synthesize on top of whatever the physical device supports.
SYNTHESIZED_KEYS = (
    e.KEY_PAGEUP,
    e.KEY_PAGEDOWN,
    e.KEY_LEFTCTRL,
    e.KEY_W,
)

HI_RES_PER_DETENT = 120


def get_mice():
    mice = []
    for path in evdev.list_devices():
        try:
            dev = evdev.InputDevice(path)
        except (evdev.EvdevError, OSError):
            continue
        if is_virtual(dev):
            dev.close()
            continue
        rel = set(dev.capabilities().get(e.EV_REL, ()))
        if e.REL_WHEEL in rel or e.REL_WHEEL_HI_RES in rel:
            mice.append(dev)
        else:
            dev.close()
    return mice


def is_virtual(dev):
    return dev.phys == VIRTUAL_PHYS


def has_hi_res(dev):
    return e.REL_WHEEL_HI_RES in dev.capabilities().get(e.EV_REL, ())


def select_mouse(mice, arg):
    if not mice:
        raise LookupError("No mouse wheels found!")
    if arg is None:
        if len(mice) == 1:
            return mice[0]
        raise LookupError("Multiple mice found; specify one")
    if arg.isnumeric():
        index = int(arg)
        if not 1 <= index <= len(mice):
            raise LookupError(f"No mouse {index}; found {len(mice)}")
        return mice[index - 1]
    matches = [dev for dev in mice if arg in dev.name]
    if not matches:
        raise LookupError(f"No mouse matching {arg!r}")
    return matches[0]


def uinput_capabilities(dev):
    """Capabilities for the virtual device, preserving the source device's.

    The kernel drops any event code a device does not advertise, so every key
    and relative axis the physical mouse reports must be declared here or it
    would be lost.
    """
    caps = {
        event_type: tuple(codes)
        for event_type, codes in dev.capabilities(absinfo=True).items()
        if event_type not in (e.EV_SYN, e.EV_FF)
    }
    caps[e.EV_KEY] = tuple(sorted(set(caps.get(e.EV_KEY, ())) | set(SYNTHESIZED_KEYS)))
    caps.setdefault(e.EV_REL, ())
    return caps


def create_uinput(dev):
    info = dev.info
    return UInput(
        uinput_capabilities(dev),
        name=dev.name,
        phys=VIRTUAL_PHYS,
        vendor=info.vendor,
        product=info.product,
        bustype=info.bustype,
        version=info.version,
    )


class WheelRemapper:
    """Turn a mouse event stream into remapped events on ``sink``.

    ``EV_SYN`` frames from the device are forwarded as they arrive, so
    synthesized events are flushed by the following SYN.  Clicks are the
    exception: libinput drops a button press and release that arrive in the
    same frame, so a click is split across two frames with ``sink.syn()``.
    """

    def __init__(self, sink, remap_sides=False, has_hi_res=False):
        self.sink = sink
        self.remap_sides = remap_sides
        self.has_hi_res = has_hi_res
        self.right_pressed = False
        self.pressed_action = False
        self.swallowed_middle = False
        self.hi_res_accum = 0

    def feed(self, event):
        if event.type == e.EV_KEY:
            self._key(event)
        elif event.type == e.EV_REL:
            self._rel(event)
        else:
            self.sink.write(event.type, event.code, event.value)

    def _key(self, event):
        code, value = event.code, event.value

        if code == e.BTN_RIGHT:
            if value == 1:
                self.right_pressed = True
                self.pressed_action = False
                self.hi_res_accum = 0
            elif value == 0:
                if not self.pressed_action:
                    # Right button pressed and released without another action:
                    # emit a plain right click, in two frames.
                    self.sink.write(e.EV_KEY, e.BTN_RIGHT, 1)
                    self.sink.syn()
                    self.sink.write(e.EV_KEY, e.BTN_RIGHT, 0)
                self.right_pressed = False
                self.hi_res_accum = 0
            return

        if code == e.BTN_MIDDLE:
            if self.swallowed_middle:
                if value == 0:
                    self.swallowed_middle = False
                return
            if value == 1 and self.right_pressed:
                self._tap_ctrl_w()
                self.pressed_action = True
                self.swallowed_middle = True
                return
            self.sink.write(event.type, code, value)
            return

        if self.remap_sides and code == e.BTN_EXTRA:
            self.sink.write(e.EV_KEY, e.KEY_PAGEUP, value)
            return

        if self.remap_sides and code == e.BTN_SIDE:
            self.sink.write(e.EV_KEY, e.KEY_PAGEDOWN, value)
            return

        self.sink.write(event.type, code, value)

    def _rel(self, event):
        code, value = event.code, event.value

        if code in (e.REL_WHEEL, e.REL_WHEEL_HI_RES) and self.right_pressed:
            if code == e.REL_WHEEL_HI_RES:
                self._page_hi_res(value)
            elif not self.has_hi_res:
                self._page_presses(value)
            self.pressed_action = True
            return

        self.sink.write(event.type, code, value)

    def _tap_ctrl_w(self):
        self.sink.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)
        self.sink.write(e.EV_KEY, e.KEY_W, 1)
        self.sink.write(e.EV_KEY, e.KEY_W, 0)
        self.sink.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)

    def _page_presses(self, count):
        code = e.KEY_PAGEUP if count > 0 else e.KEY_PAGEDOWN
        for _ in range(abs(count)):
            self.sink.write(e.EV_KEY, code, 1)
            self.sink.write(e.EV_KEY, code, 0)

    def _page_hi_res(self, value):
        self.hi_res_accum += value
        while self.hi_res_accum >= HI_RES_PER_DETENT:
            self.sink.write(e.EV_KEY, e.KEY_PAGEUP, 1)
            self.sink.write(e.EV_KEY, e.KEY_PAGEUP, 0)
            self.hi_res_accum -= HI_RES_PER_DETENT
        while self.hi_res_accum <= -HI_RES_PER_DETENT:
            self.sink.write(e.EV_KEY, e.KEY_PAGEDOWN, 1)
            self.sink.write(e.EV_KEY, e.KEY_PAGEDOWN, 0)
            self.hi_res_accum += HI_RES_PER_DETENT


def wait_for_device(old, delay=1.0):
    """Wait for a disconnected device to come back (same path or phys)."""
    while True:
        time.sleep(delay)
        found = None
        for dev in get_mice():
            if found is None and (dev.path == old.path or (old.phys and dev.phys == old.phys)):
                found = dev
            else:
                dev.close()
        if found is not None:
            return found


def run(device, remap_sides):
    while True:
        try:
            ui = create_uinput(device)
        except (OSError, evdev.UInputError) as exc:
            print(
                f"Cannot create virtual input device: {exc}\n"
                "Check that /dev/uinput is writable (input group or udev rule).",
                file=sys.stderr,
            )
            return 1

        with ui:
            remapper = WheelRemapper(ui, remap_sides=remap_sides, has_hi_res=has_hi_res(device))
            try:
                with device.grab_context():  # get exclusive access
                    for event in device.read_loop():
                        remapper.feed(event)
            except OSError as exc:
                if exc.errno == errno.EBUSY:
                    print(f"Could not grab {device.name}: {exc}", file=sys.stderr)
                    return 1
                print(f"{device.name} disconnected ({exc}); waiting for it to return", file=sys.stderr, flush=True)

        try:
            device.close()
        except OSError:
            pass
        device = wait_for_device(device)
        print(f"Reconnected to {device.name} ({device.path})", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Select a mouse device with a scroll wheel.")
    parser.add_argument("device", nargs="?", help="Path to the device (e.g., /dev/input/eventX).")
    parser.add_argument("--remap-sides", action="store_true", help="Enable remapping of side buttons to PageUp/PageDown.")
    args = parser.parse_args(argv)

    mice = get_mice()

    if not args.device:
        if not mice:
            print("No mouse wheels found!", file=sys.stderr)
            return 1
        print("Available mice:")
        for i, dev in enumerate(mice):
            print(f"{i + 1}: {dev.name} (path: {dev.path})")
        return 0

    try:
        device = evdev.InputDevice(args.device)
    except (evdev.EvdevError, OSError):
        try:
            device = select_mouse(mice, args.device)
        except LookupError as exc:
            print(exc, file=sys.stderr)
            return 1

    print(f"Listening for events on {device.name} ({device.path})", flush=True)

    try:
        return run(device, args.remap_sides)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
