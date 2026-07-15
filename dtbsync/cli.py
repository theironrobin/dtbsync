"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser
import json
import shutil
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



def get_device_maker() -> str:
    """Return the device's device_maker, e.g., 'qcom'"""
    result = subprocess.run(
        ["cat", "/proc/device-tree/compatible"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.rstrip("\x00").split("\x00")[1].split(",")[0]



def get_kernel_version() -> str:
    """Return the running kernel version."""
    result = subprocess.run(
        ["uname", "-r"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def get_efi_dir() -> str:
    """Return the mount point of the EFI System Partition."""
    result = subprocess.run(
        ["lsblk", "--json", "--output", "MOUNTPOINT,PARTTYPE"],
        check=True,
        capture_output=True,
        text=True,
    )
    efi_parttype = "c12a7328-f81f-11d2-ba4b-00a0c93ec93b"
    devices = json.loads(result.stdout).get("blockdevices", [])

    while devices:
        device = devices.pop(0)
        mountpoint = device.get("mountpoint")
        if (device.get("parttype") or "").lower() == efi_parttype and mountpoint:
            return mountpoint
        devices.extend(device.get("children", []))

    raise RuntimeError("No mounted EFI System Partition found")


def copy_dtb_to_efi(dtb: str, efi_dir: str) -> None:
    """Copy a DTB file into the mounted EFI directory."""
    shutil.copy2(dtb, efi_dir)



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
    device_maker = get_device_maker()
    efi_dir = get_efi_dir()
    dtb_path = "/usr/lib/modules/" + kernel_version + "/dtb/" + device_maker + "/"
    dtb = dtb_path + dtb_name

    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} Copying {dtb} to {efi_dir}")
    copy_dtb_to_efi(dtb, efi_dir)
    
    #for user in args.users:
    #    print(f"Hello {Fore.YELLOW}{user.name}{Fore.RESET}")
    exit(0)
