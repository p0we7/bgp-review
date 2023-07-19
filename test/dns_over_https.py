
import os
import sys
import django
import logging
import requests
import dns.resolver
from ipaddress import IPv4Address, ip_address
from retrying import retry
from json import JSONDecodeError
from collections import Counter
import traceback

sys.path.append('./bgp_review')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bgp_review.settings'
django.setup()

from warehouse.models import Domain

resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ['1.1.1.1', '1.0.0.1', '8.8.8.8', '8.8.4.4']
resolver.lifetime = 5


def print_data_if_none(udp_res):
    """
    TODO 通过装饰器访问被装饰函数内变量
    """
    def wrapper(func):
        def print_data(*args, **kwargs):
            i = func(*args, **kwargs)

            if not i:
                raise TypeError("DNS result is None")
        return print_data
    return wrapper

def retry_if_fail(exception):
    print()
    print("#Retry for {}".format(exception))
    if isinstance(exception, JSONDecodeError) or \
       isinstance(exception, TypeError) \
       :
        return True
    else:
        False



@retry(retry_on_exception=retry_if_fail)
def dns_lookup_udp(ip='1.1.1.1', domain=None):
    try:
        query_answers = resolver.query(domain)
    except (dns.resolver.NXDOMAIN, dns.exception.Timeout, dns.resolver.NoAnswer):
        return None
    # except Exception as e:
    #     print("UNKNOW ERROR: {} {}".format(domain, e))
    #     print(traceback.format_exc())
    return [ rdata.address for rdata in query_answers ]




@retry(retry_on_exception=retry_if_fail)
def dns_lookup_over_https(res_udp, ip='1.1.1.1', domain=None, ):

    logger = logging.getLogger("urllib3")
    logger.setLevel(logging.CRITICAL)
    url = 'https://cloudflare-dns.com/dns-query'
    data = {
        'name': domain,
        'type': 'A' if isinstance(ip_address(ip), IPv4Address) else 'AAAA'
    }
    headers = { 'accept': 'application/dns-json' }

    r = requests.get(url, headers=headers, params=data)

    result = r.json()

    answer = result.get('Answer')

    if res_udp and not answer:
        raise TypeError("return empty answer")


    def ip_filter(ip):
        ip = ip.get('data') if isinstance(ip, dict) else ip
        try:
            return True if isinstance(ip_address(ip), IPv4Address) else False
        except ValueError:
            return False

    return [ ip.get('data') for ip in answer if ip_filter(ip) ] if answer else None



if __name__ == "__main__":
    # domains = Domain.objects.all()
    domains = ['cloudflare.com']
    count = 0

    res_https = ''
    res_udp = ''

    # print(domians[:10])
    for i in domains:
        i = str(i)
        count += 1
        
        res_udp = dns_lookup_udp(domain=i)
        res_https = dns_lookup_over_https(res_udp, domain=i)

        match = True if Counter(res_https) == Counter(res_udp) else False
        if not match:
            print()
            print("{} {}: {}, {}   {}".format(count, i, res_https, res_udp, match))
            print()
        else:
            print("{},".format(count), end='', flush=True)
