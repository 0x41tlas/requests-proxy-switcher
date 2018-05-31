import requests
import bs4
# for IP check: only works on linux
import os

# global proxy list
# proxy format: 'http(s)://<proxy_ip>:<proxy_port>'
proxies = {
    'https': None,
    'http': None
}

# format: <ip>:<port>
current_proxy = None

# Quick and easy bs4 parsing function
def bsoup(data):
    return bs4.BeautifulSoup(data.text, 'lxml')

# pings proxy IP to ensure host is up
"""NOTE: If the IP is one of another valid, non-proxy server, the check will still return True... I need to fix this."""
def check_host_up(host):
    response = os.system("ping -c 1 {}".format(host))
    if response == 0:
        return True
    else:
        return False

def add_proxy(ip, port):
    proxies['https'] = "https://{}:{}".format(ip, port)
    proxies['http'] = "http://{}:{}".format(ip, port)

    current_proxy = (ip, port)

def set_proxy():
    proxy_tuple = current_proxy()
    if proxy_tuple is False:
        print("[!] You've either broken it, or run out of proxies.")
        print("[*] Exiting with status code 1")
        exit(1)
    else:
        set_proxy(proxy_tuple[0], proxy_tuple[1])


def current_proxy():
    try:
        return next(PROXY_ITER)
    except Exception as e:
        print e
        return False

def find_proxy():
    print "[*] requesting proxy list..."
    r = requests.get('https://us-proxy.org/')
    print "[*] done"
    r.raise_for_status
    soup = bsoup(r)
    out = soup.find('tbody')

    # returns list of proxies with https
    out_list = filter(lambda x: (x.find_all('td')[6].text == "yes") is True, out.find_all('tr'))

    # I know, I know... This is a terrible one-liner. I'm working on a solution using regex that'll be alot cleaner
    proxy_dict = {ip: port for (ip, port) in zip((map(lambda x: x.find_all('td')[0].text, out_list)), (map(lambda x: x.find_all('td')[1].text, out_list)))}
    global PROXY_ITER
    PROXY_ITER = proxy_dict.iteritems()

# makes all the function calls of a first connection for you
def first_connection():
    find_proxy()
    set_proxy()
    if check_host_up(current_proxy[0]) is True:
        print("[*] Connected to {}:{}".format(current_proxy[0], current_proxy[1]))
    else:
        print("[!] Connection to {}:{} failed. Exiting".format(current_proxy[0], current_proxy[1]))
        exit(0)

if __name__ == '__main__':
    first_connection()
