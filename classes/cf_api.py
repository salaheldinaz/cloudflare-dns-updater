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
    logo = """\n
  ____ _____   ____  _   _ ____  
 / ___|  ___| |  _ \| \ | / ___| 
| |   | |_    | | | |  \| \___ \ 
| |___|  _|   | |_| | |\  |___) |
 \____|_|     |____/|_| \_|____/ 
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
                dns_records[i] = record['type'], record['id'], record['name'], record['content']
                print(str(i) + " : ", record['type'], " | ", record['name'], " | ", record['content'])
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

            payload = '{"type":"' + str(record_type) \
                       + '","name":"' + str(current_domain) \
                       + '","content":"' + str(new_ip) \
                       + '","ttl":1,"proxied":true}'

            response = requests.put(url, data=payload, headers=self.header)
            done = json.loads(response.text)["success"]
            if done is True:
                print(ST.hd("Domain "
                            + current_domain
                            + " | ip address updated to "
                            + new_ip + " | DNS record "
                            + record_type))
                update_status = "updated"
                return update_status
            else:
                print("Domain update failed")
                update_status = "failed"
                return update_status
# logging
    @staticmethod
    def log_(update_status, current_ip, new_ip, current_domain):
        ts = time.time()
        log_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        api_file_msg ={"created", "recreated", "added"}
        dns_msg = {"unchanged", "failed"}

        if update_status in api_file_msg:
            log_msg = "API File " + str(update_status) + " | Domain: " + str(current_domain) + "\n"
        elif update_status == "updated":
            log_msg = str(current_domain) + " | DNS record " + str(update_status) + ", ip: " + str(current_ip) + " > " + str(new_ip) + "\n"
        elif update_status in dns_msg:
            log_msg = str(current_domain) + " | DNS record " + str(update_status) + " , ip: " + str(current_ip) + '\n'
        else:
            log_msg = "logging error"

        log_data = str(log_time) + " | " + log_msg
        print(ST.hd(log_data))

        # Creating file
        with open("./cf.log", "a") as log_file:
            # write data to the file
            log_file.write(log_data)
            log_file.close()
