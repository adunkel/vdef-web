from django.shortcuts import render
import requests
from django.http import HttpResponse
from .agaveRequests import agaveRequestAppsList, agaveRequestAppDetails,agaveRequestSubmitJob
from .forms import JobSubmitForm
from django import forms
import json
import os
from django.contrib import messages

def home(request):
	return render(request, 'vDefAgave/home.html')

def apps(request):
	user = request.user
	response = agaveRequestAppsList(user.profile.accesstoken)
	return render(request, 'vDefAgave/apps.html', response, {'title': 'Apps'})

def jobsubmit(request,appId):
	user = request.user

	# Get application parameter details
	response = agaveRequestAppDetails(user.profile.accesstoken,appId)
	parameters = response['result']['parameters']

	if request.method == 'POST':
		form = JobSubmitForm(request.POST, parameters=parameters)
		if form.is_valid():
			# Extract form data
			name = form.cleaned_data.get("name")
			email = form.cleaned_data.get("email")
			parameters = {}
			for key, value in form.cleaned_data.items():
				if key.startswith('para'):
					key = key[5:]
					parameters[key] = value

			# Set other job values
			appId = appId
			executionSystem = "schur-execution-fdunke1"
			batchQueue = "CLUSTER"
			maxRunTime = "00:10:00"
			nodeCount = 1
			processorsPerNode = 1
			inputs = {}
			archive = True
			archiveSystem = "schur-storage-fdunke1"
			notification1 = {
				"url":email,
				"event":"FINISHED",
				"persistent":"true"
			}
			notification2 = {
				"url":email,
				"event":"FAILED",
				"persistent":"true"
			}
			notifications = [notification1, notification2]

			# Put everything into a dictionary
			job = {
				"name":name,
				"appId": appId,
				"executionSystem": executionSystem,
				"batchQueue": batchQueue,
				"maxRunTime": maxRunTime,
				"nodeCount": nodeCount,
				"processorsPerNode": processorsPerNode,
				"inputs": inputs,
				"parameters": parameters,
				"archive": archive,
				"archiveSystem": archiveSystem,
				"notifications": notifications
			}

			# Create job file to submit
			fileName = 'job.txt'
			with open(fileName, 'w') as outfile:  
				json.dump(job, outfile, indent=4)

			# Submit the job
			response = agaveRequestSubmitJob(user.profile.accesstoken)

			if response['status'] == 'success':
				messages.success(request, 'The job was submitted successfully.')
			else:
				messages.error(request, response['message'])

			if os.path.exists(fileName):
				os.remove(fileName)
	else:
		form = JobSubmitForm(parameters=parameters)

	context = {
	"form": form,
	"appId": appId
	}
	return render(request, 'vDefAgave/jobsubmit.html', context, {'title': appId})