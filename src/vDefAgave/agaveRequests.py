import requests
from django.contrib.auth.models import User
from datetime import timedelta 
from django.utils import timezone
import re, json

# BASEURL = 'https://public.agaveapi.co/'
BASEURL = 'https://api.tacc.utexas.edu/'

def agaveRequestCommon(user):
	user = checkAuth(user)
	token = user.profile.accesstoken
	headers = {'Authorization': 'Bearer ' + token,}
	params = (('pretty', 'true'),)
	return token,headers,params

def agaveRequestGet(urlExt, headers, params):
	response = None
	attempts = 1
	while response is None and attempts <= 3:
		try:
			response = requests.get(BASEURL + urlExt, 
									 headers=headers, 
									 params=params, 
									 verify=True)
		except:
			print('Agave request error. Attempt', attempts)
	return response

def agaveRequestPost(urlExt, headers, params, data):
	response = None
	attempts = 1
	while response is None and attempts <= 3:
		try:
			response = requests.post(BASEURL + urlExt, 
									 headers=headers, 
									 params=params, 
									 data=data,
									 verify=True)
		except:
			print('Agave request error. Attempt', attempts)
	return response

def agaveRequestSystemsRolesUpdate(user,systemId,updateUser,role):
	"""Gives updateUser the role for systemId
	Agave CLI: systems-roles-addupdate -u updateUser -r role systemId
	"""
	token,headers,params = agaveRequestCommon(user)
	headers['Content-Type'] = 'application/json'

	data = json.dumps({'role': role})
	urlExt = 'systems/v2/' + systemId + '/roles/' + updateUser
	response = agaveRequestPost(urlExt=urlExt, headers=headers, params=params, data=data)
	return response.json()

def agaveRequestSystemsRolesList(user,systemId):
	"""Lists roles of system
	Agave CLI: systems-roles-list systemId
	"""
	token,headers,params = agaveRequestCommon(user)
	urlExt = 'systems/v2/' + systemId + '/roles/'
	print(urlExt)
	response = agaveRequestGet(urlExt=urlExt, headers=headers, params=params)
	print(response.text)
	return response.json()

def agaveRequestAppsPemsUpdate(user,appId,updateUser):
	"""Gives updateUser permission for appId
	Agave CLI: apps-pems-update -u updateUser -p ALL appId
	"""
	token,headers,params = agaveRequestCommon(user)
	urlExt = 'apps/v2/' + appId + '/pems/' + updateUser
	data = {'permission': 'ALL'}
	response = agaveRequestPost(urlExt=urlExt, headers=headers, params=params, data=data)
	return response.json()

def agaveRequestAppPemsList(user,appId):
	"""Lists permission of app
	Agave CLI: apps-pems-list appId
	"""
	token,headers,params = agaveRequestCommon(user)
	urlExt = 'apps/v2/' + appId + '/pems/'
	response = agaveRequestGet(urlExt=urlExt, headers=headers, params=params)
	return response.json()


def agaveRequestMetadataList(user):
	"""List metadata
	Agave CLI: metadata-list
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token,}

	q = {"name":"vDef"}
	q = json.dumps(q)

	params = (
		('q', q),
	    ('pretty', 'true'),
	)

	response = requests.get(BASEURL + 'meta/v2/data/', 
							headers=headers, 
							params=params, 
							verify=True)

	return response.json()

def agaveRequestMetadataUpdate(user,jobIds,jobName,templates,parameters,paraValues):
	"""Update metadata
	Agave CLI: metadata-addupdate
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {
		'Authorization': 'Bearer ' + token,
		'Content-Type': 'application/json',
	}
	params = (('pretty', 'true'),)

	data = {
				"value": {
					"jobName": jobName,
					"templates": templates,
					"parameters": parameters,
					"paraValues": dict(zip(jobIds,paraValues))
				}, 
				"name": "vDef", 
				"associationIds": jobIds
		   }
	data = json.dumps(data)

	response = requests.post(BASEURL + 'meta/v2/data/', 
							 headers=headers, 
							 params=params, 
							 data=data, 
							 verify=True)
	return response.json()

def agaveRequestUploadFile(user,data,fileName,system,location):
	"""Uploads a file to system with location
	Agave CLI: jobs-upload -F - <<< data -S system location
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	files = {
		'fileToUpload': (None, data),
		'fileName': (None, fileName),
	}

	print('===File Uploaded===')
	response = None
	while response is None:
		try:
			response = requests.post(BASEURL + 'files/v2/media/system/' + system + '/' + location, 
									 headers=headers, 
									 params=params, 
									 files=files, 
									 verify=True)
		except:
			print('===Error===')
	
	print(response.json())
	return response.json()

def agaveRequestGetFile(user,path,fileName):
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	path = re.sub('listings','media',path)

	link = path + '/' + fileName
	response = None
	while response is None:
		try:
			response = requests.get(link, 
									headers=headers, 
									verify=True)
		except:
			print('===Error===')
	return response

def agaveRequestJobSearch(user,jobName='',jobId=''):
	"""Searches for all jobs with the name jobName.
	Agave CLI: jobs-search 'name=jobName'
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	# params = (('pretty', 'true'),)
	if jobName:
		params = (('name', jobName),)
	if jobId:
		params = (('id', jobId),)

	response = requests.get(BASEURL + 'jobs/v2', 
							 headers=headers, 
							 params=params,  
							 verify=True)
	return response.json()

def agaveRequestJobsOutputList(user,jobId):
	"""List the output file of the given job.
	Agave CLI: jobs-output-list jobId
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)

	response = requests.get(BASEURL + 'jobs/v2/' + jobId + '/outputs/listings/', 
							headers=headers, 
							params=params, 
							verify=True)
	return response.json()

def agaveRequestSystemsList(user):
	"""List available systems.
	Agave CLI: systems-list -V
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'systems/v2/', 
							headers=headers, 
							params=params, 
							verify=True)
	return response.json()

def agaveRequestSubmitJob(user,data):
	"""Submit a new job.
	Agave CLI: jobs-submit -F - <<< data
	Note: the dict data needs to be in double quotes.
	Use json.dumps(data) if needed
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {
		'Authorization': 'Bearer ' + token,
		'Content-Type': 'application/json',
	}
	params = (('pretty', 'true'),)
	data = data

	response = None
	print('===Job Submitted===')
	while response is None:
		try:
			response = requests.post(BASEURL + 'jobs/v2/', 
									 headers=headers, 
									 params=params, 
									 data=data, 
									 verify=True)
		except:
			print('===Error===')
	
	print(response)
	print(response.json())
	return response.json()

def agaveRequestAppDetails(user,appid):
	"""Get the details of an application.
	Agave CLI: apps-list -V appid
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'apps/v2/' + appid, 
							headers=headers, 
							params=params, 
							verify=True)
	return response.json()

def agaveRequestAppsList(user):
	"""Lists all applications available to the user
	Agave CLI: apps-list
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken
	
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'apps/v2', 
							headers=headers, 
							params=params, 
							verify=True)
	return response.json()

def agaveRequestClientList(username, password, clientName='vDef'):
	"""List client
	Agave CLI: clients-list -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'clients/v2/' + clientName, 
							params=params, 
							verify=True, 
							auth=(username, password))
	return response.json()

def agaveRequestClientDelete(username, password, clientName='vDef'):
	"""Delete client
	Agave CLI: clients-delete -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.delete(BASEURL + 'clients/v2/' + clientName, 
								params=params, 
								verify=True, 
								auth=(username, password))
	return response.json()

def agaveRequestCreateClient(username, password, clientName='vDef'):
	"""Create a new client
	Agave CLI: clients-create -u username -p password -N clientName
	"""
	params = (('pretty', 'true'),)
	data = {
		'clientName': clientName,
		'tier': 'Unlimited',
		'description': '',
		'callbackUrl': ''
	}
	response = requests.post(BASEURL + 'clients/v2/', 
								params=params, 
								data=data, 
								verify=True, 
								auth=(username, password))
	return response.json()

def agaveRequestCreateToken(username, password, user):
	"""Create a new token
	Agave CLI: auth-tokens-create -u username -p password
	"""
	data = {
	  'username': username,
	  'password': password,
	  'grant_type': 'password',
	  'scope': 'PRODUCTION'
	}

	clientkey = user.profile.clientkey
	clientsecret = user.profile.clientsecret

	response = requests.post(BASEURL + 'token', 
								data=data, 
								verify=True, 
								auth=(clientkey, clientsecret))
	return response.json()

def agaveRequestRefreshToken(user):
	"""Refresh the token
	Saves new token to user profile
	Agave CLI: auth-tokens-refresh
	"""
	clientKey = user.profile.clientkey
	clientSecret = user.profile.clientsecret
	refreshToken = user.profile.refreshtoken

	headers = {'Content-Type': 'application/x-www-form-urlencoded',}
	data = {
		'grant_type': 'refresh_token',
		'refresh_token': refreshToken,
		'scope': 'PRODUCTION'
	}

	response = requests.post(BASEURL + 'token', 
								headers=headers, data=data, 
								verify=True, 
								auth=(clientKey, clientSecret))
	return response.json()

def agaveRequestStopJob(user,jobId):
	"""Stop a job
	Agave CLI: jobs-stop jobid
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken
	
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	data = {'action': 'stop'}

	response = requests.post(BASEURL + 'jobs/v2/' + jobId, 
								headers=headers, 
								params=params, 
								data=data, 
								verify=True)
	print(response.json())
	return response.json()

def checkAuth(user):
	"""Refresh token and saves to user profile"""
	user = User.objects.filter(username=user.username).first()
	expiresAt = user.profile.expiresat
	currentTime = timezone.now()
	if expiresAt < currentTime:
		response = agaveRequestRefreshToken(user)
		user.profile.accesstoken = response['access_token']
		user.profile.refreshtoken = response['refresh_token']
		expiresIn = response['expires_in']
		currentTime = timezone.now()
		user.profile.expiresin = expiresIn
		user.profile.timecreated = currentTime
		user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
		user.save()
	return user

def waitForIt(eventid,key):
	params = (
	    ('eventid', eventid),
	    ('key', key),
	    ('tmout', '120'),
	)
	response = requests.get('http://melete05.cct.lsu.edu/event', params=params)
	if response.text == '':
		result = {eventid: None}
	else:
		result = response.json()
	return result