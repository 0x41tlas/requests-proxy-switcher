import requests
import bs4
# for IP check: only works on linux
import os

# global proxy list
# proxy format: 'http(s)://<proxy_ip>:<proxy_port>'
PROXIES = {
    'https': None,
    'http': None
}

# format: <ip>:<port>
CURRENT_PROXY = None
# change to False if you don't want to exit on an error
exit_status = True

PROXY_ITER = None

# Quick and easy bs4 parsing function
def bsoup(data):
    return bs4.BeautifulSoup(data.text, 'lxml')

# Quick and easy request function
def req_with_proxy(url):
    r = requests.get(url, proxies=PROXIES)
    r.raise_for_status
    return r

def req_without_proxy(url):
    r = requests.get(url)
    r.raise_for_status
    return r

def exit_quit():
    if exit_status is True:
        exit(0)
    elif exit_status is False:
        return
    else:
        print("[*] True or False man... One or the other")

# pings proxy IP to ensure host is up
# Note: If the IP is one of another valid, non-proxy server, the check will still return True... I need to fix this.
def check_host_up(host):
    print("[*] Pinging proxy server...")
    response = os.system("ping -c 1 {} > /dev/null".format(host))
    if response == 0:
        print("[ OKAY ]")
        return True
    else:
        return False

def check_proxy_ip():
    print("[*] Checking proxy connection...")
    if CURRENT_PROXY[0] == get_proxy_ip():
        print("[ OKAY ]")
        return True
    else:
        print("[!] Current IP does not match proxy IP! Quitting.")
        exit_quit()
        return False

def get_proxy_ip():
    r = req_with_proxy('https://www.iplocation.net')
    soup = bsoup(r)
    return soup.p.span.text

def add_proxy(ip, port):
    PROXIES['https'] = "https://{}:{}".format(ip, port)
    PROXIES['http'] = "http://{}:{}".format(ip, port)

    global CURRENT_PROXY
    CURRENT_PROXY = (ip, port)

def set_proxy():
    proxy_tuple = set_current_proxy()
    if proxy_tuple is False:
        print("[!] You've either broken it, or run out of proxies.")
        print("[*] Exiting with status code 1")
        exit_quit(1)
    else:
        add_proxy(proxy_tuple[0], proxy_tuple[1])

def set_current_proxy():
    try:
        return next(PROXY_ITER)
    except Exception as e:
        print e
        return False

def find_proxy():
    print "[*] Requesting proxy list..."
    r = req_without_proxy('https://us-proxy.org/')
    print "[ OKAY ]"
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
    if check_host_up(CURRENT_PROXY[0]) and check_proxy_ip() is True:
        print("[*] Set proxy as {}:{}".format(CURRENT_PROXY[0], CURRENT_PROXY[1]))
    else:
        print("[!] Connection to {}:{} failed. Exiting".format(CURRENT_PROXY[0], CURRENT_PROXY[1]))
        exit_quit()

if __name__ == '__main__':
    first_connection()
