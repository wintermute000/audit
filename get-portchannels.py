from ciscoconfparse import CiscoConfParse
from ciscoconfparse.ccp_util import IPv4Obj
from netaddr import *
import re
import sys
import csv
from pprint import pprint

def WriteListToCSV(csv_file,csv_columns,data_list):
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(csv_columns)
            for data in data_list:
                writer.writerow(data)
    except IOError as (errno, strerror):
            print("I/O error({0}): {1}".format(errno, strerror))
    return


def get_portchannels(config,output):

    # Compile Regex
    ADDR_RE = re.compile(r'ip\saddress\s(\S+\s+\S+)')
    PORTCHANNEL_RE = re.compile(r'^interface\sPort-channel\d+$')
    INTF_RE = re.compile(r'interface\s\S+')
    MEMBER_RE = re.compile(r'(channel-group\s\d+\smode\s\D+)')
    PROTOCOL_RE = re.compile(r'channel-protocol\s(\S+)')
    SHUTDOWN_RE = re.compile(r'(^\sshutdown$)')
    L2MTU_RE = re.compile(r'mtu\s(\S+)')
    DESCRIPTION_RE = re.compile(r'description\s(.+)')

    # Instantiate ciscoconfparse object from show run file and master interface list
    show_run = CiscoConfParse(config)
    interfaces_list = []
    portchannels_raw = []
    portchannels_list = []
    portchannels_master = []

    # Get list of all physical port-channels
    portchannels_raw = show_run.find_objects(PORTCHANNEL_RE)

    for obj in portchannels_raw:
        portchannel = obj.text[10:]
        shutdown = obj.re_match_iter_typed(SHUTDOWN_RE, result_type=str, default=' Up')[1:]
        portchannels_list.append([portchannel,shutdown])
    portchannels_master = [list(i) for i in portchannels_list]


    # Iterate through all physical interfaces and find member
    interfaces_raw = show_run.find_objects_w_child(parentspec=INTF_RE,childspec=MEMBER_RE)

    for obj in interfaces_raw:
        interface = obj.text[10:]
        channelgroup_raw = obj.re_match_iter_typed(MEMBER_RE, result_type=str)
        shutdown = obj.re_match_iter_typed(SHUTDOWN_RE, result_type=str, default='No Shutdown')
        l2_mtu = obj.re_match_iter_typed(L2MTU_RE, result_type=str, default='default')
        description = obj.re_match_iter_typed(DESCRIPTION_RE, result_type=str, default='no description')
        channelgroup_member = channelgroup_raw.split()[1]
        channelgroup_mode = channelgroup_raw.split()[3]
        if channelgroup_mode == 'active':
            protocol = 'lacp'
        if channelgroup_mode == 'passive':
            protocol = 'lacp'
        if channelgroup_mode == 'desirable':
            protocol = 'pagp'
        if channelgroup_mode == 'auto':
            protocol = 'pagp'
        if channelgroup_mode == 'on':
            protocol = 'static'
        for sublist in portchannels_master:
            if (str(sublist[0])[12:]) == channelgroup_member:
                if len(sublist) == 2:
                    sublist.append(channelgroup_member)
                    sublist.append(description)
                    sublist.append(protocol)
                    sublist.append(l2_mtu)
                    sublist.append(channelgroup_mode)
                    sublist.append(interface)
                    sublist.append(shutdown)
                else:
                    sublist.append(interface)
                    sublist.append(shutdown)
                    continue

    pprint(portchannels_master)
    WriteListToCSV(output,['Port-channel','Shutdown','Group','Description','Protocol','L2 MTU','Mode','Member-1','Member-1 Up','Member-2','Member-2 Up','Member-3','Member-3 Up','Member-4','Member-4 Up'],portchannels_master)




if __name__ == '__main__':
    # Input parameters
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-portchannels.py <raw IOS config file>")
    config = sys.argv[1]
    output = str('./outputs/'+(sys.argv[1])+'.portchannels.csv')
    print("Configuration File = "+config)
    print("Output File = "+output)
    get_portchannels(config,output)

