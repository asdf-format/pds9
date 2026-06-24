from argparse import ArgumentParser
from pathlib import Path
from string import Template
import sys
import pds9

def main():
    parser = ArgumentParser()
    parser.add_argument("--print", "-p", action="store_true", help="Print ds9 config snippet")

    args = parser.parse_args()
    topdir = Path(pds9.__file__).parent
    inifile = topdir / "ds9.ini"
    python_bin = Path(sys.prefix) / "bin" / "python3"

    if args.ini:
        print(f"set pds9_python {python_bin}")
        print(f"source {inifile}")
