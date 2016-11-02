import os
import re
import sys
import pprint



def split_file(input, startstring, matchstring):

    USERNAME_RE = re.compile(r'username\s(.+)')
    ENABLE_RE = re.compile(r'enable\ssecret\s(.+)')
    SNMPCOMMUNITY_RE = re.compile(r'snmp-server\scommunity\s\S+(\s.+)')
    SNMPSERVER_RE = re.compile(r'snmp-server\shost\s(\S+)\s\S+')
    TACACS_RE = re.compile(r'tacacs-server\skey(\s\S+)\s\S+')
    NTP_RE = re.compile(r'ntp\sauthentication-key(\s\S+\s\S+\s)\S+\s\S+')
    HOSTNAME_RE = re.compile(r'hostname\s(\S+)')
    MORE_RE = re.compile(r' --More--         ')


### REMOVE '--More--         ' from putty line breaks AND GENERATE WORKING FILE

    with open (input,'r') as rawfile:
        raw = rawfile.read()
        raw_sanitised = re.sub(MORE_RE, '', raw)
        text_file = open('temp.txt', "w")
        text_file.write(raw_sanitised)

### EXTRACT AND SANITISE CONFIGURATION FROM WORKING FILE
    with open('temp.txt','r') as rawfile:
        contents = rawfile.readlines()

        # FIND START AND END OF CONFIG
        marker_start = contents.index(startstring)
        marker_end = contents.index(matchstring)
        config_list = contents[marker_start:marker_end]

        # CONVERT TO STRING AND REMOVE LINE BREAKS
        config_string = ('\n'.join(map(str.rstrip, config_list)))

        # GENERATE OUTPUT FILENAME BASED ON HOSTNAME
        hostname = re.search(HOSTNAME_RE,config_string)
        output = str(hostname.group(1)+'.cfg')

        # SANITISE PASSWORDS
        username_sanitised = re.sub(USERNAME_RE,'username XXXXXX',config_string)
        enable_sanitised = re.sub(ENABLE_RE, 'enable secret XXXXXX', username_sanitised)
        snmpcommunity_sanitised = re.sub(SNMPCOMMUNITY_RE, 'snmp-server community XXXXXX\g<1>', enable_sanitised)
        snmpserver_sanitised = re.sub(SNMPSERVER_RE, 'snmp-server host \g<1> XXXXXX', snmpcommunity_sanitised)
        tacacs_sanitised = re.sub(TACACS_RE, 'tacacs-server key \g<1> XXXXXX', snmpserver_sanitised)
        ntp_sanitised = re.sub(NTP_RE, 'ntp authentication-key \g<1> XXXXXX', tacacs_sanitised)

        sanitised = ntp_sanitised
        # WRITE CONFIG FILE
        text_file = open(output, "w")
        text_file.write(sanitised)

        # CLEANUP WORKING FILE
        os.remove('temp.txt')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-config.py <raw IOS config file with additional stuff - uses the 'Building configuration...' as start and (regex) '$end\n' as markers >")
    input = sys.argv[1]
    startstring = 'Building configuration...\n'
    matchstring = 'end\n'
    split_file(input, startstring, matchstring)