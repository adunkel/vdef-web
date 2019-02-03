from django.shortcuts import render
import requests
from django.http import HttpResponse
from .agaveRequests import agaveRequestAppsList, agaveRequestAppDetails
from .forms import JobSubmitForm
from django import forms

def home(request):
	return render(request, 'vDefAgave/home.html')

def apps(request):
	user = request.user
	response = agaveRequestAppsList(user.profile.accesstoken)
	return render(request, 'vDefAgave/apps.html', response, {'title': 'Apps'})

def jobsubmit(request,id):
	user = request.user
	response = agaveRequestAppDetails(user.profile.accesstoken,id)
	parameters = response['result']['parameters']

	# if form.is_valid():
	# 	appId = form.cleaned_data.get("appId")
	# 	print(form.cleaned_data)

	if request.method == 'POST':
		form = JobSubmitForm(request.POST, parameters=parameters)
		if form.is_valid():
			print("valid!")
	else:
		form = JobSubmitForm(parameters=parameters)

	response = {
	"form": form,
	}
	return render(request, 'vDefAgave/jobsubmit.html', response, {'title': id})