# dod_certs_to_mobileconfig

This script will connect to the DOD PKE library and download the latest bundle of PKI certificates.  It will extract the contents, and generate a .mobileconfig file that can be used to deploy the certificates to managed systems.

```
Usage: dod_certs_to_mobileconfig.py [options]
       Run 'dod_certs_to_mobileconfig.py --help' for more information.

Options:
  -h, --help            show this help message and exit
  -r, --removal-allowed
                        Specifies that the profile can be removed.
  --organization=ORGANIZATION
                        Cosmetic name for the organization deploying the
                        profile.
  -o PATH, --output=PATH
                        Output path for profile. Defaults to '<name of DOD
                        Cert file>.mobileconfig' in the current working
                        directory.
```