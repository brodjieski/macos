#!/usr/bin/python3

# Title         : p7b_to_mobileconfig.py
# Description   : This script will convert certificate bundles (p7b) and 
#                 generate a .mobileconfig file for use with an MDM.
# Author        : Dan Brodjieski <brodjieski@gmail.com>
# Date          : 06/01/2022
# Version       : 0.1
# Changelog     : 06/01/2022 - Initial Script

import os
import tempfile
import subprocess
import sys
import os.path
import base64
import optparse
import logging
import re
from plistlib import Data, dump
from uuid import uuid4
from html.parser import HTMLParser

class URLHtmlParser(HTMLParser):
    links = []
    
    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
            
        for attr in attrs:
            if 'href' in attr[0]:
                self.links.append(attr[1])
                break

class ConfigurationProfile:
    """Class to create and manipulate Configuration Profiles.
    """
    def __init__(self, identifier, uuid=False, removal_allowed=False, organization='', displayname=''):
        self.data = {}
        self.data['PayloadVersion'] = 1
        self.data['PayloadOrganization'] = organization
        if uuid:
            self.data['PayloadUUID'] = uuid
        else:
            self.data['PayloadUUID'] = makeNewUUID()
        if removal_allowed:
            self.data['PayloadRemovalDisallowed'] = False
        else:
            self.data['PayloadRemovalDisallowed'] = True
        self.data['PayloadType'] = 'Configuration'
        self.data['PayloadScope'] = 'System'
        self.data['PayloadDescription'] = displayname
        self.data['PayloadDisplayName'] = displayname
        self.data['PayloadIdentifier'] = makeNewUUID()
        
        # An empty list for 'sub payloads' that we'll fill later
        self.data['PayloadContent'] = []
    
    def _addCertificatePayload(self, payload_content, certname, certtype):
        """Add a Certificate payload to the profile. Takes a dict which will be the
        PayloadContent dict within the payload.
        """
        payload_dict = {}
        payload_dict['PayloadVersion'] = 1
        payload_dict['PayloadUUID'] = makeNewUUID()
        payload_dict['PayloadEnabled'] = True
        
        if certtype == 'root':
            payload_dict['PayloadType'] = 'com.apple.security.root'
            payload_dict['PayloadIdentifier'] = 'com.apple.security.root.' + payload_dict['PayloadUUID']
        else:
            payload_dict['PayloadType'] = 'com.apple.security.pkcs1'
            payload_dict['PayloadIdentifier'] = 'com.apple.security.pkcs1.' + payload_dict['PayloadUUID']
                
        payload_dict['PayloadDisplayName'] = certname
        payload_dict['AllowAllAppsAccess'] = False
        payload_dict['PayloadCertificateFileName'] = certname + ".cer"
        payload_dict['KeyIsExtractable'] = True
        payload_dict['PayloadDescription'] = "Adds a PKCS#1-formatted certificate"

        # Add our actual content
        payload_dict['PayloadContent'] = payload_content

        # Add to the profile's PayloadContent array
        self.data['PayloadContent'].append(payload_dict)


    def addPayloadFromPEM(self, pemfile):
        """Add Certificates to the profile's payloads.
        """
        payload_content = ""
        regex_pattern = '(-+BEGIN CERTIFICATE-+)(.*?)(-+END CERTIFICATE-+)'
        regex = re.compile(regex_pattern, flags=re.MULTILINE|re.DOTALL)
        cert = regex.search(pemfile)
        
        payload_content = cert.group(2)
        payload_content_ascii = payload_content.encode('ascii')
        payload_content_bytes = base64.b64decode(payload_content_ascii)
  
        try:
            name_regex_pattern = '(^subject.*)((?<=CN=)>*?.*)'
            name_regex = re.compile(name_regex_pattern, flags=re.MULTILINE)
            name = name_regex.search(pemfile).group(2)
        except:
            name_regex_pattern = '(^subject.*)((?<=OU=)>*?.*)'
            name_regex = re.compile(name_regex_pattern, flags=re.MULTILINE)
            name = name_regex.search(pemfile).group(2)
            logging.debug("Using OU for CN")
        logging.debug(f"Subject: {name}")
        
        
        try:
            issuer_regex_pattern = '(^issuer.*)((?<=CN=)>*?.*)'
            issuer_regex = re.compile(issuer_regex_pattern, flags=re.MULTILINE)
            issuer = issuer_regex.search(pemfile).group(2)
        except:
            issuer_regex_pattern = '(^issuer.*)((?<=OU=)>*?.*)'
            issuer_regex = re.compile(issuer_regex_pattern, flags=re.MULTILINE)
            issuer = issuer_regex.search(pemfile).group(2)
            logging.debug("Using OU for CN")
        logging.debug(f"Issuer: {issuer}")
        
        # get type
        if issuer == name:
            certtype = "root"
        else:
            certtype = "intermediate"
        
        self._addCertificatePayload(Data(payload_content_bytes), name, certtype)

    def finalizeAndSave(self, output_path):
        """Perform last modifications and save to an output plist.
        """
        print(f"Writing .mobileconfig file to: {output_path}")
        with open(output_path, 'wb+') as plist_file:
            dump(self.data, plist_file)


def makeNewUUID():
    return str(uuid4())


def errorAndExit(errmsg):
    print >> sys.stderr, errmsg
    exit(-1)


def main():
    # set up argument parser
    parser = optparse.OptionParser()
    parser.set_usage(
        """usage: %prog [options] file1.p7b file2.p7b ...
       Run '%prog --help' for more information.""")

    # Optionals
    parser.add_option('--debug', '-d',
        action="store_true",
        default=False,
        help="""Enable verbose output.""")
    parser.add_option('--removal-allowed', '-r',
        action="store_true",
        default=False,
        help="""Specifies that the profile can be removed.""")
    parser.add_option('--organization',
        action="store",
        default="",
        help="Cosmetic name for the organization deploying the profile.")

    options, args = parser.parse_args()

    if len(args) < 1:
        parser.print_usage()
        sys.exit(-1)
    else:
        p7b_files = args[0:]
    
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    # create working directory
    tempdir = tempfile.mkdtemp()

    pem_title = ""

    while True:
        pem_title = input("Enter a name for this configuration profile (i.e. PKI Trust) ")
        if pem_title:
            break
        else:
            print("Name cannot be blank.")

    for p7b_file in p7b_files:
        logging.debug(f"Processing p7b file: {p7b_file}")
        pem_file = tempdir + f"/{p7b_file}.txt"
        pem_file_prefix = tempdir + f"/CERT-{p7b_file}"
        pem_bundle_file = f"./{p7b_file}"
        process = subprocess.Popen(
            ["openssl", "pkcs7", "-inform", "DER", "-in", pem_bundle_file, "-print_certs", "-out", pem_file],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell=False
        )
        process.communicate()

        # split the .pem file into individual certificates
        split_process = subprocess.Popen(
            ["split", "-p", "subject=", pem_file, pem_file_prefix],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell=False
        )
        split_process.communicate()

    # setup output file
    build_path = os.path.join(os.getcwd(), 'build')
    if not os.path.exists(build_path):
      os.makedirs(build_path)
    
    output_file = os.path.join(build_path, pem_title + '.mobileconfig')

    newPayload = ConfigurationProfile(identifier=pem_title,
        uuid=False,
        removal_allowed=options.removal_allowed,
        organization=options.organization,
        displayname=pem_title)

    for x, cert in enumerate(os.listdir(tempdir)):
        logging.debug(f"{x},{cert}")
        if cert.startswith("CERT-"):
            f = open(os.path.join(tempdir, cert), 'r')
            certData = f.read()
            newPayload.addPayloadFromPEM(certData)
            continue
        else:
            continue
    		
    newPayload.finalizeAndSave(output_file)

if __name__ == "__main__":
    main()