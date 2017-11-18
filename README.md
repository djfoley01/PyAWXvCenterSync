# PyAWXvCenterSync

Example code, currently missing postgres connection and query to update final survey_spec

The current output can be directly used to update the specific Ansible AWX postgres database.
The only task now is to simply create a function to update the postgres database.

### Setup

Pre-Reqs:
```python
pip install -r requirements.txt
```

Requirements (app/requirements.txt):
* pycurl==7.43.0
* requests==2.18.4
* pyVim==0.0.21
* pyVmomi==6.5.0.2017.5-1

### OverView

Variables:
* vCenter
  * host = <vcenter_fqdn>
  * user = <user>@<domain>
  * pwd = <password>
  * port = <port> (usually 443)
* Ansible AWX
  * host = <ansible_fqdn>
  * user = <user>
  * password = <password>
  * survey_spec_id = <integer>
* Postgres
  * TBD

Main Function:
```python
def main():
    serviceInstance = SmartConnectNoSSL(host="ashvc01.ash.com",user="svcawx@ash.com",pwd="#####",port=443)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    vds_ports = get_portgroups(content)
    vds_ports_org = '\n'.join([str(x) for x in vds_ports]) 
    #vds_ports_json = json.dumps(vds_ports_org)
    ans_survey = get_ansible_survey("7")
    update_ansible_survey(ans_survey, vds_ports_org)
    return
```

Current Output:
```
{"description": "", "name": "", "spec": [{"question_description": "", "min": 0, "default": "ashvc01.ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_server", "question_name": "Vcenter server:", "type": "text"}, {"question_description": "", "min": 0, "default": "svcawx@ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_user", "question_name": "Vcenter user:", "type": "text"}, {"question_description": "", "min": 0, "default": "$encrypted$", "max": 32, "required": true, "choices": "", "new_question": true, "variable": "vcenter_password", "question_name": "Vcenter password:", "type": "password"}, {"question_description": "", "min": null, "default": "type1", "max": null, "required": true, "choices": "ABC-PROD-VLAN123\nDEF-DEV-VLAN1234\ndvPortGroup\ndvPortGroup2\ndvSwitch-DVUplinks-381\ndvSwitch2-DVUplinks-384", "new_question": true, "variable": "client_type", "question_name": "Type", "type": "multiplechoice"}]}
```

Postgres Query:
```
UPDATE main_jobtemplate
SET survey_spec = '{"description": "", "name": "", "spec": [{"question_description": "", "min": 0, "default": "ashvc01.ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_server", "question_name": "Vcenter server:", "type": "text"}, {"question_description": "", "min": 0, "default": "svcawx@ash.com", "max": 1024, "required": true, "choices": "", "new_question": true, "variable": "vcenter_user", "question_name": "Vcenter user:", "type": "text"}, {"question_description": "", "min": 0, "default": "$encrypted$", "max": 32, "required": true, "choices": "", "new_question": true, "variable": "vcenter_password", "question_name": "Vcenter password:", "type": "password"}, {"question_description": "", "min": null, "default": "type1", "max": null, "required": true, "choices": "ABC-PROD-VLAN123\nDEF-DEV-VLAN1234\ndvPortGroup\ndvPortGroup2\ndvSwitch-DVUplinks-381\ndvSwitch2-DVUplinks-384", "new_question": true, "variable": "client_type", "question_name": "Type", "type": "multiplechoice"}]}'
WHERE unifiedjobtemplate_ptr_id = '7'
```
### Features

Feature list:

 * Synchronizes list of all portgroups from vCenter

 Future features:
 
 * Synchronizes list of all resource groups from vCenter
 * Synchronizes list of available networks (Subnets, IP's, gateways)
 