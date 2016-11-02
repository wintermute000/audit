A collection of dirty scripts to automate cisco IOS L2/L3 device auditing

Assumes info is presented via a text file putty session with following show commands in one file per device
(examples not provided due to information security) - assumes audit project where direct scripting against devices not allowed

show run - NEEDS TO BE FIRST TO EXTRACT HOSTNAME FOR FILE NAMING
show ip int brie
show int status
show etherchannel summary 
show vlan
show ip route
show ip ospf nei 
show ip bgp summary
show ip bgp
show ip bgp nei
show cdp nei
show cdp nei det

- get-configs.py - sanitises text file to remove putty line breaks and passwords, produces *.cfg output

Following scripts utilise ciscoconfparse to parse the config files for values and output as CSV
- get-bgp.py
- get-interfaces.py (for interfaces with IP addresses only)
- get-ospf.py
- get-portchannels.py

Following scripts utilise textfsm templates to parse the show commands in the raw file and output as respective CSV
- get-bgp-routes.py
- get-bgp-sum.py
- get-cdp-nei.py
- get-ospf-adj.py

+ a bunch of dirty bash scripts to iterate the above over multiple input files

!!!!! CAVEATS
- no BGP address-family support yet
- BGP routes (i.e. show ip bgp --> CSV) is experimental - seems to work OK, you tell me (show ip bgp command output is ridiculously non-structured!!!)
