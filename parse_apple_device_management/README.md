# Apple Device Management Configuration Parser

A Python script for parsing Apple device management YAML configuration files to extract and analyze payload keys for different platforms (macOS, iOS, visionOS).

## Overview

This tool helps security analysts and system administrators analyze Apple device management configurations by:
- Extracting payload keys from YAML configuration files
- Filtering results by platform and OS version
- Displaying results in formatted tables
- Identifying configuration patterns across different Apple platforms

## Features

- **Multi-platform support**: macOS, iOS, and visionOS
- **Flexible filtering**: Filter by OS version to focus on specific releases

## Requirements

- Python 3.8+
- Required packages:
  - `pyyaml` - YAML file parsing
  - `tabulate` - Table formatting
  - `pandas` (optional) - For data analysis

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install pyyaml tabulate
   ```

## Usage

### Basic Usage

```bash
python parse_device_management.py -p <platform>
```

### Command Line Options

| Option | Short | Description | Required | Example |
|--------|-------|-------------|----------|---------|
| `--platform` | `-p` | Target platform | Yes | `macOS`, `iOS`, `visionOS` |
| `--os_filter` | `-o` | OS version filter | No | `26`, `15.0` |
| `--directory` | `-d` | Directory to cloned Apple Device Management repository | Yes | `./path/to/cloned/repo` |

### Examples

_Assuming the Apple device-management repository has been cloned to your desktop folder._

**Parse macOS configurations:**
```bash
python parse_device_management.py -p macOS -d ~/Desktop/device-management/
```

**Filter iOS configurations for items introduced in version 26:**
```bash
python parse_device_management.py -p iOS -o 26 -d ~/Desktop/device-management/
```

## Output Format

Results are displayed in a formatted table showing:
- **Payload Key**: The configuration key name
- **Platform**: Target platform (macOS/iOS/visionOS)
- **Introduced**: OS version when the key was introduced
- **Deprecated**: OS version when deprecated (if applicable)
- **File**: Source YAML file path

### Sample Output
```
📄 File: ~/Desktop/device-management/mdm/profiles/com.apple.applicationaccess.yaml
+---------------------------------+--------------+
| Payload Key                     |   introduced |
+=================================+==============+
| allowSafariHistoryClearing      |           26 |
+---------------------------------+--------------+
| allowSafariPrivateBrowsing      |           26 |
+---------------------------------+--------------+
| deniedICCIDsForiMessageFaceTime |           26 |
+---------------------------------+--------------+
| deniedICCIDsForRCS              |           26 |
+---------------------------------+--------------+
```