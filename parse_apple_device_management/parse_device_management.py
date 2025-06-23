import argparse
import os
import yaml
from collections import defaultdict
from tabulate import tabulate

def normalize_platform(value):
    value = value.lower()
    if value in ["macos", "mac"]:
        return "macOS"
    elif value in ["ios"]:
        return "iOS"
    elif value in ["visionos", "vision"]:
        return "visionOS"
    else:
        raise argparse.ArgumentTypeError(f"Unsupported platform: {value}")

def find_keys(directory, options):
    platform = options.platform
    os_filter = options.os_filter
    results = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            # if file == "safari.settings.yaml":
            if file.endswith(".yaml"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            payload_keys = data.get("payloadkeys")
                            if isinstance(payload_keys, list):
                                for payload_key in payload_keys:
                                    match = extract_os_key(payload_key, platform)
                                    if match:
                                        results[file_path].append(match)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                
                if not results[file_path]:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = yaml.safe_load(f)
                            if isinstance(data, dict):
                                payload = data.get("payload")
                                if isinstance(payload, dict):
                                    match = extract_os_key(payload, platform)
                                    if match:
                                        results[file_path].append(match)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

    print_results_table(results, os_filter)

def extract_os_key(payload_key, platform):
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

def print_results_table(results, os_filter):
    if not results:
        print("No payloadKeys with non-'n/a' entries found.")
        return

    for file, matches in results.items():
        try:
            # table_data = [match for match in matches if "26" in match["introduced"]]
            table_data = []
            for match in matches:
                if "introduced" in match:
                    if os_filter in match["introduced"]:
                        table_data.append(match)

        except KeyError:
            table_data = []
        # headers = table_data[0].keys() if table_data else []
        if table_data:
            print(f"\n📄 File: {file}")
            print(tabulate(table_data, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(__file__)

    # Platform values
    parser.add_argument("-p", "--platform", dest="platform", type=normalize_platform, required=True, help="macOS, iOS, visionOS")

    parser.add_argument("-o", "--os_filter", dest="os_filter", required=False, default="", help="Version of OS to filter results on")

    # Process command line
    options = parser.parse_args()
    
    directory = './'
    if os.path.exists(directory):
        find_keys(directory, options)
    else:
        print(f"Directory {directory} does not exist.")

