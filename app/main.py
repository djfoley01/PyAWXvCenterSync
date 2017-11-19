import pycurl
import cStringIO
import base64
import json
from pyVim.connect import Disconnect, SmartConnectNoSSL
from pyVmomi import vim
import atexit
import psycopg2

# Query Ansible AWX to obtain the survey_spec
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

# Needs to be updated to execute postgres query using the updated survey
def update_ansible_survey(survey, survey_id, spec):
    x = 0
    for value in survey["spec"]:
        #print value['variable']
        if value['variable'] == "client_type":
            survey['spec'][x]['choices'] = spec
        x = x + 1
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host="ashawx01",database="awx", user="awx", password="awxpass")
 
        # create a cursor
        cur = conn.cursor()
        # execute a statement
        print('Update survey_spec:')
        query = """UPDATE main_jobtemplate
                   SET survey_spec = %s 
                   WHERE unifiedjobtemplate_ptr_id = %s"""
        json_survey = json.dumps(survey)
        cur.execute(query, (json_survey, survey_id))
 
        # display the PostgreSQL database server version
        updated_rows = cur.rowcount
        conn.commit()
        print('Updated Rows:')
        print(updated_rows)
       
        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
# Unused
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

# Get the virtual portgroups from vcenter
def get_portgroups(content):
    trunk_dvswitch_name = "dvSwitch"
    dvsportgroups = get_obj(content,
                                [vim.dvs.DistributedVirtualPortgroup],
                                trunk_dvswitch_name)
    port_groups = dvsportgroups
    return port_groups

# Find and gather objects from vCenter, executed by get_portgroups
def get_obj(content, vimtype, name):
    """Get the vsphere object associated with a given text name."""
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                              vimtype, True)
    lobject = list()
    for containername in container.view:
        lobject.append(containername.name)
    return lobject

# Main Function
def main():
    # Initiate Connection to vCenter
    serviceInstance = SmartConnectNoSSL(host="ashvc01.ash.com",user="svcawx@ash.com",pwd="Svc@wx1",port=443)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    survey_id = "7"
    
    # Get a list of all the portgroups
    vds_ports = get_portgroups(content)
    vds_ports_org = '\n'.join([str(x) for x in vds_ports]) 
 
    # Get the ansible survey based on the survey_id 
    ans_survey = get_ansible_survey(survey_id)
    
    # Execute the ansible survey update based on the prior queries
    update_ansible_survey(ans_survey, survey_id, vds_ports_org)
    return


main()