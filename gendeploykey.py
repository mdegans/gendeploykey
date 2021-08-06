#!/usr/bin/python3

# Copyright 2021 Michael de Gans

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import platform
import shutil
import string
import subprocess
import sys

SSH_KEYGEN = shutil.which("ssh-keygen")
BITS = 4096
# this is so we don't store any deploy private keys, even accidentally
ALLOWED_PATHS = (
    # usually, in Linux, external drives are mounted in one of these
    "/mnt/",
    "/media/",
    # Mac OS uses `Volumes`
    "/Volumes/",
    # In Windows, all drives except C
    *(f"{d}:\\" for d in string.ascii_letters if d.lower() != "c"),
)


def check_ssh_keygen(ssh_keygen=SSH_KEYGEN):
    system = platform.system()
    if not ssh_keygen:
        if system == "Linux":
            if shutil.which("apt-get"):
                # every Debian distro we care about will use this package name
                howto = "Run: `sudo apt-get update && sudo apt-get install openssh-client`"
            else:
                howto = (
                    "Install OpenSSH client using your distro's package manager"
                )
        if system == "Windows":
            if int(platform.uname().release) >= 10:
                howto = (
                    "Use Windows 'Apps and Features' to install `OpenSSH"
                    "Client` or run `Add-WindowsCapability -Online -Name"
                    " OpenSSH.Client*` from PowerShell"
                )
        if system == "Darwin":
            howto = (
                "Mac OS should already include `ssh-keygen` but it's not found."
            )
        raise FileNotFoundError(f"`ssh-keygen` not found. {howto}")


def check_id_rsa_path(path: str, allowed_paths=ALLOWED_PATHS) -> str:
    realpath = os.path.realpath(path)
    if not realpath.startswith(allowed_paths):
        raise ValueError("Key must be generated in-place on the SD card.")
    return realpath


def ssh_keygen(id_rsa: str, bits=BITS, ssh_keygen=SSH_KEYGEN, check_path=True):
    check_ssh_keygen(ssh_keygen)
    if check_path:
        id_rsa = check_id_rsa_path(id_rsa)
    command = [ssh_keygen, "-f", id_rsa, "-N", "", "-C", ""]
    if bits:
        command.extend(("-b", str(int(bits))))
    print(f'Running: {" ".join(command)}')
    subprocess.run(command).check_returncode()
    outfilename = f"{id_rsa}.pub"
    with open(outfilename) as f:
        pubkey = next(f)
        print(f"\nAdd this public key to github deploy keys with customer name:\n\n{pubkey}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="generate a deploy key on an external drive",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    ap.add_argument("id_rsa", help="deploy key filename")
    ap.add_argument(
        "--no-check-path",
        action="store_false",
        dest="check_path",
        help="allow generating keys in any path",
    )
    ap.add_argument("-b", "--bits", default=BITS)
    ap.add_argument(
        "--ssh-keygen", default=SSH_KEYGEN, help="custom ssh-keygen executable"
    )

    ssh_keygen(**vars(ap.parse_args()))
