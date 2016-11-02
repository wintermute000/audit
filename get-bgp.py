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

def get_bgp(config,output_network,output_agg,output_peergrps,output_peerings):
    # Compile Regex
    NETWORK_RE = re.compile(r'network\s\d+')
    AGG_RE = re.compile(r'aggregate-address\s\S+\s\S+\s\S+\s\S+')

    NEI_PGRP_AS_RE = re.compile(r'neighbor\s\D+\sremote-as\s\d*')
    NEI_PGRP_TIMERS_RE = re.compile(r'neighbor\s\D+\stimers\s\d*\s\d*')
    NEI_PGRP_NHS_RE = re.compile(r'neig    hbor\s\D+\snext-hop-self')
    NEI_PGRP_SOFT_RE = re.compile(r'neighbor\s\D+\ssoft-reconfiguration\sinbound')
    NEI_PGRP_MAXPREFIX_RE = re.compile(r'neighbor\s\D+\smaximum-prefix\s\d*\s\d*\s\S+')
    NEI_PGRP_PEERGRP_RE = re.compile(r'neighbor\s\D+\speer-group')
    NEI_PGRP_RMIN_RE = re.compile(r'neighbor\s\D+\sroute-map\s\S+\sin')
    NEI_PGRP_RMOUT_RE = re.compile(r'neighbor\s\D+\sroute-map\s\S+\sout')
    NEI_PGRP_COMMUNITY = re.compile(r'neighbor\s\D+\ssend-community\s\S+')
    NEI_PGRP_DESCRIPTION = re.compile(r'neighbor\s\D+\sdescription\s\S+')
    NEI_PGRP_MULTIHOP = re.compile(r'neighbor\s\D+\sebgp-multihop\s\d*')
    NEI_PGRP_UPDATE = re.compile(r'neighbor\s\D+\supdate-source\s\S+')

    NEI_PEER_PEERGRP_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\speer-group\s\S+')
    NEI_PEER_AS_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\sremote-as\s\d*')
    NEI_PEER_TIMERS_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\stimers\s\d*\s\d*')
    NEI_PEER_NHS_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\snext-hop-self')
    NEI_PEER_SOFT_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\ssoft-reconfiguration\sinbound')
    NEI_PEER_MAXPREFIX_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\smaximum-prefix\s\d*\s\d*\s\S+')
    NEI_PEER_RMIN_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\sroute-map\s\S+\sin')
    NEI_PEER_RMOUT_RE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\sroute-map\s\S+\sout')
    NEI_PEER_COMMUNITY = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\ssend-community\s\S+')
    NEI_PEER_DESCRIPTION = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\sdescription\s\S+')
    NEI_PEER_MULTIHOP = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\sebgp-multihop\s\d*')
    NEI_PEER_UPDATE = re.compile(r'neighbor\s([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\supdate-source\s\S+')

    # Instantiate ciscoconfparse object from show run file and master bgp list
    show_run = CiscoConfParse(config)
    bgp_networks_master = []
    bgp_agg_master = []
    bgp_peergrps_master = []
    bgp_peerings_master = []

   # Iterate and output all BGP network statements
    bgp_obj = show_run.find_objects("^router bgp")
    for obj in bgp_obj:
        bgp_networks_all = obj.re_search_children(NETWORK_RE)
        for line in bgp_networks_all:
            bgp_network_line = (line.text)
            bgp_net_list = bgp_network_line.split()
            bgp_net = bgp_net_list[1]
            # catch class A statements with no mask
            if len(bgp_net_list) == 2:
                bgp_mask = 'none'
            else:
                bgp_mask = bgp_net_list[3]
            row = [bgp_net,bgp_mask]
            bgp_networks_master.append(row)

    pprint("*******BGP NETWORKS START************")
    pprint(bgp_networks_master)
    pprint("*******BGP NETWORKS END**************")

    WriteListToCSV(output_network,['Network','Mask'],bgp_networks_master)


##################################
    # Iterate and output all BGP aggregate statements
    bgp_obj = show_run.find_objects("^router bgp")
    for obj in bgp_obj:
        bgp_agg_all = obj.re_search_children(AGG_RE)
        for line in bgp_agg_all:
            bgp_agg_line = (line.text)
            bgp_agg_list = bgp_agg_line.split()
            bgp_agg = bgp_agg_list[1]
            bgp_mask = bgp_agg_list[2]
            bgp_advmap = bgp_agg_list[4]

            # # catch class A statements with no mask
            # if len(bgp_net_list) == 2:
            #     bgp_mask = 'none'
            # else:
            #     bgp_mask = bgp_net_list[3]

            row = [bgp_agg, bgp_mask, bgp_advmap]
            bgp_agg_master.append(row)

    pprint("*******BGP AGGREGATIONS LIST START************")
    pprint(bgp_agg_master)
    pprint("*******BGP AGGREGATIONS LIST END**************")
    WriteListToCSV(output_agg, ['Aggregate-Address', 'Mask','Advertise-Map'], bgp_agg_master)

##################################
   # Iterate and output all BGP peer group statements
    bgp_obj = show_run.find_objects("^router bgp")

    bgp_peergrp_group_list = []
    bgp_peergrp_as_list = []
    bgp_peergrp_community_list = []

    # Iterate through and generate lists
    for obj in bgp_obj:
        # Iterate through and generate list of bgp peer-group names - note this is mandatory variable
        peergrp_group = obj.re_search_children(NEI_PGRP_PEERGRP_RE)
        for line in peergrp_group:
            bgp_peergrp_group_raw = line.text[10:]
            bgp_peergrp_group = re.sub(' peer-group','',bgp_peergrp_group_raw)
            bgp_peergrp_group_list.append(bgp_peergrp_group)

        # Iterate through and generate list of bgp peer-group AS numbers - note this is mandatory variable
        peergrp_as = obj.re_search_children(NEI_PGRP_AS_RE)
        for line in peergrp_as:
            bgp_peergrp_as_raw = line.text[10:]
            #bgp_peergrp_id = re.sub('\sremote-as\s\S+','',bgp_peergrp_as_raw)
            bgp_peergrp_as = re.sub('\S+\sremote-as\s','',bgp_peergrp_as_raw)
            bgp_peergrp_as_list.append(bgp_peergrp_as)

        # List comprehension with zip function to combine two lists into 'list of lists'
        bgp_peergrps_master = [list(i) for i in zip(bgp_peergrp_group_list,bgp_peergrp_as_list)]

        # Iterate through each individual peer-group as defined from already generated list above
        for x in bgp_peergrp_group_list:

            # DESCRIPTION - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_description_searchstring = r'neighbor\s'+x+r'\sdescription\s\S+'
            for obj in bgp_obj:
                peergrp_description = obj.re_search_children(peergrp_description_searchstring)
                if peergrp_description == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no description')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_description:
                    bgp_peergrp_description_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sdescription\s.*','',bgp_peergrp_description_raw)
                    bgp_peergrp_description = re.sub('\S+\sdescription\s','',bgp_peergrp_description_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_description)

            # RR-CLIENT - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_rrclient_searchstring = r'neighbor\s'+x+r'\sroute-reflector-client'
            for obj in bgp_obj:
                peergrp_rrclient = obj.re_search_children(peergrp_rrclient_searchstring)
                if peergrp_rrclient == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_rrclient:
                    bgp_peergrp_rrclient_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sroute-reflector-client','',bgp_peergrp_rrclient_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')

            # NEXT-HOP-SELF - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_nhs_searchstring = r'neighbor\s'+x+r'\snext-hop-self'
            for obj in bgp_obj:
                peergrp_nhs = obj.re_search_children(peergrp_nhs_searchstring)
                if peergrp_nhs == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find if NHS set and add them to correct 'list of lists'
                for line in peergrp_nhs:
                    bgp_peergrp_nhs_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\snext-hop-self','',bgp_peergrp_nhs_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')

            # UPDATE SOURCE - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_update_searchstring = r'neighbor\s'+x+r'\supdate-source\s\S+'
            for obj in bgp_obj:
                peergrp_update = obj.re_search_children(peergrp_update_searchstring)
                if peergrp_update == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('default')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_update:
                    bgp_peergrp_update_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\supdate-source\s\S+','',bgp_peergrp_update_raw)
                    bgp_peergrp_update = re.sub('\S+\supdate-source\s','',bgp_peergrp_update_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_update)

            # BFD - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_bfd_searchstring = r'neighbor\s' + x + r'\sfall-over\sbfd'
            for obj in bgp_obj:
                peergrp_bfd = obj.re_search_children(peergrp_bfd_searchstring)
                if peergrp_bfd == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find if bfd set and add them to correct 'list of lists'
                for line in peergrp_bfd:
                    bgp_peergrp_bfd_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sfall-over\sbfd', '', bgp_peergrp_bfd_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')


            # SOFT-RECONFIG - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_soft_searchstring = r'neighbor\s'+x+r'\ssoft-reconfiguration\sinbound'
            for obj in bgp_obj:
                peergrp_soft = obj.re_search_children(peergrp_soft_searchstring)
                if peergrp_soft == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find if soft set and add them to correct 'list of lists'
                for line in peergrp_soft:
                    bgp_peergrp_soft_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\ssoft-reconfiguration\sinbound','',bgp_peergrp_soft_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')

            # TIMERS - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_timers_searchstring = r'neighbor\s'+x+r'\stimers\s\d*\s\d*'
            for obj in bgp_obj:
                peergrp_timers = obj.re_search_children(peergrp_timers_searchstring)
                if peergrp_timers == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('60 180')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_timers:
                    bgp_peergrp_timers_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\stimers\s\d*\s\d*','',bgp_peergrp_timers_raw)
                    bgp_peergrp_timers = re.sub('\S+\stimers\s','',bgp_peergrp_timers_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_timers)

            # MULTIHOP - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_multihop_searchstring = r'neighbor\s'+x+r'\sebgp-multihop\s\d*'
            for obj in bgp_obj:
                peergrp_multihop = obj.re_search_children(peergrp_multihop_searchstring)
                if peergrp_multihop == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no multihop')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_multihop:
                    bgp_peergrp_multihop_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sebgp-multihop\s\d*','',bgp_peergrp_multihop_raw)
                    bgp_peergrp_multihop = re.sub('\S+\sebgp-multihop\s','',bgp_peergrp_multihop_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_multihop)


            # COMMUNITY - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_community_searchstring = r'neighbor\s'+x+r'\ssend-community\s\S+'
            for obj in bgp_obj:
                peergrp_community = obj.re_search_children(peergrp_community_searchstring)
                if peergrp_community == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no community')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_community:
                    bgp_peergrp_community_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\ssend-community\s\S+','',bgp_peergrp_community_raw)
                    bgp_peergrp_community = re.sub('\S+\ssend-community\s','',bgp_peergrp_community_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_community)


            # MAXPREFIX - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_maxprefix_searchstring = r'neighbor\s'+x+r'\smaximum-prefix\s\d*\s\d*\s\S+'
            for obj in bgp_obj:
                peergrp_maxprefix = obj.re_search_children(peergrp_maxprefix_searchstring)
                if peergrp_maxprefix == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no maxprefix')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_maxprefix:
                    bgp_peergrp_maxprefix_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\smaximum-prefix\s\d*\s\d*\s\S+','',bgp_peergrp_maxprefix_raw)
                    bgp_peergrp_maxprefix = re.sub('\S+\smaximum-prefix\s','',bgp_peergrp_maxprefix_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_maxprefix)

            # DEFAULT-ORIGINATE - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_defaultorig_searchstring = r'neighbor\s' + x + r'\sdefault-originate'
            for obj in bgp_obj:
                peergrp_defaultorig = obj.re_search_children(peergrp_defaultorig_searchstring)
                if peergrp_defaultorig == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find if defaultorig set and add them to correct 'list of lists'
                for line in peergrp_defaultorig:
                    bgp_peergrp_defaultorig_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sdefault-originate', '', bgp_peergrp_defaultorig_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')


            # ROUTE-MAP IN - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_rmin_searchstring = r'neighbor\s'+x+r'\sroute-map\s\S+\sin'
            for obj in bgp_obj:
                peergrp_rmin = obj.re_search_children(peergrp_rmin_searchstring)
                if peergrp_rmin == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no route-map in')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_rmin:
                    bgp_peergrp_rmin_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sroute-map\s\S+\sin','',bgp_peergrp_rmin_raw)
                    bgp_peergrp_rmin_raw2 = re.sub('\sroute-map\s','',bgp_peergrp_rmin_raw)
                    bgp_peergrp_rmin = re.sub('\sin$','',bgp_peergrp_rmin_raw2)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_rmin)

            # ROUTE-MAP OUT - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_rmout_searchstring = r'neighbor\s'+x+r'\sroute-map\s\S+\sout'
            for obj in bgp_obj:
                peergrp_rmout = obj.re_search_children(peergrp_rmout_searchstring)
                if peergrp_rmout == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('no route-map out')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peergrp_rmout:
                    bgp_peergrp_rmout_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sroute-map\s\S+\sout','',bgp_peergrp_rmout_raw)
                    bgp_peergrp_rmout_raw2 = re.sub('\sroute-map\s','',bgp_peergrp_rmout_raw)
                    bgp_peergrp_rmout = re.sub('\sout$','',bgp_peergrp_rmout_raw2)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append(bgp_peergrp_rmout)

            # SHUTDOWN - Iterate through list - catch 'not found' and manually insert null entry
            peergrp_shutdown_searchstring = r'neighbor\s' + x + r'\sshutdown'
            for obj in bgp_obj:
                peergrp_shutdown = obj.re_search_children(peergrp_shutdown_searchstring)
                if peergrp_shutdown == []:
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == x:
                            sublist.append('N')
                # Iterate through list - find if shutdown set and add them to correct 'list of lists'
                for line in peergrp_shutdown:
                    bgp_peergrp_shutdown_raw = line.text[10:]
                    bgp_peergrp_id = re.sub('\sshutdown', '', bgp_peergrp_shutdown_raw)
                    for sublist in bgp_peergrps_master:
                        if sublist[0] == bgp_peergrp_id:
                            sublist.append('Y')


    pprint("*******BGP PEER-GROUPS START************")
    pprint(bgp_peergrps_master)
    pprint("*******BGP PEER-GROUPS END**************")
    WriteListToCSV(output_peergrps,['Peer-group','Remote-AS', 'Description', 'RR-Client', 'Next-Hop-Self', 'Update-source', 'BFD','Soft-Reconfiguration Inbound','Timers','EBGP-Multihop','Community','Max-prefix','Default-originate','Route-map In','Route-map Out','Shutdown'],bgp_peergrps_master)


#############################
       # Iterate and output all BGP peer group statements
    bgp_obj = show_run.find_objects("^router bgp")

    bgp_peerings_group_list = []
    bgp_peerings_group = []
    bgp_peerings_as_list = []
    bgp_peerings_community_list = []

    # Iterate through and generate lists
    for obj in bgp_obj:

        # Iterate through and generate list of bgp peers defined via IP address - AS numbers - note this is mandatory variable

        peerings_grp_nei = obj.re_search_children(NEI_PEER_PEERGRP_RE)
        for line in peerings_grp_nei:
            bgp_peerings_as_raw = line.text[10:]
            bgp_peerings_as = re.sub('\s\peer-group\s\S+','',bgp_peerings_as_raw)
            bgp_peerings_group_list.append([bgp_peerings_as])
            bgp_peerings_group.append(bgp_peerings_as)

        peerings_nei = obj.re_search_children(NEI_PEER_AS_RE)
        for line in peerings_nei:
            bgp_peerings_as_raw = line.text[10:]
            bgp_peerings_as = re.sub('\sremote-as\s\d*','',bgp_peerings_as_raw)
            bgp_peerings_group_list.append([bgp_peerings_as])
            bgp_peerings_group.append(bgp_peerings_as)

        bgp_peerings_master = [list(i) for i in bgp_peerings_group_list]

        # Iterate through each individual peer as defined from already generated list above
        for x in bgp_peerings_group:

            # PEER-GROUP - Iterate through list - catch 'not found' and manually insert null entry
            peerings_peergrp_searchstring = r'neighbor\s'+x+r'\speer-group\s\S+'
            for obj in bgp_obj  :
                peerings_peergrp = obj.re_search_children(peerings_peergrp_searchstring)
                if peerings_peergrp == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            sublist.append('no-peer-group')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_peergrp:
                    bgp_peerings_peergrp_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\speer-group\s.*','',bgp_peerings_peergrp_raw)
                    bgp_peerings_peergrp = re.sub('\S+\speer-group\s','',bgp_peerings_peergrp_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_peergrp)

           # REMOTE-AS - Iterate through list - catch 'not found' and manually insert null entry
            peerings_peeras_searchstring = r'neighbor\s'+x+r'\sremote-as\s\d+'
            for obj in bgp_obj  :
                peerings_peeras = obj.re_search_children(peerings_peeras_searchstring)
                if peerings_peeras == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_peeras:
                    bgp_peerings_peeras_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sremote-as\s\d*','',bgp_peerings_peeras_raw)
                    bgp_peerings_peeras = re.sub('\S+\sremote-as\s','',bgp_peerings_peeras_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_peeras)

            # DESCRIPTION - Iterate through list - catch 'not found' and manually insert null entry
            peerings_description_searchstring = r'neighbor\s'+x+r'\sdescription\s\S+'
            for obj in bgp_obj  :
                peerings_description = obj.re_search_children(peerings_description_searchstring)
                if peerings_description == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            sublist.append('no description')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_description:
                    bgp_peerings_description_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sdescription\s.*','',bgp_peerings_description_raw)
                    bgp_peerings_description = re.sub('\S+\sdescription\s','',bgp_peerings_description_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_description)
                            
            # RR-CLIENT - Iterate through list - catch 'not found' and manually insert null entry
            peerings_rrclient_searchstring = r'neighbor\s'+x+r'\sroute-reflector-client'
            for obj in bgp_obj:
                peerings_rrclient = obj.re_search_children(peerings_rrclient_searchstring)
                if peerings_rrclient == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_rrclient:
                    bgp_peerings_rrclient_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sroute-reflector-client','',bgp_peerings_rrclient_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append('Y')
                            
            # NEXT-HOP-SELF - Iterate through list - catch 'not found' and manually insert null entry or manually note peer-group member
            peerings_nhs_searchstring = r'neighbor\s'+x+r'\snext-hop-self'
            for obj in bgp_obj:
                peerings_nhs = obj.re_search_children(peerings_nhs_searchstring)
                if peerings_nhs == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find if NHS set and add them to correct 'list of lists'
                for line in peerings_nhs:
                    bgp_peerings_nhs_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\snext-hop-self','',bgp_peerings_nhs_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append('Y')

            # UPDATE SOURCE - Iterate through list - catch 'not found' and manually insert null entry
            peerings_update_searchstring = r'neighbor\s'+x+r'\supdate-source\s\S+'
            for obj in bgp_obj:
                peerings_update = obj.re_search_children(peerings_update_searchstring)
                if peerings_update == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('default')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_update:
                    bgp_peerings_update_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\supdate-source\s\S+','',bgp_peerings_update_raw)
                    bgp_peerings_update = re.sub('\S+\supdate-source\s','',bgp_peerings_update_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_update)

            # BFD - Iterate through list - catch 'not found' and manually insert null entry
            # NOTE CAN BE APPLIED TO INDIVIDUAL PEER OR PEER GROUP
            peerings_bfd_searchstring = r'neighbor\s' + x + r'\sfall-over\sbfd'
            for obj in bgp_obj:
                peerings_bfd = obj.re_search_children(peerings_bfd_searchstring)
                if peerings_bfd == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find if bfd set and add them to correct 'list of lists'
                for line in peerings_bfd:
                    bgp_peerings_bfd_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sfall-over\sbfd', '', bgp_peerings_bfd_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('Y')
                            else:
                                sublist.append('Y')



            # SOFT-RECONFIG - Iterate through list - catch 'not found' and manually insert null entry
            peerings_soft_searchstring = r'neighbor\s'+x+r'\ssoft-reconfiguration\sinbound'
            for obj in bgp_obj:
                peerings_soft = obj.re_search_children(peerings_soft_searchstring)
                if peerings_soft == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find if soft set and add them to correct 'list of lists'
                for line in peerings_soft:
                    bgp_peerings_soft_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\ssoft-reconfiguration\sinbound','',bgp_peerings_soft_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('Y')
                            else:
                                sublist.append('Peer-group setting')

            # TIMERS - Iterate through list - catch 'not found' and manually insert null entry
            peerings_timers_searchstring = r'neighbor\s'+x+r'\stimers\s\d*\s\d*'
            for obj in bgp_obj:
                peerings_timers = obj.re_search_children(peerings_timers_searchstring)
                if peerings_timers == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('60 180')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_timers:
                    bgp_peerings_timers_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\stimers\s\d*\s\d*','',bgp_peerings_timers_raw)
                    bgp_peerings_timers = re.sub('\S+\stimers\s','',bgp_peerings_timers_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_timers)

            # MULTIHOP - Iterate through list - catch 'not found' and manually insert null entry
            peerings_multihop_searchstring = r'neighbor\s'+x+r'\sebgp-multihop\s\d*'
            for obj in bgp_obj:
                peerings_multihop = obj.re_search_children(peerings_multihop_searchstring)
                if peerings_multihop == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('no multihop')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_multihop:
                    bgp_peerings_multihop_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sebgp-multihop\s\d*','',bgp_peerings_multihop_raw)
                    bgp_peerings_multihop = re.sub('\S+\sebgp-multihop\s','',bgp_peerings_multihop_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_multihop)


            # COMMUNITY - Iterate through list - catch 'not found' and manually insert null entry
            peerings_community_searchstring = r'neighbor\s'+x+r'\ssend-community\s\S+'
            for obj in bgp_obj:
                peerings_community = obj.re_search_children(peerings_community_searchstring)
                if peerings_community == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('no community')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_community:
                    bgp_peerings_community_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\ssend-community\s\S+','',bgp_peerings_community_raw)
                    bgp_peerings_community = re.sub('\S+\ssend-community\s','',bgp_peerings_community_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_community)


            # MAXPREFIX - Iterate through list - catch 'not found' and manually insert null entry
            peerings_maxprefix_searchstring = r'neighbor\s'+x+r'\smaximum-prefix\s\d*\s\d*\s\S+'
            for obj in bgp_obj:
                peerings_maxprefix = obj.re_search_children(peerings_maxprefix_searchstring)
                if peerings_maxprefix == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('no max-prefix')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_maxprefix:
                    bgp_peerings_maxprefix_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\smaximum-prefix\s\d*\s\d*\s\S+','',bgp_peerings_maxprefix_raw)
                    bgp_peerings_maxprefix = re.sub('\S+\smaximum-prefix\s','',bgp_peerings_maxprefix_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_maxprefix)

            # DEFAULT-ORIGINATE - Iterate through list - catch 'not found' and manually insert null entry
            # NOTE CAN BE APPLIED TO INDIVIDUAL PEER OR PEER GROUP
            peerings_defaultorig_searchstring = r'neighbor\s' + x + r'\sdefault-originate'
            for obj in bgp_obj:
                peerings_defaultorig = obj.re_search_children(peerings_defaultorig_searchstring)
                if peerings_defaultorig == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find if defaultorig set and add them to correct 'list of lists'
                for line in peerings_defaultorig:
                    bgp_peerings_defaultorig_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sdefault-originate', '', bgp_peerings_defaultorig_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('Y')
                            else:
                                sublist.append('Y')

            # ROUTE-MAP IN - Iterate through list - catch 'not found' and manually insert null entry
            peerings_rmin_searchstring = r'neighbor\s'+x+r'\sroute-map\s\S+\sin'
            for obj in bgp_obj:
                peerings_rmin = obj.re_search_children(peerings_rmin_searchstring)
                if peerings_rmin == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('no route-map in')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_rmin:
                    bgp_peerings_rmin_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sroute-map\s\S+\sin','',bgp_peerings_rmin_raw)
                    bgp_peerings_rmin_raw2 = re.sub('\sroute-map\s','',bgp_peerings_rmin_raw)
                    bgp_peerings_rmin = re.sub('\sin$','',bgp_peerings_rmin_raw2)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_rmin)

            # ROUTE-MAP OUT - Iterate through list - catch 'not found' and manually insert null entry
            peerings_rmout_searchstring = r'neighbor\s'+x+r'\sroute-map\s\S+\sout'
            for obj in bgp_obj:
                peerings_rmout = obj.re_search_children(peerings_rmout_searchstring)
                if peerings_rmout == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist [1] is 'no-peer-group':
                                sublist.append('no route-map out')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find values and add them to correct 'list of lists'
                for line in peerings_rmout:
                    bgp_peerings_rmout_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sroute-map\s\S+\sout','',bgp_peerings_rmout_raw)
                    bgp_peerings_rmout_raw2 = re.sub('\sroute-map\s','',bgp_peerings_rmout_raw)
                    bgp_peerings_rmout = re.sub('\sout$','',bgp_peerings_rmout_raw2)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            sublist.append(bgp_peerings_rmout)

            # SHUTDOWN - Iterate through list - catch 'not found' and manually insert null entry
            # NOTE CAN BE APPLIED TO INDIVIDUAL PEER OR PEER GROUP
            peerings_shutdown_searchstring = r'neighbor\s' + x + r'\sshutdown'
            for obj in bgp_obj:
                peerings_shutdown = obj.re_search_children(peerings_shutdown_searchstring)
                if peerings_shutdown == []:
                    for sublist in bgp_peerings_master:
                        if sublist[0] == x:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('N')
                            else:
                                sublist.append('Peer-group setting')
                # Iterate through list - find if shutdown set and add them to correct 'list of lists'
                for line in peerings_shutdown:
                    bgp_peerings_shutdown_raw = line.text[10:]
                    bgp_peerings_id = re.sub('\sshutdown', '', bgp_peerings_shutdown_raw)
                    for sublist in bgp_peerings_master:
                        if sublist[0] == bgp_peerings_id:
                            if sublist[1] is 'no-peer-group':
                                sublist.append('Y')
                            else:
                                sublist.append('Y')


    pprint("*******BGP PEERINGS START************")
    pprint(bgp_peerings_master)
    pprint("*******BGP PEERINGS END**************")
    WriteListToCSV(output_peerings,['Peer IP','Remote-AS','Peer-group Member', 'Description', 'RR-Client','Next-Hop-Self', 'Update-source','BFD','Soft-Reconfiguration Inbound','Timers','EBGP-Multihop','Community','Max-prefix','Default-originate','Route-map In','Route-map Out','Shutdown'],bgp_peerings_master)



if __name__ == '__main__':
    # Input parameters
    if len(sys.argv) != 2:
        # Exit the script
        sys.exit("Usage: ./get-bgp.py <raw IOS config file>")
    config = sys.argv[1]
    output_network = str('./outputs/'+(sys.argv[1])+'.bgp.networks.csv')
    output_agg = str('./outputs/'+(sys.argv[1]) + '.bgp.agg.csv')
    output_peergrps = str('./outputs/'+(sys.argv[1])+'.bgp.peergroups.csv')
    output_peerings = str('./outputs/'+(sys.argv[1])+'.bgp.peerings.csv')
    print("Configuration File = "+config)
    print("Output Network Statements File = "+output_network)
    print("Output Aggregates = " + output_agg)
    print("Output Peer Groups File = "+output_peergrps)
    print("Output Peerings File = "+output_peerings)

    get_bgp(config,output_network,output_agg,output_peergrps,output_peerings)