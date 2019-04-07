import requests


# Get public ip
class IP:
    @staticmethod
    def get_ip():
        url = "https://api.ipify.org"
        response = requests.get(url)
        new_ip = response.text
        print(new_ip)
        return new_ip
