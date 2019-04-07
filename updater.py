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

        # Import data into json object
        data = json.loads(api_data.read())
        cf_email = data["cf_email"]
        cf_auth_token = data["cf_auth_token"]
        cf_domain = data["cf_domain"]
        cf_domain_token = data["cf_domain_token"]
        cf_record = data["cf_record"]
        cf_record_token = data["cf_record_token"]

        # Print data
        print("Email: ", cf_email,
              "\nGlobal API Key: ", cf_auth_token,
              "\nDomain: ", cf_domain,
              "\nDomain token: ", cf_domain_token,
              "\nDns record: ", cf_record,
              "\nRecord token: ", cf_record_token)

        # Get public ip
        new_ip = IP.get_ip()

        # Get DNS Record
        cf_data = CF(cf_email, cf_auth_token, cf_domain_token, cf_record_token)
        current_ip, current_domain = cf_data.get_dns("dns-record")

        # Update DNS record to the new ip
        update_status = cf_data.update_dns(new_ip, current_ip, current_domain, cf_record)
        api_data.close()

        # log transaction
        CF.log_(update_status, current_ip, new_ip, current_domain)
        exit()

    else:
        print(ST.warn("No API Data found, Please run first_time.py"))
        exit()
