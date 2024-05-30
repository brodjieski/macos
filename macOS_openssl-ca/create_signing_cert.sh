#!/bin/bash

# collect information

read -p "Enter full name to be used on certificate: " name
read -p "Enter the organization name: " org
read -p "Enter the oganizational unit: " ou
read -p "Enter the email address: " email
read -p "Enter the city or locality: " city
read -p "Enter the state: " state
read -p "Enter the 2 character country: " country
read -sp "Enter passphrase for CA: " ca_pass
echo
# read -sp "Enter passphrase for generated PKCS12 bundle (will be the same for both generated bundles): " bundle_pass
bundle_pass=$(openssl rand -base64 16)

# establish CA index and serial files
if ! [[ -e "index.txt" ]];then
    touch index.txt
fi
if ! [[ -e serial ]];then
    echo "01" > serial
fi

# create csr for PIV authentication cert
openssl req \
	-config openssl.cnf \
	-new -newkey rsa:2048 -nodes -keyout "./out/${name}.key" \
	-out "./out/${name}.csr" \
    -subj "/O=$org/OU=$ou/emailAddress=$email/L=$city/ST=$state/C=$country/CN=$name"

chmod 600 "./out/${name}.key"

# issue cert from csr

openssl ca -batch \
    -out "./out/${name}.pem" -config ./openssl.cnf \
    -notext \
    -passin pass:"${ca_pass}" \
    -infiles "./out/${name}.csr"

# create PKCS12 bundle
openssl pkcs12 \
    -export \
    -in "./out/${name}.pem" \
    -inkey "./out/${name}.key" \
    -passout pass:"${bundle_pass}" \
    -out "./newcerts/${name}.p12"


echo "Certificates created successfully."
echo "-----------------------------------------------------------------------------------------------------"
echo -e "Password for .p12 bundle: \033[1m${bundle_pass}\033[0m"
echo -e "In order for your system to trust these certs, the issuing CA (\033[1m./CA/ca.crt\033[0m) must be added to the keychain."
echo "-----------------------------------------------------------------------------------------------------"

open ./newcerts