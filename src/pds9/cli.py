from argparse import ArgumentParser
from pathlib import Path
from string import Template
import pds9

def main():
    parser = ArgumentParser()
    parser.add_argument("--ini", "-i", action="store_true", help="Return ds9 config snippet")

    args = parser.parse_args()
    topdir = Path(pds9.__file__).parent
    inifile = topdir / "ds9.ini"

    if args.ini:
        print(f"source {inifile}")
