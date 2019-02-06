from django.shortcuts import render
import requests
from django.http import HttpResponse
from .agaveRequests import *
from .forms import JobSubmitForm, JobSearchForm
from django import forms
import json
import os
from django.contrib import messages
import numpy as np
import itertools

def home(request):
	return render(request, 'vDefAgave/home.html')

def apps(request):
	user = request.user
	response = agaveRequestAppsList(user.profile.accesstoken)
	return render(request, 'vDefAgave/apps.html', response, {'title': 'Apps'})

def systems(request):
	user = request.user
	response = agaveRequestSystemsList(user.profile.accesstoken)
	return render(request, 'vDefAgave/systems.html', response, {'title': 'Systems'})

def joboutput(request,jobId):
	user = request.user
	response = agaveRequestJobsOutputList(user.profile.accesstoken,jobId)
	context = {
	'jobId': jobId,
	'output': response['result']
	}
	return render(request, 'vDefAgave/joboutput.html', context, {'title': jobId})

def jobsearch(request):
	user = request.user
	response = {}
	if request.method == 'POST':
		form = JobSearchForm(request.POST)
		if form.is_valid():
			jobName = form.cleaned_data.get('jobName')
			response = agaveRequestJobSearch(user.profile.accesstoken,jobName)
			if not response['result']:
				messages.warning(request, 'No jobs with the name %s were found.' % jobName)
	else:
		form = JobSearchForm()
	context = {
	'form': form,
	'response': response
	}
	return render(request, 'vDefAgave/jobsearch.html', context, {'title': 'Job Search'})

def jobsubmit(request,appId):
	user = request.user

	# Get application parameter details
	response = agaveRequestAppDetails(user.profile.accesstoken,appId)
	parameters = response['result']['parameters']

	# Get system option
	response = agaveRequestSystemsList(user.profile.accesstoken)
	availableSystems = response['result']

	if request.method == 'POST':
		form = JobSubmitForm(request.POST, parameters=parameters, availableSystems=availableSystems)
		if form.is_valid():
			# Extract form data
			name = form.cleaned_data.get('name')
			email = form.cleaned_data.get('email')
			executionSystem = form.cleaned_data.get('executionSystem')
			archiveSystem = form.cleaned_data.get('storageSystem')
			parameters = {}
			sweepParameters = {}
			for key, value in form.cleaned_data.items():
				if key.startswith('para'):
					key = key[5:]
					parameters[key] = value
				elif key.startswith('sweepPara') and key.endswith('start'):
					key = key[10:]
					key = key[0:-6]
					sweepParameters[key] = 0 #Just a placeholder
			parameters.update(sweepParameters)

			# Set other job values
			appId = appId
			batchQueue = 'CLUSTER'
			maxRunTime = '00:10:00'
			nodeCount = 1
			processorsPerNode = 1
			inputs = {}
			archive = True
			notification1 = {
				'url':email,
				'event':'FINISHED',
				'persistent':'true'
			}
			notification2 = {
				'url':email,
				'event':'FAILED',
				'persistent':'true'
			}
			notifications = [notification1, notification2]

			# Put everything into a dictionary
			job = {
				'name':name,
				'appId': appId,
				'executionSystem': executionSystem,
				'batchQueue': batchQueue,
				'maxRunTime': maxRunTime,
				'nodeCount': nodeCount,
				'processorsPerNode': processorsPerNode,
				'inputs': inputs,
				'parameters': parameters,
				'archive': archive,
				'archiveSystem': archiveSystem,
				'notifications': notifications
			}

			# Prepare parameter space
			space = []
			keys = []
			for key, value in sweepParameters.items():
				start = form.cleaned_data.get('sweepPara_%s_start' % key)
				end = form.cleaned_data.get('sweepPara_%s_end' % key)
				num = form.cleaned_data.get('sweepPara_%s_num' % key)
				space.append([int(x) for x in np.linspace(start=start, stop=end, num=num)])
				keys.append(key)

			# Iterate through all parameter combination and submit a job for each
			fileName = 'job.txt'
			jobids = []
			failedJobs = []
			for paraCombination in list(itertools.product(*space)):
				for i in range(len(keys)):
					# Create job file to submit
					job['parameters']['%s' % keys[i]] = paraCombination[i]
					with open(fileName, 'w') as outfile:  
						json.dump(job, outfile, indent=4)

				# Submit the job
				response = agaveRequestSubmitJob(user.profile.accesstoken)

				if response['status'] == 'success':
					jobids.append(response['result']['id'])
				else:
					failedJobs.append(response['message'])

			if len(jobids) > 0:
				messages.success(request, 'Successfully submitted %d job(s) with the ids %s.' % (len(jobids),jobids))
			if len(failedJobs) > 0:
				messages.warning(request, '%d job(s) failed with messages %s' % (len(failedJobs),failedJobs))

			if os.path.exists(fileName):
				os.remove(fileName)
	else:
		form = JobSubmitForm(parameters=parameters,availableSystems=availableSystems)

	context = {
	'form': form,
	'appId': appId
	}
	return render(request, 'vDefAgave/jobsubmit.html', context, {'title': appId})