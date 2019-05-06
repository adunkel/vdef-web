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
def refresh(request,jobName):
	user = request.user
	jobs = user.job_set.filter(name=jobName)
	jobIds = jobs.values_list('jobid', flat=True)
	jobs.delete()
	# for jobId in jobIds:
	# 	Job(name=jobName,jobid=jobId,user=user).save()
	data = {
		'jobName': jobName
	}
	return JsonResponse(data)

@login_required
def getData(request,jobName):
	colorDefinitions = {'red': ['193','46','12'],
						'blue': ['63','11','193']}
	colors = []
	points = []
	fileEnding = '_chart.json'
	mediaPath = './src/media/'
	mediaFolder = 'job_pictures/'

	user = request.user
	jobs = user.job_set.filter(name=jobName)

	if jobs:
		# Download chart json and save to jobs model if needed
		response = ''
		paraNames = []

		# Exclude jobs that did not finish
		jobs = [job for job in jobs if job.status == 'FINISHED']

		for job in jobs:
			if not job.value:
				jobResponse = agaveRequestJobSearch(user,jobId=job.jobid)
				fileName = job.jobid + fileEnding
				imageName = job.jobid + '.png'
				path = jobResponse['result'][0]['_links']['archiveData']['href']
				fileResponse = agaveRequestGetFile(user,path,fileName)
				imageResponse = agaveRequestGetFile(user,path,imageName)
				with open(mediaPath + mediaFolder + imageName, 'wb') as f:
					f.write(imageResponse.content)

				print(fileResponse.text)
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
				job.picture = mediaFolder + imageName
				job.save()				

				time.sleep(2) # Pause time

		# Prepare data
		jobs = user.job_set.filter(name=jobName)
		# Exclude jobs that did not finish
		jobs = [job for job in jobs if job.status == 'FINISHED']

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
	pictures = [job.picture.url for job in jobs]
	
	data = {
		'points': points,
		'backgroundColor': backgroundColor,
		'borderColor': borderColor,
		'colorDefinitions': colorDefinitions,
		'axisLabels': paraNames,
		'jobIds': jobIds,
		'pictures': pictures
	}
	return JsonResponse(data)

@login_required
def getFile(request,jobId,fileName):
	user = request.user
	jobResponse = agaveRequestJobSearch(user,jobId=jobId)
	path = jobResponse['result'][0]['_links']['archiveData']['href']
	response = agaveRequestGetFile(user,path,fileName)
	return HttpResponse(response.content)

@login_required
def output(request,jobId):
	user = request.user
	response = agaveRequestJobsOutputList(user,jobId)
	files = []
	for file in response['result']:
		files.append(file['name'])
	data = {
		'files': files,
		'jobId': jobId,
	}
	# return render(request, 'jobs/joboutput.html', context)
	return JsonResponse(data)

@login_required
def listJobs(request):
	user = request.user
	jobStatus = []

	# Get list of jobs in db
	jobNames = user.job_set.values_list('name', flat=True).distinct()

	# Get metadata
	response = agaveRequestMetadataList(user)

	# Add job if not in db
	for metadata in response['result']:
		value = metadata['value']
		if 'jobName' in value:
			jobName = value['jobName']
			if jobName not in jobNames:
				for jobId in metadata['associationIds']:
					Job(name=jobName,jobid=jobId,user=user).save()

	# Get distinct job names in database by user
	jobNames = user.job_set.values_list('name', flat=True).distinct()
	for jobName in jobNames:
		response = {}
		finished = 0
		failed = 0
		jobs = Job.objects.filter(name=jobName)
		print('===')
		print(jobName)
		for job in jobs:
			# If status is not finished in db, get current status
			print(job.status)
			if job.status not in ['FINISHED','STOPPED','FAILED']:
				response = agaveRequestJobSearch(user,jobId=job.jobid)
				status = response['result'][0]['status']
				job.status = status
				job.save()
				if status in ['FINISHED','STOPPED','FAILED']:
					finished += 1
				elif status in ['STOPPED','FAILED']:
					failed += 1
				else:
					# break if one subjob is not finished
					break
		if (finished+failed) == len(jobs) and finished > 0:
			jobStatus.append('FINISHED')
		else:
			jobStatus.append(job.status)

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
	response = agaveRequestAppDetails(user,appId)
	inputs = response['result']['inputs']

	# Get system option
	response = agaveRequestSystemsList(user)
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
	fileParameters = []
	with open(geoFileTemplate,'r') as templateFile:
		for line in templateFile.readlines():
			g = re.search(r'{{(\w+)}}',line)
			if g:
				fileParameters.append(g.group(1))
	with open(yamlFileTemplate,'r') as templateFile:
		for line in templateFile.readlines():
			g = re.search(r'{{(\w+)}}',line)
			if g:
				fileParameters.append(g.group(1))
	fileParameters = list(set(fileParameters))

	# Get agave parameters
	response = agaveRequestAppDetails(user,appId)
	parametersResponse = response['result']['parameters']
	agaveParameters = []
	for p in parametersResponse:
		if p['value']['type'] == 'number':
			agaveParameters.append(p['id'])

	parameters = fileParameters + agaveParameters

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
			maxRunTime = '04:00:00'
			nodeCount = 1
			processorsPerNode = 12
			inputs = {
				'geoFile': '',
				'yamlFile': '',
			}
			archive = True
			notificationURL = 'http://melete05.cct.lsu.edu/report?status=QUEUED&eventid='+appId+'&key='+user.username
			notification = [{
				'url':notificationURL,
				'event':'QUEUED',
				'persistent':False
			}]
			agaveParameters = {key: 0 for key in agaveParameters}

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
				'parameters': agaveParameters,
				'archive': archive,
				'archiveSystem': archiveSystem,
				'notifications': notification
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
				print(paraDict)
				paraValues.append(paraDict)#######!!!!!!!!!!!!!!

				# Substitute agave parameters
				agaveParameters = {key: paraDict[key] for key in agaveParameters}
				job['parameters'] = agaveParameters

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
				agaveRequestUploadFile(user,geoFile, geoFileName, archiveSystem,location)
				time.sleep(2) # Pause time
				agaveRequestUploadFile(user,yamlFile,yamlFileName,archiveSystem,location)

				inputs['geoFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + geoFileName
				inputs['yamlFile'] = 'agave://' + executionSystem + '//home1/fdunke1/' + location + '/' + yamlFileName
				job['inputs'] = inputs

				# Submit the job
				response = {'fault': True}
				waitResponse = {appId: None}
				attempts = 1
				while (('fault' in response) or (waitResponse[appId] == None)) and attempts <= 3:
					time.sleep(5) # Pause time
					response = agaveRequestSubmitJob(user,json.dumps(job))

					if 'status' in response:
						if response['status'] == 'success':
							jobId = response['result']['id']
							
							print('===WAITING===')
							waitResponse = waitForIt(appId,user.username)
							print(waitResponse)
							if waitResponse[appId] == None:
								agaveRequestStopJob(user,jobId)
							else:
								jobIds.append(jobId)
								paraValues.append(paraDict)
								# exit while loop
						else:
							failedJobs.append(response['message'])
					attempts += 1

				time.sleep(10) # Pause time
				# Pause time between jobs
				# for i in reversed(range(10)):
				# 	print('Time ' + str(i*10))
				# 	time.sleep(10)

			if len(jobIds) > 0:
				messages.success(request, 'Successfully submitted %d job(s) with the ids %s.' % (len(jobIds),jobIds))
				templates = [geoFileTemplate,yamlFileTemplate]
				request = agaveRequestMetadataUpdate(user,jobIds,name,templates,parameters,paraValues)
				print(request)
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