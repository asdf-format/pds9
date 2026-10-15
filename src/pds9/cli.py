import sys
from argparse import ArgumentParser
from pathlib import Path

import pds9
from pds9 import plugin

plugin.create_ds9_tmp_dir()


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--print", "-p", action="store_true", help="Print ds9 config snippet"
    )

    args = parser.parse_args()
    topdir = Path(pds9.__file__).parent
    inifile = topdir / "ds9.ini"
    python_bin = Path(sys.prefix) / "bin" / "python3"
    asdf_tmp_dir = str(plugin.DS9TMP)

    if args.print:
        print(f"set pds9_python {python_bin}")  # noqa: T201
        print(f"set asdf_tmp_dir_arg {asdf_tmp_dir}")  # noqa: T201
        print(f"source {inifile}")  # noqa: T201
