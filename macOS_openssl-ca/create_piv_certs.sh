#!/bin/bash

# collect information

read -p "Enter full name to be used on certificate: " name
read -p "Enter NT Principal Name: " upn
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
	-config <(cat ./openssl.cnf \
			<(printf "subjectAltName = otherName:1.3.6.1.4.1.311.20.2.3;UTF8:${upn}")) \
	-newkey rsa -nodes -keyout "./out/${name}.key" \
	-out "./out/${name}.csr" -extensions v3_req \
    -subj "/O=$org/OU=$ou/emailAddress=$email/L=$city/ST=$state/C=$country/CN=$name"

chmod 600 "./out/${name}.key"

# issue cert from csr

openssl ca -batch \
    -out "./out/${name}.pem" -config ./openssl.cnf \
    -notext -extensions v3_req \
    -passin pass:"${ca_pass}" \
    -infiles "./out/${name}.csr"

# create PKCS12 bundle
openssl pkcs12 \
    -export \
    -in "./out/${name}.pem" \
    -inkey "./out/${name}.key" \
    -passout pass:"${bundle_pass}" \
    -out "./newcerts/${name}.p12"


# create csr for Key Management Cert
openssl req \
    -config ./openssl.cnf \
    -newkey rsa -nodes -keyout "./out/${name}-key_management.key" \
    -out "./out/${name}-key_management.csr" -extensions v3_key_enc \
    -subj "/O=$org/OU=$ou/emailAddress=$email/L=$city/ST=$state/C=$country/CN=$name-key_management"

chmod 600 "./out/${name}-key_management.key"

openssl ca -batch \
    -out "./out/${name}-key_management.pem" -config ./openssl.cnf \
    -extensions v3_key_enc \
    -passin pass:"${ca_pass}" \
    -infiles "./out/${name}-key_management.csr"

# create PKCS12 bundle
openssl pkcs12 \
    -export \
    -in "./out/${name}-key_management.pem" \
    -inkey "./out/${name}-key_management.key" \
    -passout pass:"${bundle_pass}" \
    -out "./newcerts/${name}-key_management.p12"

# create csr for Digital Signature Cert
openssl req \
    -config ./openssl.cnf \
    -newkey rsa -nodes -keyout "./out/${name}-digital-signature.key" \
    -out "./out/${name}-digital-signature.csr" -extensions v3_digital_sign \
    -subj "/O=$org/OU=$ou/emailAddress=$email/L=$city/ST=$state/C=$country/CN=$name-digital-signature"

chmod 600 "./out/${name}-digital-signature.key"

openssl ca -batch \
    -out "./out/${name}-digital-signature.pem" -config ./openssl.cnf \
    -extensions v3_digital_sign \
    -passin pass:"${ca_pass}" \
    -infiles "./out/${name}-digital-signature.csr"

# create PKCS12 bundle
openssl pkcs12 \
    -export \
    -in "./out/${name}-digital-signature.pem" \
    -inkey "./out/${name}-digital-signature.key" \
    -passout pass:"${bundle_pass}" \
    -out "./newcerts/${name}-digital-signature.p12"

echo "Certificates created successfully."
echo "-----------------------------------------------------------------------------------------------------"
echo -e "Import \033[1m${name}.p12\033[0m into the Authentication slot (9A) using yubikey manager."
echo -e "Import \033[1m${name}-key_management.p12\033[0m into the Key Management slot (9D) using yubikey manager."
echo -e "Password for .p12 bundles: \033[1m${bundle_pass}\033[0m"
echo -e "In order for your system to trust these certs, the issuing CA (\033[1m./CA/ca.crt\033[0m) must be added to the keychain."
echo "-----------------------------------------------------------------------------------------------------"

open ./newcerts