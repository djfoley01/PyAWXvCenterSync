# PyAWXvCenterSync

Example code

The plugin is fully functional at this time. Only cleanup left is required.

### Setup

Pre-Reqs:
```python
pip install -r requirements.txt
```

Requirements (app/requirements.txt):
* pycurl==7.43.0
* requests==2.18.4
* psycopg2==2.7.3.2
* pyVim==0.0.21
* pyVmomi==6.5.0.2017.5-1

### OverView

Variables:
* vCenter
  * host = vcenter_fqdn
  * user = user@domain
  * pwd = password
  * port = port (usually 443)
  * trunk_dvswitch_name = dvSwitch (may not be in the future)
* Ansible AWX
  * host = ansible_fqdn
  * user = user
  * password = password
  * survey_spec_id = integer
* Postgres
  * hostname = pgsql_fqdn
  * user = db_user
  * password db_password
  * database = db

Main Function:
```python
def main():
    # Initiate Connection to vCenter
    serviceInstance = SmartConnectNoSSL(host="ashvc01.ash.com",user="svcawx@ash.com",pwd="Svc@wx1",port=443)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    survey_id = "7"
    
    # Get a list of all the portgroups
    vds_ports = get_portgroups(content)
    # Use regex filter to remove anything that starts with two lowercase letters
    regex = re.compile('[^a-z]{2,}')
    filtered_ports = [i for i in vds_ports if regex.match(i)]
    vds_ports_org = '\n'.join([str(x) for x in filtered_ports]) 
 
    # Get the ansible survey based on the survey_id 
    ans_survey = get_ansible_survey(survey_id)
    
    # Execute the ansible survey update based on the prior queries
    update_ansible_survey(ans_survey, survey_id, vds_ports_org)
    return
```

Current Output:
```
{"description": "", "name": "", "spec": [{"question_description": "", "min": 0, "default": "ashvc01.ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_server", "question_name": "Vcenter server:", "type": "text"}, {"question_description": "", "min": 0, "default": "svcawx@ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_user", "question_name": "Vcenter user:", "type": "text"}, {"question_description": "", "min": 0, "default": "$encrypted$", "max": 32, "required": true, "choices": "", "new_question": true, "variable": "vcenter_password", "question_name": "Vcenter password:", "type": "password"}, {"question_description": "", "min": null, "default": "type1", "max": null, "required": true, "choices": "ABC-PROD-VLAN123\nDEF-DEV-VLAN1234\ndvPortGroup\ndvPortGroup2\ndvSwitch-DVUplinks-381\ndvSwitch2-DVUplinks-384", "new_question": true, "variable": "client_type", "question_name": "Type", "type": "multiplechoice"}]}
```

Postgres Query:
```python
query = """UPDATE main_jobtemplate
                   SET survey_spec = %s 
                   WHERE unifiedjobtemplate_ptr_id = %s"""
```
### Features

Feature list:

 * Synchronizes list of all portgroups from vCenter

 Future features:
 
 * Synchronizes list of all resource groups from vCenter
 * Synchronizes list of available networks (Subnets, IP's, gateways)
 