# macOS_openssl-ca

This is a forked version of https://github.com/llekn/openssl-ca.git, modified specifically for macOS and the generation of self-signed certificates used in a PIV implementation on test YubiKeys.

__Notice:__ This is meant for testing purposes only.  The certificates generated within are self-signed and self-hosted. They are not meant for production use.

## Getting started

1. __Clone this repo__
2. __Run `create_ca.sh`__ to create your root CA certificate and private key. The root CA certificate will be stored on the `./CA` folder named `ca.crt` and the private key will be stored in `./CA/private/ca.key`. You should call this script only once, as it will overwrite any existing CA key and CA certificate already present on the repo. Remember the passphrase used when creating the CA, as it will be needed to request additonal certificates in the next step.
3. __Create as many PIV certificates you want__, using `create_piv_certs.sh`. The keys, CSRs and certificates generated will be stored in the `./out/` folder.  This process will generate a PIV authentication certificate as well as a key management certificate. You will be prompted for some information including the desired UPN (NT Principal Name), this is typically used in attribute matching for PIV authentication on macOS.
4. __Ready!__ You can load the certificates onto a Yubikey using the Yubikey manager to create a PIV-compatible token. You will need to trust the issuing CA in order for your Mac to trust the generated certificates. The certificates you should add to your System Keychain is located in `./CA/ca.crt`. 

__Warning__: Adding `ca.crt` to your list of trusted CA means that your Mac will trust any certificate signed by `./CA/private/ca.key`.  __Keep this key private!!__ (Ideally offline)

Running the `clean.sh` script will clear out all generated certificates allowing you to start from scratch if need be.  