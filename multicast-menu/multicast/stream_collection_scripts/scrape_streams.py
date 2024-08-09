from pathlib import Path
import sys

from GEANT.run import run as run_geant
from Internet2.run import run as run_i2


valid_user_inputs = ["all", "GEANT", "I2"]

user_input = None
if len(sys.argv) == 2 and sys.argv[1].strip() in valid_user_inputs:
    user_input = sys.argv[1].strip()
else:
    print("Please pass a valid parameter to specify the looking glass.")
    sys.exit(1)

devices_path = str(Path(__file__).resolve().parent)
results_dictionary_list = []
failed_list = []
if user_input == "GEANT" or user_input == "all":
    results = run_geant(devices_path + "/GEANT/devices.txt")
    results_dictionary_list.append(results[0])
    failed_list.append(results[1])
if user_input == "I2" or user_input == "all":
    results = run_i2(devices_path + "/Internet2/devices.txt")
    results_dictionary_list.append(results[0])
    failed_list.append(results[1])

outfile = open("output.txt", "w+")
for results in results_dictionary_list:
    for entry in results.keys():
        outfile.write("*************\n")
        entry_dict = results[entry]
        for field in entry_dict.keys():
            outfile.write("{}: {}\n".format(field, entry_dict[field]))
outfile.write("*************\n")
for failed in failed_list:
    for ip in failed:
        outfile.write("Failed to query {}\n".format(ip))
        outfile.write("*************\n")

print("Success! Your results are available at ~/multicat-menu/output.txt.")
outfile.close()
