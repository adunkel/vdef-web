import requests
from django.contrib.auth.models import User
from datetime import timedelta 
from django.utils import timezone
import re, json

# BASEURL = 'https://public.agaveapi.co/'
BASEURL = 'https://api.tacc.utexas.edu/'

def agaveRequestMetadataList(user):
	"""List metadata
	Agave equivalent: metadata-list
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
	Agave equivalent: metadata-addupdate
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
	Agave equivalent: jobs-upload -F - <<< data -S system location
	"""
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	files = {
		'fileToUpload': (None, data),
		'fileName': (None, fileName),
	}

	response = requests.post(BASEURL + 'files/v2/media/system/' + system + '/' + location, 
							 headers=headers, 
							 params=params, 
							 files=files, 
							 verify=True)
	print('===File Uploaded===')
	print(response.json())
	return response.json()

def agaveRequestGetFile(user,path,fileName):
	user = checkAuth(user)
	token = user.profile.accesstoken

	headers = {'Authorization': 'Bearer ' + token}
	path = re.sub('listings','media',path)

	link = path + '/' + fileName
	response = requests.get(link, 
							headers=headers, 
							verify=True)
	return response

def agaveRequestJobSearch(user,jobName='',jobId=''):
	"""Searches for all jobs with the name jobName.
	Agave equivalent: jobs-search 'name=jobName'
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
	Agave equivalent: jobs-output-list jobId
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
	Agave equivalent: systems-list -V
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
	Agave equivalent: jobs-submit -F - <<< data
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

	response = requests.post(BASEURL + 'jobs/v2/', 
							 headers=headers, 
							 params=params, 
							 data=data, 
							 verify=True)
	print('===Job Submitted===')
	print(response)
	print(response.json())
	return response.json()

def agaveRequestAppDetails(user,appid):
	"""Get the details of an application.
	Agave equivalent: apps-list -V appid
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
	Agave equivalent: apps-list
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
	Agave equivalent: clients-list -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'clients/v2/' + clientName, 
							params=params, 
							verify=True, 
							auth=(username, password))
	return response.json()

def agaveRequestClientDelete(username, password, clientName='vDef'):
	"""Delete client
	Agave equivalent: clients-delete -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.delete(BASEURL + 'clients/v2/' + clientName, 
								params=params, 
								verify=True, 
								auth=(username, password))
	return response.json()

def agaveRequestCreateClient(username, password, clientName='vDef'):
	"""Create a new client
	Agave equivalent: clients-create -u username -p password -N clientName
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
	Agave equivalent: auth-tokens-create -u username -p password
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
	Agave equivalent: auth-tokens-refresh
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
	return response