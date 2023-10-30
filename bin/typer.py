#!/usr/bin/python3

import random
import string
import sys
import threading
import time

import numpy as np
import pynput


class sim_keyboard(threading.Thread):
    def __init__(self, text, start_delay=1.5, dct_delays={('a', 'i'): 0.12}, delay_range=(0.07, 0.24)):
        threading.Thread.__init__(self)

        self.text = text
        self.start_delay = start_delay
        self.last_char = " "
        self.dct_delays = dct_delays
        self.delay_range = delay_range

        self.control = pynput.keyboard.Controller()

    def run(self):
        time.sleep(self.start_delay)
        for char in self.text:
            if (self.last_char, char) not in self.dct_delays:
                self.dct_delays[(self.last_char, char)] = random.uniform(*self.delay_range)
            delay = np.random.normal(loc=self.dct_delays.get((self.last_char, char)), scale=0.02)

            if random.random() < np.random.normal(loc=0.1, scale=0.03):
                time.sleep(delay - 0.03)
                self.press_wrong_key(delay)
                time.sleep(delay + 0.02)
            else:
                time.sleep(delay - 0.03)

            self.control.type(char)
            self.last_char = char

    def press_wrong_key(self, delay):
        one_typo = 0.8
        two_typos = 0.15
        three_typos = 0.05
        num_typos = np.random.choice([1, 2, 3], p=[one_typo, two_typos, three_typos])

        for _ in range(num_typos):
            wrong_char = random.choice(string.ascii_lowercase)
            self.control.type(wrong_char)
            time.sleep(delay)

        for _ in range(num_typos):
            self.control.tap(pynput.keyboard.Key.backspace)
            time.sleep(np.random.normal(loc=0.05, scale=0.01))


keyboard_thread = sim_keyboard('\n'.join(sys.stdin.readlines()).replace("    ", "\t"))
keyboard_thread.start()
keyboard_thread.join()
