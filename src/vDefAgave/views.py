from django.shortcuts import render, redirect, reverse
import requests
from django.http import HttpResponse, JsonResponse
from .agaveRequests import *
from .forms import JobSubmitForm, JobSearchForm, JobSetupForm
from django import forms
import json
import os
import re
from django.contrib import messages
import numpy as np
import itertools
from django.contrib.auth.models import User
import time

def home(request):
	return render(request, 'vDefAgave/home.html')

def chart(request):
	return render(request, 'vDefAgave/chart.html')

def getData(request):
	usersCount = User.objects.all().count()
	labels = ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"]
	defaultItems = [usersCount, 1,2,3,4,5]
	data = {
		'labels': labels,
		'default': defaultItems,
	}
	return JsonResponse(data)

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

def jobsetup(request):
	appId = request.GET.get('appId','')
	user = request.user

	# Get application parameter details
	response = agaveRequestAppDetails(user.profile.accesstoken,appId)
	inputs = response['result']['inputs']

	# Get system option
	response = agaveRequestSystemsList(user.profile.accesstoken)
	availableSystems = response['result']

	if request.method == 'POST':
		form = JobSetupForm(request.POST, request.FILES, inputs=inputs, availableSystems=availableSystems)
		if form.is_valid():

			# Extract form data
			executionSystem = form.cleaned_data.get('executionSystem')
			archiveSystem = form.cleaned_data.get('storageSystem')
			geoFileName = ''
			yamlFileName = ''

			# Save files to server
			for key, value in request.FILES.items():
				file = request.FILES[key]
				fileName = request.FILES[key].name

				if key == 'geoFile':
					geoFileName = fileName
				elif key == 'yamlFile':
					yamlFileName = fileName

				with open(fileName, 'wb+') as destination:
					for chunk in file.chunks():
						destination.write(chunk)

			return redirect(reverse('vDefAgave-jobsubmit') + '?appId=' + appId 
														   + '&archiveSystem=' + archiveSystem
														   + '&executionSystem=' + executionSystem
														   + '&geoFile=' + geoFileName
														   + '&yamlFile=' + yamlFileName)
	else:
		form = JobSetupForm(inputs=inputs, availableSystems=availableSystems)

	context = {
	'form': form,
	'appId': appId
	}
	return render(request, 'vDefAgave/jobsubmit.html', context, {'title': appId})

def jobsubmit(request):
	appId = request.GET.get('appId','')
	geoFileTemplate = request.GET.get('geoFile','')
	yamlFileTemplate = request.GET.get('yamlFile','')
	archiveSystem = request.GET.get('archiveSystem','')
	executionSystem = request.GET.get('executionSystem','')
	user = request.user

	# Get parameters from templates
	parameters = []
	with open(geoFileTemplate,'r') as templateFile:
		for line in templateFile.readlines():
			g = re.search(r'{{(\w+)}}',line)
			if g:
				parameters.append(g.group(1))
	with open(yamlFileTemplate,'r') as templateFile:
		for line in templateFile.readlines():
			g = re.search(r'{{(\w+)}}',line)
			if g:
				parameters.append(g.group(1))
	parameters = list(set(parameters))


	if request.method == 'POST':
		form = JobSubmitForm(request.POST, request.FILES, parameters=parameters)
		if form.is_valid():
			print('Form is valid')
			#Extract form data
			name = form.cleaned_data.get('name')
			email = form.cleaned_data.get('email')

			# Set other job values
			appId = appId
			batchQueue = 'CLUSTER'
			maxRunTime = '00:10:00'
			nodeCount = 1
			processorsPerNode = 1
			inputs = {
				'geoFile': '',
				'yamlFile': '',
			}
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
				'parameters': {},
				'archive': archive,
				'archiveSystem': archiveSystem,
				'notifications': notifications
			}

			# Prepare parameter space
			space = []
			for parameter in parameters:
				start = form.cleaned_data.get('sweepPara_%s_start' % parameter)
				end = form.cleaned_data.get('sweepPara_%s_end' % parameter)
				num = form.cleaned_data.get('sweepPara_%s_num' % parameter)
				space.append([int(x) for x in np.linspace(start=start, stop=end, num=num)])

			# Iterate through all parameter combination and submit a job for each
			jobFileName = 'job.txt'
			jobids = []
			failedJobs = []
			for paraCombination in list(itertools.product(*space)):
				vals = dict(zip(parameters,paraCombination))

				geoFile = '_'.join(str(p) for p in paraCombination) + '_' + geoFileTemplate
				yamlFile = '_'.join(str(p) for p in paraCombination) + '_' + yamlFileTemplate

				with open(geoFile,'w') as f:
					with open(geoFileTemplate,'r') as templateFile:
						for line in templateFile.readlines():
							g = re.search(r'{{(\w+)}}',line)
							if g:
								start = line[0:g.start()]
								end = line[g.end():]
								var = g.group(1)
								print(start,vals[var],end,sep='',end='',file=f)
							else:
								print(line,end='',file=f)

				with open(yamlFile,'w') as f:
					with open(yamlFileTemplate,'r') as templateFile:
						for line in templateFile.readlines():
							g = re.search(r'{{(\w+)}}',line)
							if g:
								start = line[0:g.start()]
								end = line[g.end():]
								var = g.group(1)
								print(start,vals[var],end,sep='',end='',file=f)
							else:
								print(line,end='',file=f)

				# Upload file to agave
				location = user.username + '/input'
				agaveRequestUploadFile(user.profile.accesstoken,geoFile,executionSystem,location)
				agaveRequestUploadFile(user.profile.accesstoken,yamlFile,executionSystem,location)

				# Delete files from server
				if os.path.exists(geoFile):
					os.remove(geoFile)
				if os.path.exists(yamlFile):
					os.remove(yamlFile)

				inputs['geoFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + geoFile
				inputs['yamlFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + yamlFile
				job['inputs'] = inputs
				print('==========JOB==========')
				print(job)
				with open(jobFileName, 'w') as outfile:  
					json.dump(job, outfile, indent=4)

				# Submit the job
				# time.sleep(10) # Pause time
				response = agaveRequestSubmitJob(user.profile.accesstoken)


				if response['status'] == 'success':
					jobids.append(response['result']['id'])
				else:
					failedJobs.append(response['message'])

				# Pause time between jobs
				# for i in reversed(range(9)):
				# 	print('Time ' + str(i*10))
				# 	time.sleep(10)	

			if len(jobids) > 0:
				messages.success(request, 'Successfully submitted %d job(s) with the ids %s.' % (len(jobids),jobids))
			if len(failedJobs) > 0:
				messages.warning(request, '%d job(s) failed with messages %s' % (len(failedJobs),failedJobs))

			if os.path.exists(jobFileName):
				os.remove(jobFileName)
			if os.path.exists(geoFileTemplate):
				os.remove(geoFileTemplate)
			if os.path.exists(yamlFileTemplate):
				os.remove(yamlFileTemplate)

			return redirect('vDefAgave-home')
	else:
		form = JobSubmitForm(parameters=parameters)

	context = {
	'form': form,
	'appId': appId
	}
	return render(request, 'vDefAgave/jobsubmit.html', context, {'title': appId})