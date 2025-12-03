# profile_parse.py

This python script will analyze the output of the `profiles` command to determine if keys are being set in muliple profiles. This is useful when troubleshooting settings that are applied incorrectly. If multiple profiles apply the same keys in the same domain, it is undermined which setting macOS will apply to the system. This tool helps identify which profiles may be duplicating the settings across the system.

