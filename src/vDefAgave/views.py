from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import requests
from .agaveRequests import agaveRequestAppsList, agaveRequestSystemsList
from .forms import AppsDropdownForm


def home(request):
	return render(request, 'vDefAgave/home.html')

@login_required
def apps(request):
	user = request.user
	response = agaveRequestAppsList(user)

	apps = response['result']

	form = AppsDropdownForm(apps=apps)
	context = {
		'form': form,
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