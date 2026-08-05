<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0b486b,100:f56217&height=200&section=header&text=LinuxSetupPro&fontColor=ffffff&fontSize=60&animation=fadeIn" alt="LinuxSetupPro" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Antech-greyhat/linux-setup-pro?style=flat-square" alt="stars" />
  <img src="https://img.shields.io/github/v/release/Antech-greyhat/linux-setup-pro?style=flat-square" alt="release" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="license" />
  <img src="https://img.shields.io/badge/tested-Termux-informational?style=flat-square" alt="termux" />
  <img src="https://img.shields.io/badge/tested-Ubuntu-informational?style=flat-square" alt="ubuntu" />
  <img src="https://img.shields.io/badge/tested-Fedora-informational?style=flat-square" alt="fedora" />
  <img src="https://img.shields.io/badge/tested-Arch-informational?style=flat-square" alt="arch" />
</p>

LinuxSetupPro is a cross-platform setup and hardening tool for Termux, Debian/Ubuntu, Fedora, and Arch/BlackArch. It installs a curated set of essentials, development runtimes, and networking utilities, then offers an opt-in tier of security and penetration-testing tools, terminal customization, honest per-package reporting, and a persistent terminal banner generator. It detects your platform, picks the right package manager, and never lets one failed package abort the run.

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Requirements](#requirements)
- [Install on Termux](#install-on-termux)
- [Install on Linux](#install-on-linux)
- [CLI Flags](#cli-flags)
- [Supported Platforms](#supported-platforms)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)

## Features

- Primary categories installed in order: Essentials, Development, Security/Networking, Fun/Terminal Flair, and an interactive Customization step.
- Opt-in secondary menu of OSINT, network analysis, web-app testing, password-auth, wireless, exploitation, and forensics tools.
- Real progress feedback per package, alternating a progress bar and a spinner, with a distinct color per status.
- Honest error reporting: captured stderr is matched against known patterns to explain the cause and suggest a platform-specific fix. Unrecognized errors are shown verbatim, never invented.
- Per-run reports saved as machine-readable JSON and plain-text logs.
- Persistent hacker-style terminal banner generator with figlet fonts and color schemes.
- `--dry-run` shows exactly what would change without executing anything.

## Screenshots

![Startup banner](./images/startup%20banner.jpg)
![Progress display](./images/progress%20display.jpg)
![Run report](./assets/report.png)
![Secondary menu](./assets/secondary-menu.png)

## Requirements

- Python 3.8 or newer
- One of the supported platforms and its package manager (pkg, apt, dnf, or pacman)
- Python packages listed in `requirements.txt` (rich, questionary, PyYAML)

## Install on Termux

```bash
apt update && apt upgrade -y
pkg install git python
pip install rich questionary PyYAML
git clone --depth=1 https://github.com/Antech-greyhat/linux-setup-pro.git
cd linux-setup-pro
python3 main.py
```

If `pip` is not available run `python3 -m ensurepip --upgrade` first. If PyYAML
fails to compile, install it from the Termux repo instead: `pkg install python-yaml`.

---

## Install on Linux

### Debian / Ubuntu

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git python3 python3-pip
pip3 install rich questionary PyYAML
git clone --depth=1 https://github.com/Antech-greyhat/linux-setup-pro.git
cd linux-setup-pro
python3 main.py
```

### Fedora / RHEL

```bash
sudo dnf upgrade -y
sudo dnf install git python3 python3-pip
pip3 install rich questionary PyYAML
git clone --depth=1 https://github.com/Antech-greyhat/linux-setup-pro.git
cd linux-setup-pro
python3 main.py
```

### Arch / BlackArch / Manjaro

```bash
sudo pacman -Syu
sudo pacman -S git python python-pip
pip install rich questionary PyYAML
git clone --depth=1 https://github.com/Antech-greyhat/linux-setup-pro.git
cd linux-setup-pro
python3 main.py
```

Python 3.8 or newer is required. Check with `python3 --version` before running.
If your version is older, upgrade it first:

```bash
# Termux
pkg upgrade python

# Debian / Ubuntu
sudo apt install python3.10

# Fedora
sudo dnf install python3.11

# Arch
sudo pacman -Syu python
```

## CLI Flags

| Flag | Description |
| --- | --- |
| `--dry-run` | Show what would install, upgrade, or remove without executing anything. |
| `--only primary` | Run the primary categories only and skip the secondary menu. |
| `--only secondary` | Jump straight to the secondary tools menu. |
| `--set-editor` | Reopen the editor picker, update `EDITOR`, then exit. |
| `--report` | Print the most recent saved report and exit. |
| `--version` | Print the tool version and exit. |
| `--no-banner` | Suppress the startup and end-of-run banners. |
| `--verbose` | Show raw subprocess output instead of the progress widgets. |
| `--remove-banner` | Remove the persistent shell banner block and exit. |

## Supported Platforms

| Platform | Backend | Detection |
| --- | --- | --- |
| Termux | pkg | `$PREFIX` contains `com.termux` |
| Debian / Ubuntu | apt | `ID`/`ID_LIKE` in `/etc/os-release` |
| Fedora / RHEL | dnf | `ID`/`ID_LIKE` in `/etc/os-release` |
| Arch / BlackArch / Manjaro | pacman | `ID`/`ID_LIKE` in `/etc/os-release` |

## FAQ

**What happens when a package fails to install?**
The run continues. The package is marked `failed`, and the report shows the cause and a platform-specific suggestion when the error is recognized, or the raw stderr and a pointer to the JSON log when it is not.

**How do I remove the terminal banner?**
Run `python3 main.py --remove-banner`. It strips the marked block from your `.bashrc` or `.zshrc`. Restart your terminal afterwards.

**Does this work on rooted devices or unrooted Termux?**
It works on both. Tools marked `[LOCKED]` need a proot Linux chroot or root access to function fully. On stock, unrooted Termux they may install but not run as expected. Use `proot-distro` to set up a Kali or Parrot chroot for those.

**How do I add a custom package?**
Edit `config/packages.yaml` and add an entry with its per-backend package names. No code changes are needed. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add packages, error patterns, and new distributions.

## License

Released under the [MIT License](LICENSE), copyright Antech.

---

Built by Antech. If LinuxSetupPro is useful to you, consider a star and a follow at https://github.com/Antech-greyhat.
