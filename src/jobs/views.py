from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django import forms
from vDefAgave.agaveRequests import *
from .forms import JobSubmitForm, JobSearchForm, JobSetupForm
from .models import Job
import json, requests, os, re, time, itertools
import numpy as np

@login_required
def dataView(request):
	index = request.GET.get('index','')
	x = request.GET.get('x','')
	y = request.GET.get('y','')
	r = request.GET.get('r','')
	context = {
		'index': index,
		'x': x,
		'y': y,
		'r': r,
		'title': 'ViewData'
	}
	return render(request, 'jobs/viewdata.html', context)

@login_required
def chart(request,jobName):
	context = {
		'jobName': jobName
	}
	return render(request, 'jobs/chart.html', context)

@login_required
def updateColor(request,jobId):
	color = request.GET.get('color','')
	user = request.user
	job = user.job_set.filter(jobid=jobId).first()
	job.color = color
	job.save()
	data = {
		'job id': job.jobid
	}
	return JsonResponse(data)

@login_required
def getData(request,jobName):
	colorDefinitions = {'red': ['193','46','12'],
						'blue': ['63','11','193']}
	colors = []
	points = []
	fileEnding = '_chart.json'

	user = request.user
	jobs = user.job_set.filter(name=jobName)

	if jobs:
		# Download chart json and save to jobs model if needed
		response = ''
		paraNames = []
		for job in jobs:
			if not job.value:
				jobResponse = agaveRequestJobSearch(user.profile.accesstoken,jobId=job.jobid)
				fileName = job.jobid + fileEnding
				path = jobResponse['result'][0]['_links']['archiveData']['href']
				fileResponse = agaveRequestGetFile(user.profile.accesstoken,path,fileName)
				print(fileResponse.content)
				pointData = json.loads(fileResponse.text)
				# Determine parameter names and order
				if not paraNames:
					paraNames = [*pointData['parameter']]
				job.value = pointData['value']
				job.color = pointData['color']
				job.para1name = paraNames[0]
				job.para2name = paraNames[1]
				job.para1value = pointData['parameter'][paraNames[0]]
				job.para2value = pointData['parameter'][paraNames[1]]
				job.save()				

				time.sleep(5) # Pause time

		# Prepare data
		jobs = user.job_set.filter(name=jobName)
		for job in jobs:
			if not paraNames:
				paraNames = [job.para1name,job.para2name]
			colors.append(job.color)
			points.append({'x':job.para1value,'y':job.para2value, 'r':job.value})
					
	# Convert colors to rgb
	colors = [('rgb(' + ','.join(colorDefinitions[color]) + ')') for color in colors]

	borderColor = colors

	# Set alpha value for background
	colors = [re.sub('rgb','rgba',color) for color in colors]
	backgroundColor = [re.sub(r'\)',',0.3)',color) for color in colors]

	jobIds = [job.jobid for job in jobs]
	
	data = {
		'points': points,
		'backgroundColor': backgroundColor,
		'borderColor': borderColor,
		'colorDefinitions': colorDefinitions,
		'axisLabels': paraNames,
		'jobIds': jobIds
	}
	return JsonResponse(data)

@login_required
def output(request,jobId):
	user = request.user
	response = agaveRequestJobsOutputList(user.profile.accesstoken,jobId)
	print(response)
	context = {
		'jobId': jobId,
		'output': response['result'],
		'title': 'Job Output'
	}
	return render(request, 'jobs/joboutput.html', context)

@login_required
def listJobs(request):
	user = request.user
	jobStatus = []

	# Get distinct job names in database by user
	jobNames = user.job_set.values_list('name').distinct()
	jobNames = [i for sub in jobNames for i in sub]
	for jobName in jobNames:
		response = {}
		finished = True
		jobs = Job.objects.filter(name=jobName)
		for job in jobs:
			# If status is not finished in db, get current status
			if job.status != 'FINISHED':
				response = agaveRequestJobSearch(user.profile.accesstoken,jobId=job.jobid)
				status = response['result'][0]['status']
				job.status = status
				job.save()
				if status != 'FINISHED':
					# break if one subjob is not finished
					finished = False
					break
		if finished:
			jobStatus.append('FINISHED')
		else:
			jobStatus.append(status)

	# Create jobname:status dictionary
	jobs = dict(zip(jobNames,jobStatus))
	
	context = {
	'jobs': jobs,
	'title': 'Job List'
	}
	return render(request, 'jobs/joblist.html', context)

@login_required
def setup(request):
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

			return redirect(reverse('jobs-submit') + '?appId=' + appId 
												   + '&archiveSystem=' + archiveSystem
												   + '&executionSystem=' + executionSystem
												   + '&geoFile=' + geoFileName
												   + '&yamlFile=' + yamlFileName)
	else:
		form = JobSetupForm(inputs=inputs, availableSystems=availableSystems)

	context = {
		'form': form,
		'appId': appId,
		'title': 'Submit Job'
	}
	return render(request, 'jobs/jobsubmit.html', context)

@login_required
def submit(request):
	appId = request.GET.get('appId','')
	geoFileTemplate = request.GET.get('geoFile','')
	yamlFileTemplate = request.GET.get('yamlFile','')
	archiveSystem = request.GET.get('archiveSystem','')
	executionSystem = request.GET.get('executionSystem','')
	user = request.user
	token = user.profile.accesstoken

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
			jobIds = []
			failedJobs = []
			paraValues = []
			for paraCombination in list(itertools.product(*space)):
				paraDict = dict(zip(parameters,paraCombination))

				# Create name for geo and yaml file
				templateSplit = geoFileTemplate.rsplit('.',1)
				geoFileName = templateSplit[0] + '_' + '_'.join(str(key) + '-' + str(value) for key,value in paraDict.items()) + '.' + templateSplit[1]
				templateSplit = yamlFileTemplate.rsplit('.',1)
				yamlFileName = templateSplit[0] + '_' + '_'.join(str(key) + '-' + str(value) for key,value in paraDict.items()) + '.' + templateSplit[1]

				# Substitute value into geo template 
				geoFile = '//' + str(paraDict) + '\n'
				with open(geoFileTemplate,'r') as templateFile:
					for line in templateFile.readlines():
						g = re.search(r'{{(\w+)}}',line)
						if g:
							start = line[0:g.start()]
							end = line[g.end():]
							var = g.group(1)
							geoFile += (start + str(paraDict[var]) + end)
						else:
							geoFile += line

				# Substitute value into yaml template 
				yamlFile = ''
				with open(yamlFileTemplate,'r') as templateFile:
					for line in templateFile.readlines():
						g = re.search(r'{{(\w+)}}',line)
						if g:
							start = line[0:g.start()]
							end = line[g.end():]
							var = g.group(1)
							yamlFile += (start + str(paraDict[var]) + end)
						else:
							yamlFile += line

				# Upload file to agave
				location = user.username + '/input'
				agaveRequestUploadFile(token,geoFile, geoFileName, archiveSystem,location)
				agaveRequestUploadFile(token,yamlFile,yamlFileName,archiveSystem,location)

				inputs['geoFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + geoFileName
				inputs['yamlFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + yamlFileName
				job['inputs'] = inputs

				# Submit the job
				time.sleep(10) # Pause time
				response = agaveRequestSubmitJob(token,json.dumps(job))

				if response['status'] == 'success':
					jobId = response['result']['id']
					jobIds.append(jobId)
					paraValues.append(paraDict)
					# Create entry for job
					# Job(name=name,jobid=response['result']['id'],user=user).save()
				else:
					failedJobs.append(response['message'])

				# Pause time between jobs
				for i in reversed(range(9)):
					print('Time ' + str(i*10))
					time.sleep(10)	

			if len(jobIds) > 0:
				messages.success(request, 'Successfully submitted %d job(s) with the ids %s.' % (len(jobIds),jobIds))
				templates = [geoFileTemplate,yamlFileTemplate]
				request = agaveRequestMetadataUpdate(token,jobIds,name,templates,parameters,paraValues)
			if len(failedJobs) > 0:
				messages.warning(request, '%d job(s) failed with messages %s' % (len(failedJobs),failedJobs))

			# Remove template files
			if os.path.exists(geoFileTemplate):
				os.remove(geoFileTemplate)
			if os.path.exists(yamlFileTemplate):
				os.remove(yamlFileTemplate)

			return redirect('vDefAgave-home')
	else:
		form = JobSubmitForm(parameters=parameters)

	context = {
	'form': form,
	'appId': appId,
	'title': 'Submit Job'
	}
	return render(request, 'jobs/jobsubmit.html', context)