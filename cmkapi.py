import requests
import pprint
class Service:
    def __init__(self):
        #bla
# Types:
# agent: Only Agent
# agentSNMP: Agent + SNMP
# none: no type
class Host:
    def __init__(self, hostname, ip, labels=[], folder="/", type="agent"):
        self.hostname = hostname
        self.ip = ip
        self.labels = labels
        self.folder = folder
        self.type = type
        #blab
class CmkApi:
    def __init__(self, hostname, site, user, secret, protocoll="https", port="443"):
        self.hostname = hostname
        self.port = port
        self.site = site
        self.user = user
        self.secret = secret
        self.session = requests.session()
        self.session.headers['Authorization'] = f"Bearer {self.user} {self.secret}"
        self.session.headers['Accept'] = 'application/json'
        self.protocoll = protocoll
        self.url = self.protocoll+"://"+self.hostname+":"+self.port+"/"+self.site+"/check_mk/api/1.0"
    def getHostObjectFromResponse(self, response):
        # ToDo: Add parsing from response
        return Host()
    def getHost(self,hostname):
        resp = self.session.get(
            f"{self.url}/objects/host_config/"+hostname,
            params={  # goes into query string
                "effective_attributes": False,
                # Show all effective attributes, which affect this host, not just the attributes which were set on this host specifically.
            },
        )
        if resp.status_code == 200:
            return self.getHostObjectFromResponse(resp)
        elif resp.status_code == 204:
            print("Done")
            return None
        else:
            raise RuntimeError(pprint.pformat(resp.json()))
            return None
    def getServiceForHost(hostname, service):
        # bla
    def addFolder(foldername, subpath="/"):
        # bla
    def addHost(host):
        # bla