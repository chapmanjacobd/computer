#!/usr/bin/env python3
# coding: utf-8
# license: WTFPLv2 [http://wtfpl.net]

import datetime
from datetime import datetime as DT
import unittest

from dateutil.relativedelta import relativedelta as RD

from chronocalc import *


class TestParseMethods(unittest.TestCase):
	def assertDatetimesEqual(self, a, b):
		self.assertEqual(a.replace(microsecond=0), b.replace(microsecond=0))

	def assertFail(self, text, exc=ParserException):
		self.assertRaises(exc, compute_from_string, text)

	def test_datetimes(self):
		self.assertEqual(compute_from_string('2015/07/09').datetime, DT(2015, 7, 9))
		self.assertEqual(compute_from_string('2015/07/10 00:00').datetime, DT(2015, 7, 10))
		self.assertEqual(compute_from_string('2015/07/11 01:45').datetime, DT(2015, 7, 11, 1, 45))
		self.assertEqual(compute_from_string('2015/07/09 14:30').datetime, DT(2015, 7, 9, 14, 30))
		self.assertEqual(compute_from_string('2015/07/09 14:30:26').datetime, DT(2015, 7, 9, 14, 30, 26))
		self.assertEqual(compute_from_string('2015/07/09 2:15pm').datetime, DT(2015, 7, 9, 14, 15))
		self.assertEqual(compute_from_string('2015/07/09 3am').datetime, DT(2015, 7, 9, 3))
		self.assertEqual(compute_from_string('2015/07/09 12am').datetime, DT(2015, 7, 9))
		self.assertEqual(compute_from_string('2015/07/31 12pm').datetime, DT(2015, 7, 31, 12))

		self.assertEqual(compute_from_string('2015-07-31').datetime, DT(2015, 7, 31))
		self.assertEqual(compute_from_string('2015-07-31 01:23').datetime, DT(2015, 7, 31, 1, 23))
		self.assertEqual(compute_from_string('2015-07-31 01:23:45').datetime, DT(2015, 7, 31, 1, 23, 45))
		self.assertEqual(compute_from_string('2015-07-31T01:23:45').datetime, DT(2015, 7, 31, 1, 23, 45))
		self.assertEqual(compute_from_string('20150731T0123').datetime, DT(2015, 7, 31, 1, 23))
		self.assertEqual(compute_from_string('20150731T012345').datetime, DT(2015, 7, 31, 1, 23, 45))

		self.assertDatetimesEqual(compute_from_string('now').datetime, DT.now())
		self.assertDatetimesEqual(compute_from_string('today').datetime, DT.combine(datetime.date.today(), datetime.time()))
		self.assertEqual(compute_from_string('epoch').datetime, DT(1970, 1, 1))

	def test_fail_datetimes(self):
		self.assertFail('2015-02-29', InvalidDate)
		self.assertFail('2015-01-01 42:00', InvalidDate)
		self.assertFail('2015-01-01 00:99', InvalidDate)
		self.assertFail('fail')

	def test_durations(self):
		self.assertEqual(compute_from_string('1 second').delta, RD(seconds=1))
		self.assertEqual(compute_from_string('86410 seconds').delta, RD(days=1, seconds=10))
		self.assertEqual(compute_from_string('1 minute').delta, RD(minutes=1))
		self.assertEqual(compute_from_string('1 hour').delta, RD(hours=1))
		self.assertEqual(compute_from_string('2 hours').delta, RD(hours=2))
		self.assertEqual(compute_from_string('36 hours').delta, RD(days=1, hours=12))
		self.assertEqual(compute_from_string('1 day').delta, RD(days=1))
		self.assertEqual(compute_from_string('-1 day').delta, RD(days=-1))
		self.assertEqual(compute_from_string('0.5 day').delta, RD(days=0.5))
		self.assertEqual(compute_from_string('30 days').delta, RD(days=30))
		self.assertEqual(compute_from_string('1 week').delta, RD(days=7))
		self.assertEqual(compute_from_string('1 month').delta, RD(months=1))
		self.assertEqual(compute_from_string('1 year').delta, RD(years=1))
		self.assertEqual(compute_from_string('1 hour, 1 second').delta, RD(hours=1, seconds=1))
		self.assertEqual(compute_from_string('1 year, 1 hour').delta, RD(years=1, hours=1))
		self.assertEqual(compute_from_string('1 year, 4 days').delta, RD(years=1, days=4))
		self.assertEqual(compute_from_string('1 year, 4 days, 36 hours, 42 seconds').delta, RD(years=1, days=5, hours=12, seconds=42))

	def test_fail_durations(self):
		self.assertFail('1 year, 1 year', DuplicateUnit)

	def test_duration_ops(self):
		TD = datetime.timedelta

		self.assertEqual(compute_from_string('1 second + 2 hours').delta, RD(seconds=1, hours=2))
		self.assertEqual(compute_from_string('1 hour, 1 second + 1 hour').delta, RD(hours=2, seconds=1))
		self.assertEqual(compute_from_string('1 hour + 1 hour, 1 second').delta, RD(hours=2, seconds=1))
		self.assertEqual(compute_from_string('0 hours').delta, RD())
		self.assertEqual(compute_from_string('0 hours - 1 hour + 1 hour').delta, RD())
		self.assertEqual(compute_from_string('3 * 1 second').delta, RD(seconds=3))
		self.assertEqual(compute_from_string('1 second * 4').delta, RD(seconds=4))
		self.assertEqual(compute_from_string('2 hours * 4').delta, RD(hours=8))
		self.assertEqual(compute_from_string('4 * 1 hour + 1 hour').delta, RD(hours=5))
		self.assertEqual(compute_from_string('4 * 1 hour, 2 seconds').delta, RD(hours=4, seconds=8))

		self.assertEqual(compute_from_string('1 hour / 2').delta, RD(minutes=30))

		mixed = compute_from_string('2 hours - 1 hour, 1 second')
		self.assertEqual(mixed.delta, RD(hours=1, seconds=-1))
		self.assertEqual(mixed.approx().delta, RD(minutes=59, seconds=59))

	def test_number_ops(self):
		self.assertEqual(compute_from_string('42.53').value(), 42.53)
		self.assertEqual(compute_from_string('12 + 0.34').value(), 12.34)
		self.assertEqual(compute_from_string('0.5 * 4').value(), 2)
		self.assertEqual(compute_from_string('1 / 2').value(), 0.5)
		self.assertEqual(compute_from_string('2 hours / 1 second').value(), 7200)

	def test_datetime_ops(self):
		self.assertEqual(compute_from_string('2015/07/31 - 2015/07/30').delta, RD(days=1))
		self.assertEqual(compute_from_string('2015/07/15 - 2015/08/15').delta, RD(months=-1))
		self.assertEqual(compute_from_string('2015/07/15 12pm - 2015/08/15 00:00').delta, RD(days=-30, hours=-12))
		self.assertEqual(compute_from_string('2015/03/15 01:10 - 2015/02/15 23:20').delta, RD(days=27, hours=1, minutes=50))
		self.assertEqual(compute_from_string('23:20 - 01:10').delta, RD(hours=22, minutes=10))
		self.assertEqual(compute_from_string('01:10 - 23:20').delta, RD(hours=-22, minutes=-10))
		self.assertEqual(compute_from_string('1970/01/10 - epoch').delta, RD(days=9))

	def test_datetime_duration_ops(self):
		self.assertEqual(compute_from_string('2015/07/31 + 1 day').datetime, DT(2015, 8, 1))
		self.assertEqual(compute_from_string('2015/07/31 + 2 days').datetime, DT(2015, 8, 2))
		self.assertEqual(compute_from_string('2015/02/28 + 1 day').datetime, DT(2015, 3, 1))
		self.assertEqual(compute_from_string('2015/05/04 + 3 hours, 10 seconds').datetime, DT(2015, 5, 4, 3, 0, 10))
		self.assertEqual(compute_from_string('2015/05/04 + 3 hours + 10 seconds').datetime, DT(2015, 5, 4, 3, 0, 10))
		self.assertEqual(compute_from_string('2015/05/04 10:45 + 3 hours + 10 seconds').datetime, DT(2015, 5, 4, 13, 45, 10))
		self.assertEqual(compute_from_string('2015/05/04 10:45 - 3 hours + 10 seconds').datetime, DT(2015, 5, 4, 7, 45, 10))
		self.assertEqual(compute_from_string('2015/01/31 + 2 months').datetime, DT(2015, 3, 31))
		self.assertEqual(compute_from_string('2015/04/29 + 2 months').datetime, DT(2015, 6, 29))

	def test_fail_ops(self):
		self.assertFail('2015/01/01 + 10', BadOperand)
		self.assertFail('2015/01/01 - 10', BadOperand)
		self.assertFail('2015/01/01 * 10', BadOperand)
		self.assertFail('2015/01/01 / 10', BadOperand)
		self.assertFail('2015/01/01 + 2015/01/01', BadOperand)
		self.assertFail('2015/01/01 * 2015/01/01', BadOperand)
		self.assertFail('2015/01/01 / 2015/01/01', BadOperand)
		self.assertFail('1 day + 10', BadOperand)
		self.assertFail('1 day - 10', BadOperand)
		self.assertFail('1 day - 2015/01/01', BadOperand)
		self.assertFail('1 day * 1 day', BadOperand)
		self.assertFail('2015/01/01 * 1 day', BadOperand)
		self.assertFail('2015/01/01 / 1 day', BadOperand)


if __name__ == '__main__':
	unittest.main()
