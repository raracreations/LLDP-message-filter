from netmiko import ConnectHandler
from datetime import datetime
from pprint import pprint
import re

#Defining device IP addresses
with open("ip.txt") as f:
    ips = f.readlines()

#pprint(ips)

#Defining device parameters
#Supported device types:
#https://github.com/ktbyers/netmiko/blob/master/netmiko/ssh_dispatcher.py#L70
arista1 = {
        "device_type": "arista_eos",
        "host": ips[0].rstrip("\n"),
        "username": "admin",
        "password": "python1"
}

arista2 = {
        "device_type": "arista_eos",
        "host": ips[1].rstrip("\n"),
        "username": "admin",
        "password": "python2"
}

arista3 = {
        "device_type": "arista_eos",
        "host": ips[2].rstrip("\n"),
        "username": "admin",
        "password": "python3"
}

#Connecting to the devices via SSHv2
switches = [arista1, arista2, arista3]

#Creating empty list for storing output
output_list = []

for switch in switches:
    connection = ConnectHandler(**switch)
    syslog_output = connection.send_command("show logging last 1 day")
    output_list.append(syslog_output)

#pprint(output_list)
#print(len(output_list))

#Creating empty dictionary for device:output mapping
output_map = {}

#Searching for and extracting LLDP Neighbor-related log messages (+ hostname)
for output in output_list:
    #Extracting hostname
    hostname_regex = re.findall(r".+\d\d:\d\d:\d\d\s(.+?)\s", output)
    hostname = hostname_regex[0]

    #Extracting LLDP neighbor information
    output_lines = output.split("\n")
    #pprint(output_lines)

    #Creating an empty list to store LLDP neighbor-related lines
    lldp_lines = []
    #pprint(lldp_lines)

    for line in output_lines:
        if re.search(r"LLDP", line, re.I) and re.search(r"neighbor", line, re.I):
            lldp_lines.append(line + "\n")

    #Creating the hostname:output mapping per device
    output_map[hostname] = lldp_lines

#pprint(output_map)

#Creating periodical LLDP text report and saving to local folder
#Naming the file using current timestamp
with open("lldp_{}".format(datetime.now().strftime("%Y-%m-%d-%H-%M")), "w") as f:
    for entry in output_map.items():
        f.write(entry[0] + "\n")
        f.writelines(entry[1])
        f.write("\n\n")

#End of program
