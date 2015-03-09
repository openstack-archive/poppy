import requests
import json
from akamai.edgegrid import EdgeGridAuth

def main():
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token = 'akab-topgoy5clii35boy-5ave5twaitspm7k4',
        client_secret='hQBfajPjx/VCTuz7N04BDbEXJZKVIXRkG7HuXurJocc=',
        access_token='akab-26uucvcift4qzcrb-eljlqllr4nterdmb')



    base_url = 'https://akab-3r276kizolbgfqbi-6tnfu4jessqtn4b4.luna.akamaiapis.net/config-secure-provisioning-service/v1/sps-requests/?contractId=ctr_C-2M6JYA&groupId=grp_23174'


    data = {
        'cnameHostname': 'poppyblog.ssl.altcdn.com',
        'issuer' : 'cybertrust',
        'createType': 'single',
        'csr.cn': 'poppyblog.ssl.altcdn.com',
        'csr.c': 'US',
        'csr.st': 'MA',
        'csr.l': 'Cambridge',
        'csr.o': 'Rackspace+US+Inc.',
        'csr.ou': 'IT',
        'organization-information.organization-name': 'Rackspace+US+Inc.',
        'organization-information.address-line-one':'1+Fanatical+Place',
        'organization-information.city' : 'San+Antonio',
        'organization-information.region' : 'TX',
        'organization-information.postal-code' : '78218',
        'organization-information.country' : 'US', 
        'organization-information.phone' : '12103124630',
        'admin-contact.first-name' : 'Domain', 
        'admin-contact.last-name' : 'Admin', 
        'admin-contact.phone' : '12103124630',
        'admin-contact.email' : 'm.jones@akamai.com',
        'technical-contact.first-name' : 'Domain',
        'technical-contact.last-name' : 'Admin',
        'technical-contact.phone' : '18008008002', 
        'technical-contact.email' : 'domains@rackspace.com',
        'ipVersion' : 'ipv4',
        'product' : 'alta',
        'slot-deployment.klass':'esslType'
    }
    
    response = s.post(
          base_url,
          data=data)
          #headers = {'Content-type': 'application/json', 'Accept': 'text/plain'})
    

    print response.status_code
    print response.headers
    print response.text
    

if __name__ == '__main__':
    main()