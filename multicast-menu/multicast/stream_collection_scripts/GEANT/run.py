import ipwhois
import json
import re
import requests
import time


def run(path_to_device_file):
    BASE_URL = "https://lg.geant.org/rest/submit"
    headers = {"accept": "application/json", "content-type": "application/json"}
    devices = [d.strip() for d in open(path_to_device_file, "r").readlines()]
    who_is_cache = dict()
    results = dict()
    failed = list()

    for ip in devices:
        try:
            # Make a request to the looking glass, surrounded by pauses to avoid rate limits.
            time.sleep(2)
            data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show multicast route extensive inet\""}}
            r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
            time.sleep(2)

            # Format the raw response text and split it into an array
            response = json.loads(r.text)["output"][ip]["commandResult"]
            response_text = [l.strip() for l in response.split("\n")]

            # Loop through the formatted raw response text to discover streams
            fields = dict()
            for line in response_text[1:-1]:
                # Begin parsing fields
                if line == "":
                    if "Group" in fields:
                        # Pull the source and group out to use
                        source = str(fields["Source"]).split("/")[0]
                        group = str(fields["Group"])

                        # Attempt to discover the upstream interface
                        upstream_interface = str(fields["Upstream interface"])
                        upstream_interface_name = "Undefined"
                        try:
                            if upstream_interface in who_is_cache.keys():
                                upstream_interface_name = who_is_cache[upstream_interface]
                            else:
                                data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show interface " + upstream_interface}} 
                                r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
                                response = json.loads(r.text)["output"][ip]["commandResult"]
                                upstream_interface_name = response[response.index("Description") + 12:response.index("Flags")].strip()
                                who_is_cache[upstream_interface] = upstream_interface_name
                        except:
                            pass
                        
                        # Attempt to discover downstream interfaces
                        downstream_interfaces_string = "None"
                        if "Downstream interface list" in fields.keys():
                            downstream_interfaces = list(fields)[list(fields).index("Downstream interface list") + 1]
                            downstream_interfaces_list = downstream_interfaces.split(" ")
                            interface_names = []
                            for interface in downstream_interfaces_list:
                                try:
                                    if interface in who_is_cache.keys():
                                        interface_name = who_is_cache[interface]
                                    else:
                                        data = {"selectedRouters":[{"name":ip}],"selectedCommand":{"value":"show interface " + interface}}
                                        r = requests.post(BASE_URL, data=json.dumps(data), headers=headers)
                                        response = json.loads(r.text)["output"][ip]["commandResult"]
                                        interface_name = response[response.index("Description") + 12:response.index("Flags")].strip()
                                        who_is_cache[interface] = interface_name
                                    interface_names.append(interface_name)
                                except:
                                    interface_names.append("Undefined")
                            downstream_interfaces_string = ", ".join(["{} ({})".format(interface_names[i], downstream_interfaces_list[i]) for i in range(len(downstream_interfaces_list))])

                        # Pull out stream statistics
                        st = fields["Statistics"].split(",")
                        pps = int(re.sub(r"[^0-9]", "", st[1]))

                        # Gather whois data
                        who_is = "Undefined"
                        formatted_source = source.split("/")[0].strip()
                        if formatted_source in who_is_cache.keys():
                            who_is = who_is_cache[formatted_source]
                        else:
                            who_is = ipwhois.IPWhois(formatted_source).lookup_whois()["nets"][0]["name"]
                            who_is_cache[formatted_source] = who_is

                        # Add information to results dictionary
                        results[len(results.keys())] = {
                            "source": source,
                            "group": group,
                            "upstream_interface": upstream_interface,
                            "upstream_interface_name": upstream_interface_name,
                            "downstream_interfaces_string": downstream_interfaces_string,
                            "pps": pps,
                            "who_is": who_is,
                        }

                        # Reset the fields dictionary
                        fields = dict()
                elif ":" in line:
                    key, value = line.split(":", 1)
                    fields[key.strip()] = value.strip()
                else:
                    fields[line.strip()] = ""   
        except:
            print("Failed on {}".format(ip))
            failed.append(ip)
    
    return (results, failed)
