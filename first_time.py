import simplejson as json
import os
from classes.cf_api import CF, ST, HD

HD()

# 1 Enter Email & Global API key
print(ST.hd("Get Global API Key from Cloudflare:\n",
      "https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-CloudFlare-API-key-\n"))

cf_email = input(ST.q(" Enter your Cloudflare email: ") + "\n")
print("\n")
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

print(ST.msg("DNS record: " + dns_records[choice][0]))
cf_record_token = dns_records[choice][1]
cf_record = dns_records[choice][0]

# Create API data file
# Check if file exists or should we create it
update_status = ""

while True:
    # Check if api data file exists then Get data from file
    if os.path.isfile("./api_data.json") and os.stat("./api_data.json").st_size != 0:
        print("\n", ST.os("API file exists, loading data ..."), "\n")

        old_file = open("./api_data.json", "r+")
        # Import data into json object
        data = json.loads(old_file.read())
        # Print data
        print("\nEmail: ", data["cf_email"],
              "\nGlobal API Key: ", data["cf_auth_token"],
              "\nDomain: ", data["cf_domain"],
              "\nDomain token: ", data["cf_domain_token"],
              "\nDns record: ", data["cf_record"],
              "\nRecord token: ", data["cf_record_token"], "\n")

        answer = input(ST.q("Data already exists, Replace data ? y:yes or n:no ") + "\n")

        if answer == "y":
            update_status = "recreated"
        elif answer is "n":
            print(ST.os("exiting..."))
            old_file.close()
            exit()
        else:
            print("\n" + ST.warn("That's not a valid option!") + "\n")
            continue
    else:
        # Creating file
        update_status = "created"
        print("\n", ST.os("Creating new API file ..."), "\n")
        old_file = open("./api_data.json", "w")
        
    # write data to the file
    data = {"cf_email": cf_email,
            "cf_auth_token": cf_auth_token,
            "cf_domain": cf_domain,
            "cf_domain_token": cf_domain_token,
            "cf_record": cf_record,
            "cf_record_token": cf_record_token}
    # start file from the position zero
    old_file.seek(0)
    json.dump(data, old_file, indent=4)
    old_file.close()

    # log transaction
    CF.log_(update_status, None, None, cf_domain)

    break

exit()
