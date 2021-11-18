#!/usr/bin/python3

# Title         : dod_certs_to_mobileconfig.py
# Description   : This script will download the DOD certificates from https://public.cyber.mil and
#                 generate a .mobileconfig file for use with an MDM.
# Author        : Dan Brodjieski <brodjieski@gmail.com>
# Date          : 11/17/2021
# Version       : 0.1
# Changelog     : 11/17/2021 - Initial Script

import urllib.request
import ssl
import zipfile
import io
import os
import tempfile
import subprocess
import sys
import os.path
import optparse
import re
from plistlib import Data, writePlist, dump
from uuid import uuid4
from html.parser import HTMLParser
from urllib.parse import urlparse

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
    The actual plist content can be accessed as a dictionary via the 'data' attribute.
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
        PayloadContent dict within the payload. Handles the boilerplate, naming and descriptive
        elements.
        """
        payload_dict = {}
        # Boilerplate
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

        # Add our actual MCX/Plist content
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

        name_regex_pattern = '(^subject.*)((?<=CN=)>*?.*)'
        name_regex = re.compile(name_regex_pattern, flags=re.MULTILINE)
        name = name_regex.search(pemfile).group(2)
        
        issuer_regex_pattern = '(^issuer.*)((?<=CN=)>*?.*)'
        issuer_regex = re.compile(issuer_regex_pattern, flags=re.MULTILINE)
        issuer = issuer_regex.search(pemfile).group(2)
        
        # get type
        if issuer == name:
            certtype = "root"
        else:
            certtype = "intermediate"

        print(payload_content)
        

        self._addCertificatePayload(Data(bytes(payload_content, 'utf-8')), name, certtype)

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

def extract_dod_cert_url(content):
    """ Takes the html content and parses the href tags to collect links.  Looks for the DoD.zip in the links and returns that URL"""
    parser = URLHtmlParser()
    parser.feed(content)
    for url in parser.links:
        if "DoD.zip" in url:
            return url

def extract_dod_cert_zip_file(zip_url, tempdir):
    """ Takes the URL to the .zip file and extracts the contents to a temp directory.  Returns the location of the .pem file for processing"""
    r = urllib.request.urlopen(url=zip_url)
    z = zipfile.ZipFile(io.BytesIO(r.read()))
    z.extractall(tempdir)
    return    

def find_p7b_file(tempdir):
    """ Attempts to return the path to the pkcs7 bundle file containing all of the certificates"""
    for dirpath, subdir, files in os.walk(tempdir):
        for file in files:
            if "DoD.pem.p7b" in file:
                return os.path.join(dirpath, file), os.path.basename(dirpath)

def main():
    # set up argument parser
    parser = optparse.OptionParser()
    parser.set_usage(
        """usage: %prog [options]
       Run '%prog --help' for more information.""")

    # Optionals
    parser.add_option('--removal-allowed', '-r',
        action="store_true",
        default=False,
        help="""Specifies that the profile can be removed.""")
    parser.add_option('--organization',
        action="store",
        default="",
        help="Cosmetic name for the organization deploying the profile.")
    parser.add_option('--output', '-o',
        action="store",
        metavar='PATH',
        help="Output path for profile. Defaults to '<name of DOD Cert file>.mobileconfig' in the current working directory.")


    options, args = parser.parse_args()

    if len(args):
        parser.print_usage()
        sys.exit(-1)

    # create working directory
    tempdir = tempfile.mkdtemp()
    pem_file = tempdir + "/dod.txt"
    pem_file_prefix = tempdir + "/DoD_CA-"


    # URL to the DOD PKE library, will parse its contents to locate the .zip file to process
    pke_library_url = "https://public.cyber.mil/pki-pke/pkipke-document-library/"

    # setup SSL connection to ignore SSL warnings
    # ctx = ssl.create_default_context()
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE

    pke_site_contents = urllib.request.urlopen(url=pke_library_url)

    pke_bytes = pke_site_contents.read()
    pke_site_contents_string = pke_bytes.decode("utf8")
    pke_site_contents.close()

    certificate_url = extract_dod_cert_url(pke_site_contents_string)

    extract_dod_cert_zip_file(certificate_url, tempdir)

    # extract the certificates in .pem format from the p7b file
    pem_bundle_file, pem_title = find_p7b_file(tempdir)
    process = subprocess.Popen(
        ["openssl", "pkcs7", "-in", pem_bundle_file, "-print_certs", "-out", pem_file],
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
    if options.output:
        output_file = options.output
    else:
        output_file = os.path.join(os.getcwd(), pem_title + '.mobileconfig')

    newPayload = ConfigurationProfile(identifier=pem_title,
        uuid=False,
        removal_allowed=options.removal_allowed,
        organization=options.organization,
        displayname=pem_title)
    
    for cert in os.listdir(tempdir):
        if cert.startswith("DoD_CA-"):
            f = open(os.path.join(tempdir, cert), 'r')
            certData = f.read()
            newPayload.addPayloadFromPEM(certData)
            continue
        else:
            continue
    		
    newPayload.finalizeAndSave(output_file)

if __name__ == "__main__":
    main()