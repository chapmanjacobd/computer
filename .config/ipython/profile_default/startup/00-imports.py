import argparse
import logging
from pathlib import Path
import os
import shutil
import sys
from subprocess import PIPE, run

import geopandas as gpd
import pandas as pd
import numpy as np
from IPython.core import ultratb
from IPython.terminal.debugger import TerminalPdb
from rich import inspect, print as rprint
from pprint import pprint
from rich.logging import RichHandler

pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.3f}'.format)

def argparse_log():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", action="count", default=0)
    args, _unknown = parser.parse_known_args()
    print(args)

    sys.excepthook = ultratb.FormattedTB(
        mode="Verbose" if args.verbose > 0 else "Context",
        theme_name="Neutral",
        call_pdb=1,
        debugger_cls=TerminalPdb,
    )

    log_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    logging.root.handlers = []  # clear any existing handlers
    logging.basicConfig(
        level=log_levels[min(len(log_levels) - 1, args.verbose)],
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )
    return logging.getLogger()


log = argparse_log()


def cmd(command, **kwargs):
    log = logging.getLogger()
    r = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True, **kwargs)
    log.debug(r.args)
    if r.returncode != 0:
        log.error(f"process exited with returncode {r.returncode}")
    log.info(r.stdout.strip())
    log.error(r.stderr.strip())
    return r
