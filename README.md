# dtbsync

# This project has moved

**The canonical repository is now on Codeberg:**

https://codeberg.org/ironrobin/dtbsync

This GitHub repository is no longer accepting issues or pull requests. Please
open new issues and submit contributions on Codeberg.

Synchronize the appropriate Device Tree Blob (DTB) to the EFI System Partition.

## Features

- Automatically detects the current hardware
- Finds the matching DTB for the installed kernel
- Locates the mounted EFI System Partition
- Copies the DTB into the EFI System Partition
- Designed to integrate with pacman hooks

## Usage

From the project directory:

```sh
sudo poetry run dtbsync
```

Once installed:

```sh
sudo dtbsync
```

> [!NOTE]
> dtbsync writes to the EFI System Partition and therefore typically requires root privileges.


## Supported Hardware

dtbsync currently supports the following Qualcomm-based platforms:

- **Lenovo ThinkPad X13s** (SC8280XP)
- **Lenovo ThinkPad T14s** (X1E, untested)
- **Windows Dev Kit 2023 (Volterra)** (SC8280XP)

Support for additional Device Tree-based systems is planned.
