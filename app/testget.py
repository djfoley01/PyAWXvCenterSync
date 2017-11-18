import requests
url = "http://ashawx01.ash.com/api/v2/job_templates/7/survey_spec/"
resp = requests.post(url, data={}, auth=('admin', 'password'))
print resp.content