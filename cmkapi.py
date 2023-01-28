import requests
import pprint
class Service:
    def __init__(self, name):
        self.name = name
# Types:
# cmk-agent: cmk Agent
# no-agent: No CMK Agent
# agentSNMP: snmp-v2
# none: no type


class Host:
    def __init__(self, hostname, ip, labels=[], folder="/", agentType="no-agent", snmpType=None):
        self.hostname = hostname
        self.ip = ip
        self.labels = labels
        self.folder = folder
        self.agentType = agentType
        self.snmpType = snmpType

    def __str__(self):
        return self.hostname+" "+self.ip+" "+self.folder+" "+self.agentType+" "+str(self.snmpType)+" "+str(self.labels)


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

    def __getHostObjectFromResponse(self, response):
        extensions = response.json()["extensions"]
        hostname = response.json()["id"]
        folder = extensions["folder"]
        attrs = extensions["attributes"]
        ipaddress = attrs["ipaddress"]
        if "labels" in attrs:
            labels = attrs["labels"]
        else:
            labels = None
        if "tag_snmp_ds" in attrs:
            snmpType = attrs["tag_snmp_ds"]
        else:
            snmpType = None
        type = attrs["tag_agent"]
        if folder == " ":
            folder = "/"
        return Host(hostname=hostname,ip=ipaddress,labels=labels,folder=folder,agentType=type, snmpType=snmpType)

    def getHost(self,hostname):
        resp = self.session.get(
            f"{self.url}/objects/host_config/"+hostname,
            params={  # goes into query string
                "effective_attributes": False,
            },
        )
        if resp.status_code == 200:
            return self.__getHostObjectFromResponse(resp)
        elif resp.status_code == 204:
            return None
        else:
            return None
    def getServiceForHost(hostname, service):
        return None
    def addFolder(foldername, subpath="/"):
        return None

    def addHost(self, host):
        url = f"{self.url}/domain-types/host_config/collections/all"
        headers = {"Content-Type": 'application/json',}
        json = {
                   'folder': host.folder,
                   'host_name': host.hostname,
                   'attributes': {
                       'ipaddress': host.ip,
                       'tag_agent': host.agentType
                   }
               }
        if host.labels is not None:
            json["attributes"]["labels"] = host.labels
        if host.snmpType is not None:
            json["attributes"]["tag_snmp_ds"] = host.snmpType
        resp = self.session.post(url=url,headers=headers,json=json)
        if resp.status_code == 200:
            return host
        elif resp.status_code == 204:
            return None
        else:
            return None

    def deleteHost(self, hostname):
        resp = self.session.delete(
            f"{self.url}/objects/host_config/{hostname}",
        )
        if resp.status_code == 200:
            return True
        elif resp.status_code == 204:
            return False
        else:
            return False

    def doServiceDiscovery(self, hostname):
        resp = self.session.post(
            f"{self.url}/objects/host/{hostname}/actions/discover_services/invoke",
            headers={
                "Content-Type": 'application/json',
                # (required) A header specifying which type of content is in the request/response body.
            },
            json={'mode': 'refresh'},
        )
        if resp.status_code == 200:
            #ToDo: Return list of discovered Services
            return True
        elif resp.status_code == 204:
            return None
        else:
            return None

    def activateChanges(self, forceForeign=False):

        resp = self.session.post(
            f"{self.url}/domain-types/activation_run/actions/activate-changes/invoke",
            headers={
                "Content-Type": 'application/json',
                # (required) A header specifying which type of content is in the request/response body.
            },
            json={
                'redirect': False,
                'sites': [self.site],
                'force_foreign_changes': forceForeign
            },
            allow_redirects=True,
        )
        if resp.status_code == 200:
            return True
        elif resp.status_code == 204:
            return False
        else:
            return False