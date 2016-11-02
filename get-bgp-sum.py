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
    STARTSTRING_RE = re.compile(r'(BGP router identifier\s\S+\slocal AS number\s\d+)')
    #STARTSTRING_RE = re.compile(r'(Neighbor\s+V\s+AS\s+MsgRcvd\s+MsgSent\s+TblVer\s+InQ\s+OutQ\s+Up\/Down\s+State\/PfxRcd\n)')

    # REMOVE '--More--         ' from putty line breaks

    with open (input,'r') as rawfile:
        raw = rawfile.read()
        raw_sanitised = re.sub(MORE_RE, '', raw)
        hostname = re.search(HOSTNAME_RE, raw_sanitised)

        # Find hostname and derive ending marker
        hostname_value = hostname.group(1)
        endstring_value = hostname_value+'#'

        # Find start of "show ip bgp summary" output
        startstring = re.search(STARTSTRING_RE, raw_sanitised)
        startstring_value = startstring.group(1)

        # Convert to list
        contents = raw_sanitised.split('\n')

        # Find start index and slice list
        marker_start = contents.index(startstring_value)
        contents_start = contents[marker_start:]

        # Find first iteration of end marker i.e. the CLI prompt which is the hostname
        for x in contents_start:
            if x.startswith(endstring_value):
                marker_end = contents_start.index(x)
                break

        # Slice list again
        show_output = contents_start[:marker_end]

        # CONVERT BACK TO STRING AND REMOVE LINE BREAKS
        output = ('\n'.join(map(str.rstrip, show_output)))

        # GENERATE OUTPUT FILENAME BASED ON HOSTNAME
        output_file = str(hostname.group(1)+'.show.ip.bgp.sum'+'.csv')

        # Run TextFSM against output block using predefined template
        template = open("get-bgp-sum.template")
        re_table = textfsm.TextFSM(template)
        fsm_results = re_table.ParseText(output)
        print(fsm_results)

        # WRITE SHOW IP BGP SUMMMARY
        WriteListToCSV(output_file,['Local Router-ID','Local AS','Remote AS','Remote IP','Uptime','Received','State'],fsm_results)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-bgp-sum.py <raw IOS config file with additional stuff >")
    input = sys.argv[1]
    split_file(input)