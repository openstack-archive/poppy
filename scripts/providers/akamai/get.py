import ConfigParser
import requests
import json
import sys

from akamai.edgegrid import EdgeGridAuth
import dns.resolver


def main(args):
    if len(args) != 3:
        print("usage: python get.py [env] [domain]")
        print(
            "example : python get.py [prod|test] www.mysite.com")
        sys.exit(2)

    env = args[1]
    domain = args[2]

    config_parser = ConfigParser.RawConfigParser()
    config_parser.read("akamai.conf")

    print
    print

    print("looking up records for " + domain)
    print
    print

    print("querying akamai api for policy definition: ")
    akamai_request(env, domain, config_parser)
    print
    print

    print("querying DIG record:")
    dig_cname(domain)
    print
    print

    browser_request(domain)
    print
    print


def edge_session(env, config):
    s = requests.Session()
    s.auth = EdgeGridAuth(
        # This is rax_cdn credential
        client_token=config.get(env, 'client_token'),
        client_secret=config.get(env, 'client_secret'),
        access_token=config.get(env, 'access_token'))

    return s


def akamai_request(env, domain, config):
    base_url = config.get(env, 'base_url')
    policy_num = config.get(env, 'policy_number')

    policy_url = '{0}partner-api/v1/network/production/properties/{1}/sub-properties/{2}/policy'.format(
        base_url,
        policy_num,
        domain
    )

    print ("API URL: " + policy_url)
    print ("ARLID: " + str(policy_num))

    s = edge_session(env, config)
    response = s.get(policy_url,
                     headers={
                         'Content-type': 'application/json',
                         'Accept': 'text/plain'
                     })
    resp_dict = json.loads(response.text)
    print(json.dumps(resp_dict, indent=4, sort_keys=True))


def dig_cname(target):
    try:
        answers = dns.resolver.query(target, 'CNAME')
        for rdata in answers:
            print answers.qname, ' IN CNAME', rdata.target
            dig_cname(rdata.target)
    except:
        pass


def browser_request(target):
    print("browser response for " + target)
    response = requests.get("http://" + target)
    print ("Status Code: " + str(response.status_code))
    print ("Response Body: " + response.text)


if __name__ == '__main__':
    main(sys.argv)
