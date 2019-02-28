import requests
from django.contrib.auth.models import User
from datetime import timedelta 
from django.utils import timezone
import re

# BASEURL = 'https://public.agaveapi.co/'
BASEURL = 'https://api.tacc.utexas.edu/'

def agaveRequestUploadFile(token,fileName,system,location):
	"""Uploads a file to system with location
	Agave equivalent: jobs-upload -F fileName -S system location
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	files = {'fileToUpload': (fileName, open(fileName, 'rb')),}

	response = requests.post(BASEURL + 'files/v2/media/system/' + system + '/' + location, 
							 headers=headers, 
							 params=params, 
							 files=files, 
							 verify=False)
	return response.json()

def agaveRequestGetFile(token,path,fileName):
	headers = {'Authorization': 'Bearer ' + token}
	path = re.sub('listings','media',path)

	link = path + '/' + fileName
	response = requests.get(link, 
							headers=headers, 
							verify=False)
	return response

def agaveRequestJobSearch(token,jobName):
	"""Searches for all jobs with the name jobName.
	Agave equivalent: jbos-search 'name=jobName'
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('name', jobName),)

	response = requests.get(BASEURL + 'jobs/v2', 
							 headers=headers, 
							 params=params,  
							 verify=False)
	return response.json()

def agaveRequestJobsOutputList(token,jobId):
	"""List the output file of the given job.
	Agave equivalent: jobs-output-list jobId
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	print(jobId)

	response = requests.get(BASEURL + 'jobs/v2/' + jobId + '/outputs/listings/', 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestSystemsList(token):
	"""List available systems.
	Agave equivalent: systems-list -V
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'systems/v2/', 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestSubmitJob(token):
	"""Submit a new job.
	Agave equivalent: jobs-submit -F 'job.txt'
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	files = {
		'fileToUpload': ('job.txt', open('job.txt', 'rb')),
	}

	response = requests.post(BASEURL + 'jobs/v2/', 
							 headers=headers, 
							 params=params, 
							 files=files, 
							 verify=False)
	print('==========RESPONSE==========')
	print(response)
	return response.json()

def agaveRequestAppDetails(token,appid):
	"""Get the details of an application.
	Agave equivalent: apps-list -V appid
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'apps/v2/' + appid, 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestAppsList(token):
	"""Lists all applications available to the user
	Agave equivalent: apps-list
	"""
	headers = {'Authorization': 'Bearer ' + token}
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'apps/v2', 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestClientList(username, password, clientName='vDef'):
	"""List client
	Agave equivalent: clients-list -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.get(BASEURL + 'clients/v2/' + clientName, 
							params=params, 
							verify=False, 
							auth=(username, password))
	return response.json()

def agaveRequestClientDelete(username, password, clientName='vDef'):
	"""Delete client
	Agave equivalent: clients-delete -u username -p password clientName
	"""
	params = (('pretty', 'true'),)
	response = requests.delete(BASEURL + 'clients/v2/' + clientName, 
								params=params, 
								verify=False, 
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
								verify=False, 
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
								verify=False, 
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
								verify=False, 
								auth=(clientKey, clientSecret))
	return response.json()