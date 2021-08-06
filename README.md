# `gendeploykey.py`

Is a simple script to generate a deploy key securely in place on an external
drive using any operating system.

Usage is:
```
python3 gendeploykey.py private_key_filename_id_rsa
```

The public key will be stored as `whatever_filename.pub` and also printed to
console so it can be added as a deploy key on GitHub (or wherever).

## Safety features:

By default, `gendeploykey` will refuse to generate a private key on internal
storage. A **USB stick or MicroSD card must be used**. This check can be
disabled with `--no-check-path` but it's recommended you not do this unless the script is not detecting your external disk correctly.