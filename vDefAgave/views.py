from django.shortcuts import render
import requests
from django.http import HttpResponse
from .agaveRequests import agaveRequestAppsList, agaveRequestAppDetails

def home(request):
	return render(request, 'vDefAgave/home.html')

def apps(request):
	user = request.user
	response = agaveRequestAppsList(user.profile.accesstoken)
	return render(request, 'vDefAgave/apps.html', response, {'title': 'Apps'})

def jobsubmit(request,id):
	user = request.user
	response = agaveRequestAppDetails(user.profile.accesstoken,id)
	return render(request, 'vDefAgave/jobsubmit.html', response, {'title': id})