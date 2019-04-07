import requests
import simplejson as json
import time
import datetime
import style


class ST:
    hd = style.bold.green
    q = style.bold.on_green.blue
    warn = style.bold.red
    msg = style.italic.blue
    os = style.bold.on_yellow.black


class HD:
    ver = "1"
    logo = """\n ____        _       _          _     _ _       
/ ___|  __ _| | __ _| |__   ___| | __| (_)_ __  
\___ \ / _` | |/ _` | '_ \ / _ \ |/ _` | | '_ \ 
 ___) | (_| | | (_| | | | |  __/ | (_| | | | | |
|____/ \__,_|_|\__,_|_| |_|\___|_|\__,_|_|_| |_|
                                             \n"""
    title = "CloudFlare DNS Updater"
    contact = "\n-=-=-=--=-=-=-=-=-=-=-=-=-" \
              "\nTwitter-->  @salaheldinaz " \
              "\nGithub -->  salaheldinaz " \
              "\n-=-=-=--=-=-=-=-=-=-=-=-=-"

    print(ST.hd(logo, title, "v" + ver),
          ST.msg(contact), "\n")


class CF:
    def __init__(self, email, auth_token, domain_token, record_token):
        self.email = email
        self.auth_token = auth_token
        self.domain_token = domain_token
        self.record_token = record_token
        self.api_url = "https://api.cloudflare.com/client/v4/zones/"
        self.header = {
                'X-Auth-Email': self.email,
                'X-Auth-Key': self.auth_token,
                'Content-Type': "application/json",
            }

# Get DNS Records
    def get_dns(self, record, cf_domain=None):
        headers = {
            'X-Auth-Email': self.email,
            'X-Auth-Key': self.auth_token,
            'Content-Type': "application/json",
        }
        if record == "domains-list":

            response = requests.get(self.api_url, headers=headers)
            r = json.loads(response.text)
            if r['success'] is False:
                if int(r['errors'][0]['error_chain'][0]['code']) == 6102 or 9103:
                    print(ST.warn("Email address is not correct."))

                if int(r['errors'][0]['error_chain'][1]['code']) == 6103 or 9103:
                    print(ST.warn("Global API key is not correct."))
                exit()

            domains = json.loads(response.text)['result']
            domains_list = {}

            print(ST.hd("\nDomain list for account attached to " + str(self.email) + " :\n"))
            i = 1
            for domain in domains:
                domains_list[i] = domain['name'], domain['id']
                print(str(i) + " : " + domain['name'])
                i = i + 1

            return domains_list

        if record == "dns-list":
            url = self.api_url + self.domain_token + "/dns_records/"
            response = requests.get(url, headers=headers)
            dns = json.loads(response.text)['result']
            dns_records = {}

            print(ST.hd("\nDNS records for domain :" + str(cf_domain) + " :\n"))
            i = 1
            for record in dns:
                dns_records[i] = record['type'], record['id']
                print(str(i) + " : " + record['type'])
                i = i + 1

            return dns_records

        if record == "dns-record":
            url = self.api_url + self.domain_token + "/dns_records/" + self.record_token
            response = requests.get(url, headers=headers)
            current_ip = json.loads(response.text)["result"]["content"]
            current_domain = json.loads(response.text)["result"]["name"]
            print(current_domain, " : ", current_ip)
            return current_ip, current_domain

# Update DNS record to the new ip
    def update_dns(self, new_ip, current_ip, current_domain, record_type):
        if new_ip == current_ip:
            print(ST.os("IP address didn't change, they are the same"))
            update_status = "unchanged"
            return update_status

        else:
            print(ST.os("IP address changed,updating DNS " + record_type + " record"))
            url = self.api_url + self.domain_token + "/dns_records/" + self.record_token
            payload = {"type": record_type, "name": current_domain, "content": new_ip, "ttl": 1, "proxied": "false"}
            requests.put(url, data=payload, headers=self.header)
            print(ST.hd("Domain "
                        + current_domain
                        + " | ip address updated to "
                        + new_ip + " | DNS record "
                        + record_type))
            update_status = "updated"
            return update_status

# logging
    @staticmethod
    def log_(update_status, current_ip, new_ip, current_domain):
        ts = time.time()
        log_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        log_msg = ""

        if update_status == "updated":
            log_msg = str(current_domain
                          + " | DNS record "
                          + update_status
                          + ", ip: " + current_ip + " > " + new_ip
                          + "\n")
        elif update_status == "unchanged":
            log_msg = str(current_domain
                          + " | DNS record "
                          + update_status
                          + ", ip: " + current_ip
                          + "\n")
        elif update_status == "created" or "recreated":
            log_msg = str(" API File " + update_status + " for the domain " + current_domain + "\n")

        log_data = str(log_time) + " | " + str(log_msg)
        print(ST.hd(log_data))

        # Creating file
        with open("./cf.log", "a") as log_file:
            # write data to the file
            log_file.write(log_data)
            log_file.close()