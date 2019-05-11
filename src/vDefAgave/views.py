from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
import requests
from .agaveRequests import *
from .forms import *


def home(request):
	return render(request, 'vDefAgave/home.html')

@login_required
def appPemsUpdate(request,appId,updateUser):
	user = request.user
	response = agaveRequestAppsPemsUpdate(user,appId,updateUser)
	return JsonResponse(response)

@login_required
def appPemsList(request,appId):
	user = request.user
	response = agaveRequestAppPemsList(user,appId)
	return JsonResponse(response)

@login_required
def apps(request):
	user = request.user
	response = agaveRequestAppsList(user)

	apps = response['result']

	print(request)

	if request.method == 'POST':
		print(request.POST)
		form = AppsDropdownForm(request.POST, apps=apps)
		permForm = AppsGrantPermission(request.POST)
		if form.is_valid():
			updateUser = form.cleaned_data.get('updateUser')
			appId = form.cleaned_data.get('apps')
			print(updateUser)
			print(appId)
	else:
		permForm = AppsGrantPermission()
		form = AppsDropdownForm(apps=apps)

	context = {
		'form': form,
		'permForm': permForm,
		'response': response,
		'title': 'Apps'
	}
	return render(request, 'vDefAgave/apps.html', context)
	

@login_required
def systems(request):
	user = request.user
	response = agaveRequestSystemsList(user)
	context = {
		'response': response,
		'title': 'Systems'
	}
	return render(request, 'vDefAgave/systems.html', context)