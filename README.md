# sysinfo-cli

[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A colorful, cross-platform system information tool for the terminal. Like neofetch, but in Python and works on Windows too.

## Features

- OS, kernel, architecture detection
- CPU info + real-time usage
- Memory usage with progress bar
- Disk usage with progress bar
- Network interface list
- Uptime, shell, terminal, DE/WM
- Process and user count
- Cross-platform (Windows, Linux, macOS)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python sysinfo.py
```

## Example Output

```
         .-.
        (0 0)
    +---ooU----+       user@host
   |          |       ----------------------
   |  O    O  |       OS:      Windows 10
   |          |       Kernel:  10.0.19045
   +----------+       Arch:    AMD64
    |________|        Uptime:  3:12:45.123456

 Shell:     cmd.exe
 Terminal:  Windows Terminal
 CPU:       Intel(R) Core(TM) i7-8700K (6 cores)
 CPU Usage: 23.4%
 RAM:       6.2GB / 16.0GB
           ████████░░░░░░░░░░░░ 38.8%
 Disk:      234GB / 512GB
           █████████░░░░░░░░░░░ 45.7%
```

## Requirements

- Python 3.8+
- psutil (optional - enables RAM/disk/process stats)
- netifaces (optional - enables network interface detection)
