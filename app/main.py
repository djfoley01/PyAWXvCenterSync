import pycurl
import cStringIO
import base64
import json
from pyVim.connect import Disconnect, SmartConnectNoSSL
from pyVmomi import vim
import atexit

def get_ansible_survey(survey_id):
    headers = { 'Authorization' : 'Basic %s' % base64.b64encode("admin:password") }
    response = cStringIO.StringIO()
    conn = pycurl.Curl()
    conn.setopt(pycurl.VERBOSE, 1)
    conn.setopt(pycurl.HTTPHEADER, ["%s: %s" % t for t in headers.items()])

    conn.setopt(pycurl.URL, "http://ashawx01.ash.com/api/v2/job_templates/" + survey_id + "/survey_spec/")
    conn.setopt(pycurl.HTTPGET, -1)
    conn.setopt(pycurl.SSL_VERIFYPEER, False)
    conn.setopt(pycurl.SSL_VERIFYHOST, False)
    conn.setopt(pycurl.WRITEFUNCTION, response.write)
    conn.perform()
    http_code = conn.getinfo(pycurl.HTTP_CODE)
    if http_code is 200:
        resp = json.loads(response.getvalue())
        return resp

def update_ansible_survey(survey, spec):
    x = 0
    for value in survey["spec"]:
        #print value['variable']
        if value['variable'] == "client_type":
            survey['spec'][x]['choices'] = spec
        x = x + 1
    print json.dumps(survey)
            
            
def GetVMHosts(content):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    obj = [host for host in host_view.view]
    host_view.Destroy()
    return obj

# Unused
def GetHostsSwitches(hosts):
    hostSwitchesDict = {}
    for host in hosts:
        switches = host.config.network.vswitch
        hostSwitchesDict[host] = switches
    return hostSwitchesDict

# Unused
def get_vds_object(dc):
    """Return dvSwitch object with specified name."""
    vds = list()
    network_folder = dc.networkFolder
    for net in network_folder.childEntity:
        print net
        if isinstance(net, vim.DistributedVirtualSwitch):
            vds.append(net.name)
    return vds

def get_portgroups(content):
    trunk_dvswitch_name = "dvSwitch"
    #dvswitch_obj = get_obj(content,
    #                            [vim.DistributedVirtualSwitch],
    #                            trunk_dvswitch_name)
    dvsportgroups = get_obj(content,
                                [vim.dvs.DistributedVirtualPortgroup],
                                trunk_dvswitch_name)
    port_groups = dvsportgroups
    return port_groups

def get_obj(content, vimtype, name):
    """Get the vsphere object associated with a given text name."""
    #obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                              vimtype, True)
    lobject = list()
    for containername in container.view:
        #temp = containername.name
        lobject.append(containername.name)
        #if containername.name != name:
        #   lobject.append(temp)
    return lobject

def main():
    serviceInstance = SmartConnectNoSSL(host="ashvc01.ash.com",user="svcawx@ash.com",pwd="Svc@wx1",port=443)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    vds_ports = get_portgroups(content)
    vds_ports_org = '\n'.join([str(x) for x in vds_ports]) 
    vds_ports_json = json.dumps(vds_ports_org)
    ans_survey = get_ansible_survey("7")
    update_ansible_survey(ans_survey, vds_ports_org)
    return
#hosts = GetVMHosts(content)
#hostSwitchesDict = GetHostsSwitches(hosts)

#for host, vswithes in hostSwitchesDict.items():
#  for v in vswithes:
    #print(v.name)

main()