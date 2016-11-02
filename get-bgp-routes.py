#### NOT WORKING

import os
import re
import sys
import csv
import pprint
import textfsm

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


def split_file(input):

    HOSTNAME_RE = re.compile(r'hostname\s(\S+)')
    MORE_RE = re.compile(r' --More--         ')
    STARTSTRING_RE = re.compile(r'([ ]{1,6}Network          Next Hop            Metric LocPrf Weight Path)')

### REMOVE '--More--         ' from putty line breaks AND GENERATE WORKING FILE

    with open (input,'r') as rawfile:
        raw = rawfile.read()
        raw_sanitised = re.sub(MORE_RE, '', raw)
        hostname = re.search(HOSTNAME_RE, raw_sanitised)
        hostname_value = hostname.group(1)
        endstring_value = hostname_value+'#'

        startstring = re.search(STARTSTRING_RE, raw_sanitised)
        startstring_value = startstring.group(1)

        contents = raw_sanitised.split('\n')


        # FIND START AND END OF SHOW IP OSPF NEI
        marker_start = contents.index(startstring_value)
        contents_start = contents[marker_start:]

        for x in contents_start:
            if x.startswith(endstring_value):
                marker_end = contents_start.index(x)
                break

        show_output = contents_start[:marker_end]

        # CONVERT TO STRING AND REMOVE LINE BREAKS
        output = ('\n'.join(map(str.rstrip, show_output)))

        # GENERATE OUTPUT FILENAME BASED ON HOSTNAME

        output_file = str(hostname.group(1)+'.show.ip.bgp'+'.csv')

        # debug
        #file = open("test-show-ip-bgp.txt", "w")
        #file.write(output)

        template = open("get-bgp-routes.template")
        re_table = textfsm.TextFSM(template)
        fsm_results = re_table.ParseText(output)

        # WRITE SHOW IP BGP
        WriteListToCSV(output_file,['*','r','>','m','i','PREFIX','NEXTHOP','METRIC','LOCALPREF','WEIGHT','AS_PATH','ORIGIN'],fsm_results)

        # CLEANUP WORKING FILE

if __name__ == '__main__':
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-bgp-sum.py <raw IOS config file with additional stuff >")
    input = sys.argv[1]
    split_file(input)