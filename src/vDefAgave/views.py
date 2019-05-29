from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
import requests, json
from .agaveRequests import *
from .forms import *


def home(request):
	return render(request, 'vDefAgave/home.html')

@login_required
def systemRoleUpdate(request,systemId,updateUser,role):
	user = request.user
	response = agaveRequestSystemsRolesUpdate(user,systemId,updateUser,role)
	return JsonResponse(response)

@login_required
def systemRolesList(request,systemId):
	user = request.user
	response = agaveRequestSystemsRolesList(user,systemId)
	print(response)
	return JsonResponse(response)

@login_required
def appPemsUpdate(request,appId,updateUser,perm):
	user = request.user
	response = agaveRequestAppsPemsUpdate(user,appId,updateUser,perm)
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

	if request.method == 'POST':
		form = AppsDropdownForm(request.POST, apps=apps)
		permForm = AppsGrantPermission(request.POST)
		if form.is_valid():
			updateUser = form.cleaned_data.get('updateUser')
			appId = form.cleaned_data.get('apps')
	else:
		permForm = AppsGrantPermission()
		form = AppsDropdownForm(apps=apps)

	context = {
		'form': form,
		'permForm': permForm,
		'apps': json.dumps(apps),
		'title': 'Apps'
	}
	return render(request, 'vDefAgave/apps.html', context)
	

@login_required
def systems(request):
	user = request.user
	response = agaveRequestSystemsList(user)

	systems = response['result']

	roleForm = SystemsGrantRole()
	dropdownForm = SystemsDropdownForm(systems=systems)

	context = {
		'dropdownForm': dropdownForm,
		'roleForm': roleForm,
		'systems': json.dumps(systems),
		'thisUser': user.username,
		'title': 'Systems'
	}
	return render(request, 'vDefAgave/systems.html', context)