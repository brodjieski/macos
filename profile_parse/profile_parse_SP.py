#!/usr/bin/env python3

# Title         : profile_parse.py
# Description   : Script that will analyze the applied configuration profiles and report on duplicate keys being set
# Author        : Dan Brodjieski, NASA - CSET <dan.brodjieski@nasa.gov>
# Date          : 2023-03-29
# Version       : 1.0
# Changelog     : 2023-03-29 - Initial Script   
# Notes         : In order to run this, you must run the script with sudo, as the profiles command requires sudo.
#                 This is only tested on macOS Ventura, but I believe will work on macOS Monterey. 
#                 Adapted from an original script from Bob Gendler https://gist.github.com/boberito/9bf7294cb206735ab482d60707714393

import plistlib
import subprocess
import os
import sys
import textwrap
import json
import pprint

def check_values(x):
    same_values = True
    same_keys = False

    values = []
    keys = []

    for d in x:
        for k,v in d.items():
            values.append(v)
            if k in keys:
                same_keys = True
            keys.append(k)
    
    ele = values[0]
    for value in values:
        if ele != value:
            same_values = False
            break

    return same_values, same_keys

def main():


    
    cmd = 'system_profiler -json SPConfigurationProfileDataType'

    profiles_bytes = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE).stdout
    profiles_dict = json.loads(profiles_bytes)
    pprint.pprint(profiles_dict)
    for i in profiles_dict['SPConfigurationProfileDataType']:
        for profile in i['_items']:
            print(f'*** {profile["_name"]} ***')
            for payload in profile['_items']:
                # print(payload["_name"])
                if "spconfigprofile_payload_data" in payload.keys():
                    continue
                    #print(payload["spconfigprofile_payload_data"])
                else:
                    for k,v in payload.items():
                        print(payload["_name"])                            
            # for k,v in item.items():
            #     print(item['_name'])
    key_dict = {}

    # for profile in profiles_dict["_computerlevel"]:
    #     for items in profile["ProfileItems"]:
    #         for key,value in items["PayloadContent"].items():
    #             if key == "PayloadContentManagedPreferences":               
    #                 for k,v in items["PayloadContent"]['PayloadContentManagedPreferences'].items():
    #                     for mcx in items["PayloadContent"]['PayloadContentManagedPreferences'][k]['Forced']:
    #                         for mcx_k,mcx_v in mcx['mcx_preference_settings'].items():
    #                             if mcx_k in key_dict:
    #                                 key_dict[mcx_k].append({profile["ProfileDisplayName"] : mcx_v})
    #                             else:
    #                                 key_dict[mcx_k] = [{profile["ProfileDisplayName"] : mcx_v}]
    #             else:
    #                 if key in key_dict:
    #                     key_dict[key].append({profile["ProfileDisplayName"]: value})
    #                 else:
    #                     key_dict[key] = [{profile["ProfileDisplayName"]: value}]

    for k,v in key_dict.items():
        if len(v) > 1:
            values_match, keys_match = check_values(v)

            if keys_match:
                continue
            else:
                print('\033[93m' + f'\n{k}' + '\033[0m')
                if values_match:
                    color = '\033[92m'
                else:
                    color = '\033[91m'

                for item in v:    
                    for profile_name, value in item.items():
                        if len(str(value)) > 60:
                            print(f'{profile_name} : ' + color + f'{str(value)[:60]}...' + '\033[0m')   
                        else:
                            print(f'{profile_name} : ' + color + f'{str(value)}' + '\033[0m')

    infoblob = 'Output indicates that multiple configuration profiles are defining values for the duplicate keys. This may result in unexpected behavior. For any keys (yellow) listed, the corresponding profile names, along with the values are provided. The values in green are the same, while values in red are different and may need review. Values have been truncated for readability.  NOTE: There are a number of keys that can be defined in multiple profiles with differing values. These are typically in application specific profiles, or seen in networking profiles or PPPC profiles. Red values in output do not necessarily indicate a problem, but rather listed to be reviewed.'

    print(f'\n\n***** INFORMATION *****')
    print(textwrap.fill(infoblob, 120))

if __name__ == '__main__':                                                      
    main() 