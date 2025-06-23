"""Apple Device Management Configuration Parser

This script parses Apple device management YAML configuration files to extract
and display payload keys for specific platforms (macOS, iOS, visionOS).
"""

import argparse
import os
import yaml
from collections import defaultdict
from tabulate import tabulate
from typing import Dict, List, Optional, Any

def normalize_platform(value: str) -> str:
    """Normalize platform string to standardized format.
    
    Args:
        value: Platform string (case-insensitive)
        
    Returns:
        Normalized platform string (macOS, iOS, or visionOS)
        
    Raises:
        argparse.ArgumentTypeError: If platform is not supported
    """
    value = value.lower()
    if value in ["macos", "mac"]:
        return "macOS"
    elif value in ["ios"]:
        return "iOS"
    elif value in ["visionos", "vision"]:
        return "visionOS"
    else:
        raise argparse.ArgumentTypeError(f"Unsupported platform: {value}")

def find_keys(directory: str, options: argparse.Namespace) -> None:
    """Find and extract payload keys from YAML configuration files.
    
    Searches through all YAML files in the specified directory and extracts
    payload keys that match the specified platform and OS version filter.
    
    Args:
        directory: Directory path to search for YAML files
        options: Parsed command line arguments containing platform and OS filter
    """
    platform = options.platform
    os_filter = options.os_filter
    results = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            # Try payloadkeys first
                            payload_keys = data.get("payloadkeys")
                            if isinstance(payload_keys, list):
                                for payload_key in payload_keys:
                                    match = extract_os_key(payload_key, platform)
                                    if match:
                                        results[file_path].append(match)
                            
                            # If no payloadkeys found, try payload
                            if not results[file_path]:
                                payload = data.get("payload")
                                if isinstance(payload, dict):
                                    match = extract_os_key(payload, platform)
                                    if match:
                                        results[file_path].append(match)
                                        
                except (yaml.YAMLError, IOError, UnicodeDecodeError) as e:
                    print(f"Error processing {file_path}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing {file_path}: {e}")

    print_results_table(results, os_filter)

def extract_os_key(payload_key: Dict[str, Any], platform: str) -> Optional[Dict[str, Any]]:
    """Extract OS-specific key information from payload key data.
    
    Args:
        payload_key: Dictionary containing payload key configuration
        platform: Target platform (macOS, iOS, or visionOS)
        
    Returns:
        Dictionary with payload key name and platform-specific entries,
        or None if no valid entries found
    """
    if not isinstance(payload_key, dict):
        return None

    key_name = payload_key.get('key', 'ALL')
    supported_os = payload_key.get('supportedOS', {})
    os_keys = supported_os.get(platform, {})

    if isinstance(os_keys, dict):
        non_na_entries = {k: v for k, v in os_keys.items() if (isinstance(v, str) and v.lower() != 'n/a')}
        if non_na_entries:
            return {
                "Payload Key": key_name,
                **non_na_entries
            }

    return None

def print_results_table(results: Dict[str, List[Dict[str, Any]]], os_filter: str) -> None:
    """Print results in a formatted table.
    
    Args:
        results: Dictionary mapping file paths to lists of extracted payload keys
        os_filter: OS version filter to apply to results
    """
    if not results:
        print("No payloadKeys with non-'n/a' entries found.")
        return

    for file, matches in results.items():
        try:
            table_data = []
            for match in matches:
                if "introduced" in match:
                    if os_filter in match["introduced"]:
                        table_data.append(match)
                elif not os_filter:  # Show all results if no filter specified
                    table_data.append(match)

        except KeyError:
            table_data = []
            
        if table_data:
            print(f"\n📄 File: {file}")
            print(tabulate(table_data, headers="keys", tablefmt="grid"))

def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Parse Apple device management YAML files to extract payload keys"
    )

    parser.add_argument(
        "-p", "--platform", 
        dest="platform", 
        type=normalize_platform, 
        required=True, 
        help="Target platform: macOS, iOS, or visionOS"
    )

    parser.add_argument(
        "-o", "--os_filter", 
        dest="os_filter", 
        required=False, 
        default="", 
        help="OS version to filter results (e.g., '26' for version 26)"
    )
    
    parser.add_argument(
        "-d", "--directory",
        dest="directory",
        required=False,
        default="./",
        help="Directory to search for YAML files (default: current directory)"
    )

    options = parser.parse_args()
    
    if os.path.exists(options.directory):
        find_keys(options.directory, options)
    else:
        print(f"Directory {options.directory} does not exist.")
        exit(1)


if __name__ == "__main__":
    main()

