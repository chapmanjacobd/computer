#!/usr/bin/env pytest
# from https://gitlab.com/hydrargyrum/attic/
# SPDX-License-Identifier: WTFPL

import datetime
from decimal import Decimal
import json
import os
import subprocess
import types

import pytest


os.chdir(os.path.dirname(__file__))


def run(input):
	return json.loads(subprocess.check_output(
		["./pyliteral-to-json"],
		encoding="utf8",
		input=input
	))


def test_basic():
	assert run("""{0o1: u'2', 0x3: None,}""") == {"1": "2", "3": None}


def test_error():
	with pytest.raises(subprocess.CalledProcessError):
		run("[1+1]")

	with pytest.raises(subprocess.CalledProcessError):
		run("[id(1)]")

	with pytest.raises(subprocess.CalledProcessError):
		run("[datetime(1+1)]")


def test_datetime():
	assert run("""[datetime(2013, 4, 5)]""") == ["2013-04-05 00:00:00"]


def test_decimal():
	assert run("""[Decimal('1')]""") == ["1"]


def test_set():
	assert run(repr(set())) == []
	assert run(repr(frozenset())) == []
	assert run(repr(frozenset({1}))) == [1]
	assert run(repr({1})) == [1]
	assert run(repr({datetime.datetime(2013, 4, 5)})) == ["2013-04-05 00:00:00"]
	assert run(repr({Decimal("1")})) == ["1"]


def test_tuple():
	assert run(repr(())) == []
	assert run(repr((1,))) == [1]
	assert run(repr((1, 2))) == [1, 2]
	assert run(repr(((),))) == [[]]


def test_namespace():
	assert run(repr(types.SimpleNamespace(a=1, b=["2"]))) == {"a": 1, "b": ["2"]}
