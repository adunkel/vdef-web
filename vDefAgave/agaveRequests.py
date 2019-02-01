import requests
from django.contrib.auth.models import User
from datetime import timedelta 
from django.utils import timezone

BASEURL = 'https://public.agaveapi.co/'

def agaveRequestAppDetails(token,appid):
	headers = {
	    'Authorization': 'Bearer ' + token,
	}

	params = (
	    ('pretty', 'true'),
	)

	response = requests.get(BASEURL + 'apps/v2/' + appid, 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestAppsList(token):
	headers = {
		'Authorization': 'Bearer ' + token,
	}

	params = (
		('pretty', 'true'),
	)

	response = requests.get(BASEURL + 'apps/v2', 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestCreateClient(username, password, clientName='vDef'):
	params = (
	    ('pretty', 'true'),
	)

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
	clientKey = user.profile.clientkey
	clientSecret = user.profile.clientsecret
	refreshToken = user.profile.refreshtoken

	headers = {
    	'Content-Type': 'application/x-www-form-urlencoded',
	}

	data = {
		'grant_type': 'refresh_token',
		'refresh_token': refreshToken,
		'scope': 'PRODUCTION'
	}

	response = requests.post(BASEURL + '/token', 
								headers=headers, data=data, 
								verify=False, 
								auth=(clientKey, clientSecret))
	response = response.json()
	if not 'error' in response:
		user.profile.accesstoken = response['access_token']
		user.profile.refreshtoken = response['refresh_token']
		expiresIn = response['expires_in']
		currentTime = timezone.now()
		user.profile.expiresin = expiresIn
		user.profile.timecreated = currentTime
		user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
		user.save()