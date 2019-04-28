import simplejson as json
import os
from classes.cf_api import CF, ST, HD

HD()

while True:

    # 1 Enter Email & Global API key

    cf_email = input(ST.q(" Enter your Cloudflare email: ") + "\n")

    print(ST.hd("\n Get Global API Key from Cloudflare:\n",
          "https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-CloudFlare-API-key-\n"))

    cf_auth_token = input(ST.q("Enter your Global API Key:"))

    # 2 Select domain you want to update
    cf_api_keys = CF(cf_email, cf_auth_token, None, None)
    domains_list = cf_api_keys.get_dns("domains-list")

    while True:
        try:
            choice = int(input(ST.q(" Enter number for selected domain: ") + "\n"))
            break
        except ValueError:
            print("\n" + ST.warn("That's not a valid option!") + "\n")

    print("Domain: " + domains_list[choice][0])
    cf_domain_token = domains_list[choice][1]
    cf_domain = domains_list[choice][0]

    # 3 select record you want to update the ip { usually will be A record }
    cf_api_keys = CF(cf_email, cf_auth_token, cf_domain_token, None)
    dns_records = cf_api_keys.get_dns("dns-list", cf_domain)

    while True:
        try:
            choice = int(input(ST.q(" Enter number for selected DNS record: ") + "\n"))
            break
        except ValueError:
            print("\n" + ST.warn("That's not a valid option!") + "\n")

    cf_record = dns_records[choice][0]
    cf_record_token = dns_records[choice][1]
    cf_name = dns_records[choice][2]
    cf_content = dns_records[choice][3]

    print(ST.msg("DNS record:", cf_record, " | ", cf_name, " | ", cf_content))

    # Create API data file
    # Check if file exists or should we create it
    update_status = ""

    data = {"cf_email": cf_email,
            "cf_auth_token": cf_auth_token,
            "cf_domain": cf_domain,
            "cf_domain_token": cf_domain_token,
            "cf_record": cf_record,
            "cf_record_token": cf_record_token}
    new_file_data = {"api_data": [data]}

    # Check if api data file exists then Get data from file
    if os.path.isfile("./api_data.json") and os.stat("./api_data.json").st_size != 0:
        print("\n", ST.os("API file exists, loading data ..."), "\n")

        old_file = open("./api_data.json", "r")
        # Import data into json object
        old_file_data = json.loads(old_file.read())

        # Print data
        i = 1
        for record in old_file_data["api_data"]:
            print("No.: ", i,
                  "\nEmail: ", record['cf_email'],
                  "\nGlobal API Key: ", record['cf_auth_token'],
                  "\nDomain: ", record['cf_domain'],
                  "\nDomain token: ", record['cf_domain_token'],
                  "\nDns record: ", record['cf_record'],
                  "\nRecord token: ", record['cf_record_token'], "\n", "----------------------------------")
            i = i + 1
        answer = input(ST.q("Data exists, Replace file or append to file ? \n r:replace , a:append, e:exit") + "\n")

        if answer == "r":
            update_status = "recreated"
            new_file = open("./api_data.json", "w")
            # write data to the file
            json.dump(new_file_data, new_file, indent=4)
            old_file.close()
        elif answer == "a":
            update_status = "added"
            old_file = open("./api_data.json", "w")
            old_file_data["api_data"] += [data]
            # write data to the file
            json.dump(old_file_data, old_file, indent=4)
            old_file.close()
        elif answer is "e":
            print(ST.os("exiting..."))
            old_file.close()
            break

        else:
            print("\n" + ST.warn("That's not a valid option!") + "\n")
            continue
    else:
        # Creating file
        update_status = "created"
        print("\n", ST.os("Creating new API file ..."), "\n")
        new_file = open("./api_data.json", "w")
        # write data to the file
        json.dump(new_file_data, new_file, indent=4)
        new_file.close()

    # log transaction
    CF.log_(update_status, None, None, cf_domain)

    more = input(ST.q("Add more or exit? y:yes e:exit") + "\n")
    if more == "y":
        print("\nAdding more... \n")
    else:
        break

exit()
