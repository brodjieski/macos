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
- **Comprehensive parsing**: Handles both `payloadkeys` and `payload` structures
- **Error handling**: Robust YAML parsing with detailed error reporting
- **Clean output**: Formatted tables with file source information

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
| `--directory` | `-d` | Search directory | No | `./configs` (default: current directory) |

### Examples

**Parse macOS configurations:**
```bash
python parse_device_management.py -p macOS
```

**Filter iOS configurations for version 26:**
```bash
python parse_device_management.py -p iOS -o 26
```

**Search specific directory for visionOS configs:**
```bash
python parse_device_management.py -p visionOS -d /path/to/configs
```

**Multiple platform analysis:**
```bash
# Analyze all platforms
python parse_device_management.py -p macOS > macos_results.txt
python parse_device_management.py -p iOS > ios_results.txt
python parse_device_management.py -p visionOS > visionos_results.txt
```

## Input File Format

The script expects YAML files with either of these structures:

### PayloadKeys Structure
```yaml
payloadkeys:
  - key: "someConfigKey"
    supportedOS:
      macOS:
        introduced: "14.0"
        deprecated: "n/a"
      iOS:
        introduced: "17.0"
        deprecated: "n/a"
```

### Payload Structure
```yaml
payload:
  key: "someConfigKey"
  supportedOS:
    macOS:
      introduced: "14.0"
      deprecated: "n/a"
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
📄 File: ./configs/security.yaml
┌─────────────────┬─────────┬────────────┬─────────────┐
│ Payload Key     │ Platform│ introduced │ deprecated  │
├─────────────────┼─────────┼────────────┼─────────────┤
│ AllowGuestUser  │ macOS   │ 26         │ n/a         │
│ EnableFirewall  │ macOS   │ 24         │ n/a         │
└─────────────────┴─────────┴────────────┴─────────────┘
```

## Use Cases

### Security Analysis
- **Configuration drift detection**: Compare payload keys across different OS versions
- **Compliance checking**: Verify required security settings are available
- **Deprecation tracking**: Identify deprecated configuration options

### System Administration
- **Platform migration**: Understand configuration differences between platforms
- **Version planning**: See what new options are available in newer OS versions
- **Documentation**: Generate configuration inventories for different platforms

### Development
- **API compatibility**: Check when configuration options were introduced
- **Testing**: Verify configuration parsing across different file formats
- **Integration**: Prepare for new OS releases by understanding configuration changes

## Advanced Usage

### Scripting Integration
```bash
#!/bin/bash
# Analyze all platforms and generate reports
PLATFORMS=("macOS" "iOS" "visionOS")
for platform in "${PLATFORMS[@]}"; do
    echo "Analyzing $platform configurations..."
    python parse_device_management.py -p "$platform" -d ./configs > "${platform}_analysis.txt"
done
```

### Configuration Validation
```bash
# Check for specific security keys across all platforms
python parse_device_management.py -p macOS | grep -i security
python parse_device_management.py -p iOS | grep -i security
```

### Version Comparison
```bash
# Compare configurations between OS versions
python parse_device_management.py -p macOS -o 25 > macos_v25.txt
python parse_device_management.py -p macOS -o 26 > macos_v26.txt
diff macos_v25.txt macos_v26.txt
```

## Error Handling

The script handles various error conditions gracefully:
- **Invalid YAML files**: Reports parsing errors with file path
- **Missing directories**: Validates directory existence before processing
- **Unsupported platforms**: Clear error messages for invalid platform names
- **File encoding issues**: Handles different text encodings automatically

## Performance Considerations

- **Large directories**: The script processes all `.yaml` files recursively
- **Memory usage**: Efficient processing of large configuration repositories
- **Error reporting**: Limited to first few errors to avoid log spam

## Security Notes

This tool is designed for **defensive security analysis only**:
- ✅ **Allowed**: Configuration analysis, vulnerability assessment, compliance checking
- ❌ **Not intended**: Malicious configuration generation, exploitation, unauthorized access

## Troubleshooting

### Common Issues

**No results found:**
- Verify YAML files are in the correct format
- Check that the directory contains `.yaml` files
- Ensure the platform name is spelled correctly

**YAML parsing errors:**
- Validate YAML syntax using an online YAML validator
- Check for proper indentation and structure
- Look for special characters that might break parsing

**Permission errors:**
- Ensure read access to the target directory
- Check file permissions on YAML configuration files

### Debug Mode
Add verbose output by modifying the script to include debug information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

This tool is part of a security analysis toolkit. When contributing:
1. Maintain focus on defensive security use cases
2. Add comprehensive error handling
3. Include examples for new features
4. Update documentation for any API changes

## License

This tool is provided for educational and defensive security purposes.