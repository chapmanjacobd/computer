#!/usr/bin/env pytest
"""Tests for wheel.py."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from evdev import ecodes as e

MODULE_PATH = Path(__file__).with_name("wheel.py")
spec = importlib.util.spec_from_file_location("wheel", MODULE_PATH)
wheel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wheel)


class FakeSink:
    def __init__(self):
        self.events = []

    def write(self, type, code, value):
        self.events.append((type, code, value))

    def syn(self):
        self.events.append(("syn",))


class FakeDevice:
    def __init__(self, name="Fake Mouse", phys="usb-fake/input0", path="/dev/input/event99", caps=None):
        self.name = name
        self.phys = phys
        self.path = path
        self.info = SimpleNamespace(vendor=0x1234, product=0x5678, bustype=0x3, version=0x111)
        self._caps = caps if caps is not None else {}

    def capabilities(self, absinfo=False):
        return self._caps


def ev(type, code, value):
    return wheel.evdev.InputEvent(0, 0, type, code, value)


def make(remap_sides=False, has_hi_res=False):
    sink = FakeSink()
    return wheel.WheelRemapper(sink, remap_sides=remap_sides, has_hi_res=has_hi_res), sink


def keys(sink):
    return [event for event in sink.events if event[0] == e.EV_KEY]


def rels(sink):
    return [event for event in sink.events if event[0] == e.EV_REL]


def test_right_click_without_action_is_click():
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 0))

    assert keys(sink) == [
        (e.EV_KEY, e.BTN_RIGHT, 1),
        (e.EV_KEY, e.BTN_RIGHT, 0),
    ]


def test_right_click_splits_press_and_release_across_frames():
    # libinput drops a button click whose press and release share a frame.
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 0))

    assert sink.events == [
        (e.EV_KEY, e.BTN_RIGHT, 1),
        ("syn",),
        (e.EV_KEY, e.BTN_RIGHT, 0),
    ]


def test_right_click_with_action_is_suppressed():
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 0))

    assert (e.EV_KEY, e.BTN_RIGHT, 1) not in sink.events
    assert (e.EV_KEY, e.BTN_RIGHT, 0) not in sink.events


def test_right_middle_sends_ctrl_w():
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 1))

    assert keys(sink) == [
        (e.EV_KEY, e.KEY_LEFTCTRL, 1),
        (e.EV_KEY, e.KEY_W, 1),
        (e.EV_KEY, e.KEY_W, 0),
        (e.EV_KEY, e.KEY_LEFTCTRL, 0),
    ]


def test_middle_release_after_chord_is_swallowed():
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 0))

    assert (e.EV_KEY, e.BTN_MIDDLE, 0) not in sink.events
    assert (e.EV_KEY, e.BTN_MIDDLE, 1) not in sink.events


def test_plain_middle_click_is_forwarded():
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_MIDDLE, 0))

    assert keys(sink) == [
        (e.EV_KEY, e.BTN_MIDDLE, 1),
        (e.EV_KEY, e.BTN_MIDDLE, 0),
    ]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, [(e.EV_KEY, e.KEY_PAGEUP, 1), (e.EV_KEY, e.KEY_PAGEUP, 0)]),
        (-1, [(e.EV_KEY, e.KEY_PAGEDOWN, 1), (e.EV_KEY, e.KEY_PAGEDOWN, 0)]),
        (
            2,
            [
                (e.EV_KEY, e.KEY_PAGEUP, 1),
                (e.EV_KEY, e.KEY_PAGEUP, 0),
                (e.EV_KEY, e.KEY_PAGEUP, 1),
                (e.EV_KEY, e.KEY_PAGEUP, 0),
            ],
        ),
    ],
)
def test_right_wheel_pages_by_coarse_detents(value, expected):
    remapper, sink = make()
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_REL, e.REL_WHEEL, value))

    assert keys(sink) == expected
    assert rels(sink) == []


def test_right_wheel_hi_res_accumulates_to_detents():
    remapper, sink = make(has_hi_res=True)
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))

    remapper.feed(ev(e.EV_REL, e.REL_WHEEL_HI_RES, 60))
    assert keys(sink) == []

    remapper.feed(ev(e.EV_REL, e.REL_WHEEL_HI_RES, 60))
    assert keys(sink) == [(e.EV_KEY, e.KEY_PAGEUP, 1), (e.EV_KEY, e.KEY_PAGEUP, 0)]


def test_right_wheel_hi_res_ignores_accompanying_coarse_event():
    remapper, sink = make(has_hi_res=True)
    remapper.feed(ev(e.EV_KEY, e.BTN_RIGHT, 1))
    remapper.feed(ev(e.EV_REL, e.REL_WHEEL_HI_RES, 120))
    remapper.feed(ev(e.EV_REL, e.REL_WHEEL, 1))

    assert keys(sink) == [(e.EV_KEY, e.KEY_PAGEUP, 1), (e.EV_KEY, e.KEY_PAGEUP, 0)]


def test_wheel_without_right_button_is_forwarded():
    remapper, sink = make(has_hi_res=True)
    remapper.feed(ev(e.EV_REL, e.REL_WHEEL_HI_RES, 120))
    remapper.feed(ev(e.EV_REL, e.REL_WHEEL, 1))

    assert rels(sink) == [
        (e.EV_REL, e.REL_WHEEL_HI_RES, 120),
        (e.EV_REL, e.REL_WHEEL, 1),
    ]


def test_side_buttons_remapped():
    remapper, sink = make(remap_sides=True)
    remapper.feed(ev(e.EV_KEY, e.BTN_EXTRA, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_SIDE, 1))

    assert keys(sink) == [
        (e.EV_KEY, e.KEY_PAGEUP, 1),
        (e.EV_KEY, e.KEY_PAGEDOWN, 1),
    ]


def test_side_buttons_forwarded_when_not_remapped():
    remapper, sink = make(remap_sides=False)
    remapper.feed(ev(e.EV_KEY, e.BTN_EXTRA, 1))
    remapper.feed(ev(e.EV_KEY, e.BTN_SIDE, 1))

    assert keys(sink) == [
        (e.EV_KEY, e.BTN_EXTRA, 1),
        (e.EV_KEY, e.BTN_SIDE, 1),
    ]


def test_syn_is_forwarded_exactly_once():
    remapper, sink = make()
    remapper.feed(ev(e.EV_SYN, e.SYN_REPORT, 0))

    assert sink.events == [(e.EV_SYN, e.SYN_REPORT, 0)]


def test_other_events_are_forwarded():
    remapper, sink = make()
    remapper.feed(ev(e.EV_REL, e.REL_X, 5))
    remapper.feed(ev(e.EV_MSC, e.MSC_SCAN, 0x90001))

    assert sink.events == [
        (e.EV_REL, e.REL_X, 5),
        (e.EV_MSC, e.MSC_SCAN, 0x90001),
    ]


def test_uinput_capabilities_keep_source_and_add_synthesized_keys():
    caps = {
        e.EV_KEY: [e.BTN_SIDE, e.BTN_EXTRA, e.BTN_LEFT],
        e.EV_REL: [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_WHEEL_HI_RES],
    }
    result = wheel.uinput_capabilities(FakeDevice(caps=caps))

    assert set(result[e.EV_KEY]) >= {
        e.BTN_SIDE,
        e.BTN_EXTRA,
        e.BTN_LEFT,
        e.KEY_PAGEUP,
        e.KEY_PAGEDOWN,
        e.KEY_LEFTCTRL,
        e.KEY_W,
    }
    assert set(result[e.EV_REL]) == {e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_WHEEL_HI_RES}


def test_uinput_capabilities_drop_syn():
    caps = {e.EV_SYN: [e.SYN_REPORT], e.EV_REL: [e.REL_WHEEL]}
    result = wheel.uinput_capabilities(FakeDevice(caps=caps))

    assert e.EV_SYN not in result


def test_has_hi_res():
    assert wheel.has_hi_res(FakeDevice(caps={e.EV_REL: [e.REL_WHEEL_HI_RES]}))
    assert not wheel.has_hi_res(FakeDevice(caps={e.EV_REL: [e.REL_WHEEL]}))


def test_virtual_device_is_detected_by_phys():
    assert wheel.is_virtual(FakeDevice(phys=wheel.VIRTUAL_PHYS))
    assert not wheel.is_virtual(FakeDevice(phys="usb-real/input0"))


def test_select_mouse_by_index():
    mice = [FakeDevice(name="a"), FakeDevice(name="b")]
    assert wheel.select_mouse(mice, "2").name == "b"


def test_select_mouse_by_name():
    mice = [FakeDevice(name="a"), FakeDevice(name="Logitech")]
    assert wheel.select_mouse(mice, "Logi").name == "Logitech"


def test_select_mouse_rejects_out_of_range():
    with pytest.raises(LookupError):
        wheel.select_mouse([FakeDevice()], "5")


def test_select_mouse_rejects_unknown_name():
    with pytest.raises(LookupError):
        wheel.select_mouse([FakeDevice(name="a")], "zzz")


def test_select_mouse_with_no_mice():
    with pytest.raises(LookupError):
        wheel.select_mouse([], "1")
