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


def get_interfaces(config,output):

    # Compile Regex
    INTF_RE = re.compile(r'interface\s\S+')
    ADDR_RE = re.compile(r'ip\saddress\s(\S+\s+\S+)')
    DESCRIPTION_RE = re.compile(r'description\s(.+)')
    STATIC_RE = re.compile(r'ip\sroute\s(\S+)')
    L2MTU_RE = re.compile(r'mtu\s(\S+)')
    L3MTU_RE = re.compile(r'ip mtu\s(\S+)')
    OSPFNETTYPE_RE = re.compile(r'ip ospf\snetwork\s(\S+)')
    OSPFHELLO_RE = re.compile(r'ip ospf\shello-interval\s(\S+)')
    OSPFDEAD_RE = re.compile(r'ip ospf\sdead-interval\s(.S+)')
    SHUTDOWN_RE = re.compile(r'(^shutdown$)')
    BFD_RE = re.compile(r'bfd\s(interval\s.+)')

    # Instantiate ciscoconfparse object from show run file and master interface list
    show_run = CiscoConfParse(config)
    interface_master = []

    # Find all interfaces with an IP address configured
    # and iterate results into output file
    ip_interface_all_objs = show_run.find_objects_w_child(parentspec='^interface',childspec=r'ip\saddress\s(\S+)')

    for obj in ip_interface_all_objs:

    # Iterate and find IP address parameters
        obj_ip = obj.re_match_iter_typed(ADDR_RE, result_type=IPv4Obj)
        int_name = obj.text[10:]
        int_ip = obj_ip.ip
        int_mask = obj_ip.netmask

    # Iterate and find description / shutdown
        shutdown = obj.re_match_iter_typed(SHUTDOWN_RE, result_type=str, default='No Shutdown')
        description = obj.re_match_iter_typed(DESCRIPTION_RE, result_type=str, default='no description')

    # Iterate and find MTU parameters
        l2_mtu = obj.re_match_iter_typed(L2MTU_RE, result_type=str, default='default')
        #l3_mtu = obj.re_match_iter_typed(L3MTU_RE, result_type=str, default='default')

    # Iterate and find OSPF parameters
        ospf_nettype = obj.re_match_iter_typed(OSPFNETTYPE_RE, result_type=str, default='broadcast')
        ospf_hello = obj.re_match_iter_typed(OSPFHELLO_RE, result_type=str, default='default')
        ospf_dead = obj.re_match_iter_typed(OSPFDEAD_RE, result_type=str, default='default')

        bfd = obj.re_match_iter_typed(BFD_RE, result_type=str, default='N')

        row=[int_name,int_ip,int_mask,description, shutdown, l2_mtu, ospf_nettype, ospf_hello, ospf_dead, bfd]
        interface_master.append(row)
    # Debug
        pprint(row)

    # Write interfaces to CSV
    WriteListToCSV(output,['Interface','IP','Netmask','Description','Shutdown','L2 MTU', 'OSPF Network Type','OSPF Hello interval','OSPF Dead interval','BFD'],interface_master)

if __name__ == '__main__':
    # Input parameters
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-interfaces.py <raw IOS config file>")
    config = str(sys.argv[1])
    output = str('./outputs/'+(sys.argv[1])+'.interfaces.csv')
    print("Configuration File = "+config)
    print("Output File = "+output)
    get_interfaces(config,output)

