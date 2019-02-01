from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
import requests
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.forms.utils import ErrorDict
from django.http import HttpResponseRedirect
from datetime import timedelta 
from django.utils import timezone


@login_required
def profile(request):
	return render(request, 'users/profile.html')

class CustomLoginView(LoginView):
	def post(self, request, *args, **kwargs):
		username = request.POST['username']
		password = request.POST['password']
		form = self.get_form()
		print(form)
		user = User.objects.filter(username=username).first()
		if user is None:
			print('User %s does not exists.' % username)
			user = createuser(username,password)
		if user is not None and not form.is_valid():
			print('Logging in user manually')
			login(self.request, user)
			return HttpResponseRedirect(self.get_success_url())
		print('Using super.post')
		if form.is_valid():
			print('Refreshing the token')
			agaveRequestRefreshToken(user)
		return super().post(self, request, *args, **kwargs)

def createuser(username,password):
	user = User.objects.create_user(username=username, password=password)

	clientResponse = agaveRequestCreateClient(username, password)
	print(clientResponse)
	if clientResponse['status'] == 'success':
		user.profile.clientkey = clientResponse['result']['consumerKey']
		user.profile.clientsecret = clientResponse['result']['consumerSecret']

		tokenResponse = agaveRequestCreateToken(username, password, user)
		print(tokenResponse)
		if not 'error' in tokenResponse:
			user.profile.accesstoken = tokenResponse['access_token']
			user.profile.refreshtoken = tokenResponse['refresh_token']
			expiresIn = tokenResponse['expires_in']
			currentTime = timezone.now()
			user.profile.expiresin = expiresIn
			user.profile.timecreated = currentTime
			user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
			user.save()
			return user
	user.delete()
	return None

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

	response = requests.post('https://public.agaveapi.co/clients/v2/', 
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

	response = requests.post('https://public.agaveapi.co/token', 
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

	response = requests.post('https://public.agaveapi.co//token', 
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
