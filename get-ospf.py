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


def get_ospf(config,output,redundant_nopassive):

    # Compile Regex
    NETWORK_RE = re.compile(r'network\s\S+')
    NOPASSIVE_RE = re.compile(r'no passive-interface ')
    ADDR_RE = re.compile(r'ip\saddress\s(\S+\s+\S+)')

    # Instantiate ciscoconfparse object from show run file
    show_run = CiscoConfParse(config)

    # Instantiate interface network dictionary and master ospf list
    interface_network_dict = {}
    ospf_master = []
    passive_found = []
    passive_notfound = []

    # Find all interfaces with an IP address configured
    # and iterate results into output file

    ip_interface_all_objs = show_run.find_objects_w_child(parentspec='^interface',childspec=r'ip\saddress\s(\S+)')
    for obj in ip_interface_all_objs:
    # Iterate and find IP network addresses and convert to reverse wildcard, create dictionary
        obj_ip = obj.re_match_iter_typed(ADDR_RE, result_type=IPv4Obj)
        int_name = obj.text[10:]
        int_network = str(obj_ip.network)
        int_hostmask = str(obj_ip.hostmask)
        row = int_network + ' ' + int_hostmask
        dict = {row:int_name}
        interface_network_dict.update(dict)

    # Iterate and output all OSPF network statements - extract matching interface from dict and append to master list
    ospf_obj = show_run.find_objects("^router ospf")
    for obj in ospf_obj:
        ospf_net = obj.re_search_children(NETWORK_RE)
        for line in ospf_net:
            ospf_statement = line.text
            ospf_list = ospf_statement.split()
            ospf_net = str(ospf_list[1]+' '+ospf_list[2])
            ospf_area = str(ospf_list[3]+' '+ospf_list[4])
            ospf_int = interface_network_dict.get(ospf_net)
            row = [ospf_net,ospf_area,ospf_int]
            ospf_master.append(row)

    # Iterate and output 'no passive-interface' statements checking against interface - assumes 'passive-interface default'
    for obj in ospf_obj:
        ospf_passive = obj.re_search_children(NOPASSIVE_RE)
        for line in ospf_passive:
            passive_int = str(line.text)[22:]
            for entry in ospf_master:
                if str(entry[2]) == passive_int:
                    entry.append('Y')
                    passive_found.append(str(entry[2]))

    # Iterate and output redundant passive-interface statements - assumes 'passive-interface default'
    for obj in ospf_obj:
        ospf_passive2 = obj.re_search_children(NOPASSIVE_RE)
        for line2 in ospf_passive2:
            passive_int2 = str(line2.text)[22:]
            if passive_int2 not in passive_found:
                passive_notfound.append(str(line2.text))
            else:
                continue

    # Write OSPF interfaces to CSV
    pprint(ospf_master)
    WriteListToCSV(output,['Network','Area','Interface','No Passive-Int?'],ospf_master)

    # Write redundant passive-interfaces interfaces to text

    pprint('*******NO PASSIVE-INTERFACE COMMANDS REDUNDANT*******')
    pprint(passive_notfound)

    text_file = open(redundant_nopassive, "w")
    text_file.write("NO-PASSIVE INTERFACES WITH NO MATCHING NETWORK STATEMENT / INTERFACE\n")
    for item in passive_notfound:
        text_file.write("%s\n" % item)



if __name__ == '__main__':
    # Input parameters
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-ospf.py <raw IOS config file>")
    config = sys.argv[1]
    output = str('./outputs/'+(sys.argv[1])+'.ospf.networks.csv')
    redundant_nopassive = str('./outputs/'+(sys.argv[1])+'.ospf.nopasv.csv')
    print("Configuration File = "+config)
    print("Output File = "+output)
    print("Redundant No Passive-Interface File = "+redundant_nopassive)
    get_ospf(config,output,redundant_nopassive)

