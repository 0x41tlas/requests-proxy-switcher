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

# pings proxy IP to ensure host is up
"""NOTE: If the IP is one of another valid, non-proxy server, the check will still return True... I need to fix this."""
def check_host_up(host):
    response = os.system("ping -c 1 {}".format(host))
    if response == 0:
        return True
    else:
        return False

def bsoup(data):
    return bs4.BeautifulSoup(data.text, 'lxml')

def https_check(state):
    state.find_all('td')[6].text == "yes"

def set_proxy():
    proxy_tuple = current_proxy()
    proxies['https'] = "https://{}:{}".format(proxy_tuple[0], proxy_tuple[1])
    proxies['http'] = "http://{}:{}".format(proxy_tuple[0], proxy_tuple[1])

def current_proxy():
    try:
        return next(PROXY_ITER)
    except Exception as e:
        print "[!] You've run out of proxies... or something. Here's the error:"
        print e

def find_proxy():
    print "[*] requesting proxy list..."
    r = requests.get('https://us-proxy.org/')
    print "[*] done"
    r.raise_for_status
    soup = bsoup(r)
    out = soup.find('tbody')

    # returns list of proxies with https
    out_list = filter(lambda x: (x.find_all('td')[6].text == "yes") is True, out.find_all('tr'))
    global PROXY_ITER
    # I know, I know... This is a terrible one-liner. I'm working on a solution using regex that'll be alot cleaner
    proxy_dict = {ip: port for (ip, port) in zip((map(lambda x: x.find_all('td')[0].text, out_list)), (map(lambda x: x.find_all('td')[1].text, out_list)))}
    PROXY_ITER = proxy_dict.iteritems()

if __name__ == '__main__':
    find_proxy()
