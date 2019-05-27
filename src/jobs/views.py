from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.files import File
from django.conf import settings
from django import forms
from vDefAgave.agaveRequests import *
from .forms import JobSubmitForm, JobSearchForm, JobSetupForm
from .models import Job
import json, requests, os, re, time, itertools, mimetypes, random
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
def tableView(request,jobName):
	user = request.user
	updateJobDB(request,Q={"value.jobName":jobName})
	jobsAsDict = []
	jobs = user.job_set.filter(name=jobName)
	if jobs:
		for job in jobs:
			jobsAsDict.append(job.__dict__)
			getPicture(request,job.jobid)

	# user.job_set.values_list('jobid', flat=True).distinct()
	context = {
		'jobName': jobName,
		'jobs': jobsAsDict
	}
	return render(request, 'jobs/table.html', context)

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
						'blue': ['63','11','193'],
						'orange': ['255','140','0']}
	colors = []
	points = []
	paraNames = []

	user = request.user
	updateJobDB(request,Q={"value.jobName":jobName})
	jobs = user.job_set.filter(name=jobName)
	if jobs:
		for job in jobs:
			getPicture(request,job.jobid)
	jobs = user.job_set.filter(name=jobName)

	if jobs:
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
	fileResponse = agaveRequestGetFile(user,path,fileName)

	content_type = fileResponse.headers['Content-Type']
	extension = os.path.splitext(fileName)[1]
	if extension not in ['png','txt']:
		content_type = 'text/plain'
	content_disposition = fileResponse.headers['Content-Disposition']
	response = HttpResponse(fileResponse.content, content_type=content_type)
	response['Content-Disposition'] = content_disposition
	# response['Content-Disposition'] = 'attachment; filename=%s' %fileName
	return response

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
def getPicture(request,jobId):
	mediaPath = './src/media/'
	mediaFolder = 'job_pictures/'
	user = request.user
	job = user.job_set.filter(jobid=jobId).first()
	if job.picture == 'job_pictures/default.jpg':
		jobResponse = agaveRequestJobSearch(user,jobId=job.jobid)
		imageName = job.jobid + '.png'
		path = jobResponse['result'][0]['_links']['archiveData']['href']
		imageResponse = agaveRequestGetFile(user,path,imageName)
		with open(mediaPath + mediaFolder + imageName, 'wb') as f:
			f.write(imageResponse.content)
		job.picture = mediaFolder + imageName
		job.save()

@login_required
def updateJobDB(request,Q={}):
	"""Update the job database with metadata items
	An option query Q can be given. Ex.: Q={"value.jobName": "myJobName"}
	"""
	user = request.user
	# Get metadata
	response = agaveRequestMetadataList(user,Q=Q)
	# Add job if not in db
	for metadata in response['result']:
		value = metadata['value']
		if 'jobName' in value and 'parameters' in value:
			jobName = value['jobName']
			para1name = value['parameters'][0]
			para2name = value['parameters'][1]
			jobsInDB = Job.objects.filter(name=jobName)

			# Update status if not 'FINISHED'
			for job in jobsInDB:
				if job.status not in ['FINISHED']:
					jobResponse = agaveRequestJobSearch(user,jobId=job.jobid)
					status = jobResponse['result'][0]['status']
					color = 'red'
					if status == 'FINISHED':
						color = 'blue'
					elif status not in ['FINISHED','FAILED','STOPPED']: # Running
						color = 'orange'
					# else failed or stopped (color = 'red')
					job.status = status
					job.color = color
					job.save()

			# Create new job entries
			jobsInDB = [job.jobid for job in Job.objects.filter(name=jobName)]
			jobsNotInDB = (set(jobsInDB) ^ set(metadata['associationIds'])) & set(metadata['associationIds'])
			for jobId in jobsNotInDB:
				myConsole(user, 'Creating job entry for ' + jobId)
				jobResponse = agaveRequestJobSearch(user,jobId=jobId)
				status = jobResponse['result'][0]['status']
				color = 'red'
				if status == 'FINISHED':
					color = 'blue'
				elif status == 'RUNNING':
					color = 'orange'
				para1value = value['paraValues'][jobId][para1name]
				para2value = value['paraValues'][jobId][para2name]
				Job(name=jobName,
					jobid=jobId,
					user=user,
					value=8,
					para1name=para1name,
					para1value=para1value,
					para2name=para2name,
					para2value=para2value,
					status=status,
					color=color).save()

@login_required
def jobSets(request):
	user = request.user
	jobStatus = []

	# Get list of jobs in db
	jobNames = user.job_set.values_list('name', flat=True).distinct()
	updateJobDB(request)

	# Get distinct job names in database by user
	jobNames = user.job_set.values_list('name', flat=True).distinct()
	for jobName in jobNames:
		response = {}
		finished = 0
		failed = 0
		running = 0
		jobs = Job.objects.filter(name=jobName)
		for job in jobs:
			if job.status in ['FINISHED']:
				finished += 1
			elif job.status in ['STOPPED','FAILED']:
				failed += 1
			else:
				running += 1
		jobStatus.append({'FINISHED': finished,
						  'RUNNING': running,
					 	  'FAILED': failed})

	# Create jobname:status dictionary
	jobs = dict(zip(jobNames,jobStatus))
	
	context = {
	'jobs': jobs,
	'title': 'Job-Sets'
	}
	return render(request, 'jobs/sets.html', context)

@login_required
def setup(request):
	appId = request.GET.get('appId','')
	user = request.user

	# Get system option
	response = agaveRequestSystemsList(user)
	availableSystems = response['result']
	# print(availableSystems)
	# for s in availableSystems:
	# 	print(s)

	# Get application parameter details
	response = agaveRequestAppDetails(user,appId)
	inputs = response['result']['inputs']

	geoFileName = ''
	yamlFileName = ''
	name = ''
	samplingChoice = ''

	if request.method == 'POST':
		form = JobSetupForm(request.POST, request.FILES, inputs=inputs, availableSystems=availableSystems)
		if form.is_valid():
			name = form.cleaned_data.get('name')
			samplingChoice = form.cleaned_data.get('samplingChoice')
			executionSystem = form.cleaned_data.get('executionSystem')
			archiveSystem = form.cleaned_data.get('storageSystem')

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

			response = agaveRequestMetadataList(user,Q={'value.jobName':name})
			if response['result']: # Job with this name already exists
				messages.warning(request, 'A job with the name %s already exists. If you continue, the results will be merged.' % name)

			return redirect(reverse('jobs-submit') + '?appId=' + appId 
												   + '&name=' + name
												   + '&geoFile=' + geoFileName
												   + '&yamlFile=' + yamlFileName
												   + '&samplingChoice=' + samplingChoice
												   + '&executionSystem=' + executionSystem
												   + '&archiveSystem=' + archiveSystem)
	else:
		form = JobSetupForm(inputs=inputs, availableSystems=availableSystems)

	context = {
		'form': form,
		'appId': appId,
		'name': name,
		'geoFileName': geoFileName,
		'yamlFileName': yamlFileName,
		'samplingChoice': samplingChoice,
		'title': 'Submit Job'
	}
	return render(request, 'jobs/jobsubmit.html', context)

@login_required
def submit(request):
	appId = request.GET.get('appId','')
	name = request.GET.get('name','')
	geoFileTemplate = request.GET.get('geoFile','')
	yamlFileTemplate = request.GET.get('yamlFile','')
	samplingChoice = request.GET.get('samplingChoice')
	archiveSystem = request.GET.get('archiveSystem')
	executionSystem = request.GET.get('executionSystem')

	user = request.user
	token = user.profile.accesstoken

	queueChoices = []
	systemResponse = agaveRequestSystemsList(user,executionSystem)
	for queue in systemResponse['result']['queues']:
		queueChoices.append(queue['name'])

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
		form = JobSubmitForm(request.POST, request.FILES, parameters=parameters, samplingChoice=samplingChoice, queueChoices=queueChoices)
		if form.is_valid():
			#Extract form data
			email = form.cleaned_data.get('email')
			executionSystem = form.cleaned_data.get('executionSystem')
			archiveSystem = form.cleaned_data.get('storageSystem')
			nodeCount = form.cleaned_data.get('nodeCount')
			processorsPerNode = form.cleaned_data.get('processorsPerNode')
			maxRunTime = form.cleaned_data.get('maxRunTime')
			queue = form.cleaned_data.get('queue')

			# Set other job values
			appId = appId
			inputs = {
				'geoFile': '',
				'yamlFile': '',
			}
			archive = True
			notificationURL = 'http://melete05.cct.lsu.edu/report?status=QUEUED&eventid='+appId+'&key='+user.username
			notification = [{
				'url':notificationURL,
				'event':'QUEUED',
				# 'event':'FINISHED',
				'persistent':False
			}]
			agaveParameters = {key: 0 for key in agaveParameters}

			# Put everything into a dictionary
			job = {
				'name':name,
				'appId': appId,
				'executionSystem': executionSystem,
				'batchQueue': queue,
				'maxRunTime': maxRunTime,
				'nodeCount': nodeCount,
				'processorsPerNode': processorsPerNode,
				'inputs': inputs,
				'parameters': agaveParameters,
				'archive': archive,
				'archiveSystem': archiveSystem,
				# 'notifications': notification
			}

			# Prepare parameter space
			space = []

			if samplingChoice == 'grid':
				for parameter in parameters:
					start = form.cleaned_data.get('sweepPara_%s_start' % parameter)
					end = form.cleaned_data.get('sweepPara_%s_end' % parameter)
					num = form.cleaned_data.get('sweepPara_%s_num' % parameter)
					space.append([x for x in np.linspace(start=start, stop=end, num=num)])
				space = list(itertools.product(*space))
			elif samplingChoice == 'random':
				start = []
				end = []
				num = form.cleaned_data.get('number')
				for parameter in parameters:
					start = form.cleaned_data.get('sweepPara_%s_start' % parameter)
					end = form.cleaned_data.get('sweepPara_%s_end' % parameter)
					space.append([random.uniform(start,end) for i in range(num)])
				space = list(zip(*space))
			else: # latin square
				1/0
			# Iterate through all parameter combination and submit a job for each
			jobIds = []
			failedJobs = []
			paraValues = []
			for paraCombination in space:
				paraDict = dict(zip(parameters,paraCombination))

				# Substitute agave parameters
				agaveParameters = {key: paraDict[key] for key in agaveParameters}
				job['parameters'] = agaveParameters

				# Create name for geo and yaml file
				templateSplit = geoFileTemplate.rsplit('.',1)
				geoFileName = templateSplit[0] + '_' + '_'.join(str(key) + '-' + str(value) for key,value in paraDict.items()) + '.' + templateSplit[1]
				templateSplit = yamlFileTemplate.rsplit('.',1)
				yamlFileName = templateSplit[0] + '_' + '_'.join(str(key) + '-' + str(value) for key,value in paraDict.items()) + '.' + templateSplit[1]

				# Substitute value into geo template 
				geoFile = '' #'//' + str(paraDict) + '\n'
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
				# time.sleep(2) # Pause time
				agaveRequestUploadFile(user,yamlFile,yamlFileName,archiveSystem,location)

				inputs['geoFile'] = 'agave://' + executionSystem + '/' + location + '/' + geoFileName
				inputs['yamlFile'] = 'agave://' + executionSystem + '/' + location + '/' + yamlFileName
				job['inputs'] = inputs

				# Submit the job
				response = {'fault': True}
				# waitResponse = {appId: None}
				waitResponse = {appId: 'something'}
				attempts = 1
				while (('fault' in response) or (waitResponse[appId] == None)) and attempts <= 3:
					# time.sleep(5) # Pause time
					response = agaveRequestSubmitJob(user,json.dumps(job))

					if 'status' in response:
						if response['status'] == 'success':
							jobId = response['result']['id']
							myConsole(user, 'Job ' + jobId + ' submitted to Agave successfully')
							
							# myConsole(user, 'Waiting on job ' + jobId + ' to queue.')
							# waitResponse = waitForIt(appId,user.username)
							# myConsole(user, waitResponse)
							if waitResponse[appId] == None:
								agaveRequestStopJob(user,jobId)
							else:
								jobIds.append(jobId)
								paraValues.append(paraDict)
								# exit while loop
						else:
							failedJobs.append(response['message'])
					attempts += 1

				# time.sleep(10) # Pause time

			if len(jobIds) > 0:
				messages.success(request, 'Successfully submitted %d job(s) with the ids %s.' % (len(jobIds),jobIds))
				templates = [geoFileTemplate,yamlFileTemplate]
				request = agaveRequestMetadataUpdate(user,jobIds,name,templates,parameters,paraValues)
			if len(failedJobs) > 0:
				messages.warning(request, '%d job(s) failed with messages %s' % (len(failedJobs),failedJobs))

			# Remove template files
			if os.path.exists(geoFileTemplate):
				os.remove(geoFileTemplate)
			if os.path.exists(yamlFileTemplate):
				os.remove(yamlFileTemplate)

			return redirect('jobs-job-sets')
	else:
		form = JobSubmitForm(parameters=parameters, samplingChoice=samplingChoice, queueChoices=queueChoices)

	context = {
	'form': form,
	'appId': appId,
	'name': name,
	'geoFileName': geoFileTemplate,
	'yamlFileName': yamlFileTemplate,
	'samplingChoice': samplingChoice,
	'archiveSystem': archiveSystem,
	'executionSystem': executionSystem,
	'title': 'Submit Job'
	}
	return render(request, 'jobs/jobsubmit.html', context)