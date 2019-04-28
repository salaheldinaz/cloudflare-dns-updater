import os
import simplejson as json
from classes.get_ip import IP
from classes.cf_api import CF, ST, HD

HD()

while True:
    # Check if api data file exists then Get data from file
    if os.path.isfile("./api_data.json") and os.stat("./api_data.json").st_size != 0:
        api_data = open("./api_data.json", "r")

        print(ST.os("API file exists, loading data ..."), "\n")

        # Get public ip
        new_ip = IP.get_ip()

        print("\n", ST.q("Analysis domains Dns records..."), "\n")

        # Import data into json object
        data = json.loads(api_data.read())

        i = 1
        for record in data["api_data"]:
            cf_email = record["cf_email"]
            cf_auth_token = record["cf_auth_token"]
            cf_domain = record["cf_domain"]
            cf_domain_token = record["cf_domain_token"]
            cf_record = record["cf_record"]
            cf_record_token = record["cf_record_token"]

            # Print data
            print("No.: ", i, "\nDomain: ", cf_domain, "\nDns record: ", cf_record)

            # Get DNS Record
            cf_data = CF(cf_email, cf_auth_token, cf_domain_token, cf_record_token)
            current_ip, current_domain = cf_data.get_dns("dns-record")

            # Update DNS record to the new ip
            update_status = cf_data.update_dns(new_ip, current_ip, current_domain, cf_record)
            api_data.close()

            # log transaction
            CF.log_(update_status, current_ip, new_ip, current_domain)
            i = i + 1

        exit()

    else:
        print(ST.warn("No API Data found, Please run first_time.py"))
        exit()
