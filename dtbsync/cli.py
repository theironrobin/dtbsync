"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser
import subprocess

from colorama import Fore

from . import __version__
from .model import User

dtbMap = {
    "lenovo,thinkpad-x13s": "sc8280xp-lenovo-thinkpad-x13s.dtb",
    "microsoft,blackrock": "sc8280xp-microsoft-blackrock.dtb"
}


def get_dtb_name() -> str:
    """Return the device tree's compatible string."""
    result = subprocess.run(
        ["cat", "/proc/device-tree/compatible"],
        check=True,
        capture_output=True,
        text=True,
    )
    compatible = result.stdout.rstrip("\x00").split("\x00")[0]
    return dtbMap[compatible]


def get_kernel_version() -> str:
    """Return the running kernel version."""
    result = subprocess.run(
        ["uname", "-r"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()



def run():
    """
    entry point
    """
    parser = ArgumentParser(description="some documentation here")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    # parser.add_argument(dest="users", nargs=ONE_OR_MORE, type=User, help="your name")
    args = parser.parse_args()
    dtb_name = get_dtb_name()
    kernel_version = get_kernel_version()
    print("DTB Name:", dtb_name)
    print("Kernel Version:", kernel_version)
    #for user in args.users:
    #    print(f"Hello {Fore.YELLOW}{user.name}{Fore.RESET}")
    exit(0)
