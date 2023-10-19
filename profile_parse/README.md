# macos
This is a collection of things I've found useful throughout my days as a Mac admin.

## dod_certs_mobileconfig
This script is used to download the latest DOD certificates from public.cyber.mil and generate a .mobileconfig file for use when deploying via MDM.
## macOS_openssl-ca
This is a forked version of https://github.com/llekn/openssl-ca.git, modified specifically for macOS and the generation of self-signed certificates used in a PIV implementation on test YubiKeys.

## p7b_to_mobileconfig
This script is used to take certificate bundles (.p7b) and build a configuration profile (.mobileconfig) that can be used in Jamf Pro or any other MDM to distribute certificates. It can read multiple .p7b files, extract the certificates from them and build a single .mobileconfig file containing all of the certificates.