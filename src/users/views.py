from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from datetime import timedelta 
from django.utils import timezone
from vDefAgave.agaveRequests import *


@login_required
def profile(request):
	return render(request, 'users/profile.html')

class CustomLoginView(LoginView):
	def post(self, request, *args, **kwargs):
		username = request.POST['username']
		password = request.POST['password']
		form = self.get_form()
		user = User.objects.filter(username=username).first()
		if user is not None and form.is_valid():
			# User exists
			if refreshToken(user):
				return super().post(self, request, *args, **kwargs)
		if user is None:
			createUser(username,password)
		if clientExists(username,password):
			# Delete Client
			if not deleteClient(username,password):
				messages.warning(request, 'Client could not be deleted.')
				return render(request, 'users/login.html', {'form':form})
		# Create Client
		if not createClient(username,password):
			messages.warning(request, 'Client could not be created.')
			return render(request, 'users/login.html', {'form':form})
		# Create Token
		if not createToken(username,password):
			messages.warning(request, 'Token could not be created.')
			return render(request, 'users/login.html', {'form':form})
		user = User.objects.filter(username=username).first()
		login(self.request, user)
		return HttpResponseRedirect(self.get_success_url())

def refreshToken(user):
	"""Refresh token and saves to user profile"""
	response = agaveRequestRefreshToken(user)
	if not 'error' in response:
		user.profile.accesstoken = response['access_token']
		user.profile.refreshtoken = response['refresh_token']
		expiresIn = response['expires_in']
		currentTime = timezone.now()
		user.profile.expiresin = expiresIn
		user.profile.timecreated = currentTime
		user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
		user.save()
		return True
	return False

def createClient(username,password):
	"""Create client and saves to user profile"""
	user = User.objects.filter(username=username).first()
	response = agaveRequestCreateClient(username, password)
	if response['status'] == 'success':
		user.profile.clientkey = response['result']['consumerKey']
		user.profile.clientsecret = response['result']['consumerSecret']
		user.save()
		return True
	return False

def clientExists(username,password):
	"""Check if client exists"""
	response = agaveRequestClientList(username=username, password=password)
	if response['status'] == 'success':
		return True
	return False

def deleteClient(username,password):
	"""Delete client"""
	response = agaveRequestClientDelete(username=username, password=password)
	if response['status'] == 'success':
		return True
	return False

def createToken(username,password):
	"""Create token and saves to user profile"""
	user = User.objects.filter(username=username).first()
	response = agaveRequestCreateToken(username, password, user)
	if not 'error' in response:
		user.profile.accesstoken = response['access_token']
		user.profile.refreshtoken = response['refresh_token']
		expiresIn = response['expires_in']
		currentTime = timezone.now()
		user.profile.expiresin = expiresIn
		user.profile.timecreated = currentTime
		user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
		user.save()
		return True
	return False

def createUser(username,password):
	"""Create user"""
	user = User.objects.create_user(username=username, password=password)
	user.save()
	return user