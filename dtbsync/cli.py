"""
command line interface
"""

from argparse import ONE_OR_MORE, ArgumentParser
from glob import glob
import json
from pathlib import Path
import shutil
import subprocess

from colorama import Fore

from . import __version__
from .model import User

# lenovo,thinkpad-t14s-oled␀lenovo,thinkpad-t14s␀qcom,x1e78100␀qcom,x1e80100
# lenovo,thinkpad-x13s␀qcom,sc8280xp␀
dtbMap = {
    "thinkpad-x13s": ("qcom", "sc8280xp-lenovo-thinkpad-x13s.dtb"),
    "thinkpad-t14s-oled": ("qcom", "x1e78100-lenovo-thinkpad-t14s-oled.dtb"),
    "blackrock": ("qcom", "sc8280xp-microsoft-blackrock.dtb")
}



def get_board_variant() -> str:
    """Return the device's device_maker, e.g., 'qcom'"""
    result = subprocess.run(
        ["cat", "/proc/device-tree/compatible"],
        check=True,
        capture_output=True,
        text=True,
    )
    x = result.stdout.rstrip("\x00").split("\x00")[0].split(",")[1]
    return x



def get_kernel_version() -> str:
    """Return the kernel version contained in an installed DTB path."""
    dtb_paths = glob("/usr/lib/modules/*/dtb/qcom/*.dtb")
    if not dtb_paths:
        raise RuntimeError("No Qualcomm DTB found under /usr/lib/modules")
    dtb_path = (
        dtb_paths[0]
        if len(dtb_paths) == 1
        else max(dtb_paths, key=lambda path: Path(path).stat().st_mtime)
    )

    path = Path(dtb_path)
    parts = path.parts
    try:
        modules_index = parts.index("modules")
        kernel_version = parts[modules_index + 1]
    except (ValueError, IndexError) as error:
        raise ValueError(f"Invalid kernel DTB path: {dtb_path}") from error

    if parts[modules_index + 2 : modules_index + 4] != ("dtb", "qcom"):
        raise ValueError(f"Invalid Qualcomm DTB path: {dtb_path}")

    return kernel_version



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



def get_dtb(board_variant: str, kernel_version: str) -> str:
    """Linux package installs to /usr/lib/modules/$kernver/dtb/$vendor/$dtb_name"""
    vendor = dtbMap[board_variant][0]
    dtb_name = dtbMap[board_variant][1]
    result = "/usr/lib/modules/{0}/dtb/{1}/{2}".format(kernel_version,vendor,dtb_name)
    return result



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

    board_variant = get_board_variant()
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} Board: {board_variant}")
    kernel_version = get_kernel_version()
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} Kernel: {kernel_version}")

    dtb = get_dtb(get_board_variant(), get_kernel_version())
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} DTB: {dtb}")
    
    efi_dir = get_efi_dir()
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} EFI System Partition: {efi_dir}")

    dtb_name = dtbMap[get_board_variant()][1]
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} Copying {dtb_name} to {efi_dir}/{dtb_name}")
    
    copy_dtb_to_efi(dtb, efi_dir)
    print(f"{Fore.CYAN}dtbsync:{Fore.RESET} Done.")
    
    #for user in args.users:
    #    print(f"Hello {Fore.YELLOW}{user.name}{Fore.RESET}")
    exit(0)
