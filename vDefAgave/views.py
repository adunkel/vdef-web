from django.shortcuts import render
import requests
from django.http import HttpResponse

posts = [
	{
		'author': 'Alex',
		'title': 'Post 1',
		'content': 'First post content',
		'date_posted': 'Jan 20, 2018'
	},
	{
		'author': 'Kaison',
		'title': 'Post 2',
		'content': 'Second post content',
		'date_posted': 'Jan 21, 2018'
	}
]

def home(request):
	context = {
		'posts': posts
	}
	return render(request, 'vDefAgave/home.html', context)

def apps(request):
	user = request.user
	response = agaveRequestAppsList(user.profile.accesstoken)
	# print(response)
	return render(request, 'vDefAgave/apps.html', response, {'title': 'Apps'})

def jobsubmit(request,id):
	user = request.user
	response = agaveRequestAppDetails(user.profile.accesstoken,id)
	return render(request, 'vDefAgave/jobsubmit.html', response, {'title': id})

def agaveRequestAppDetails(token,appid):
	headers = {
	    'Authorization': 'Bearer ' + token,
	}

	params = (
	    ('pretty', 'true'),
	)

	response = requests.get('https://public.agaveapi.co/apps/v2/' + appid, 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()

def agaveRequestAppsList(token):
	headers = {
		'Authorization': 'Bearer ' + token,
	}

	params = (
		('pretty', 'true'),
	)

	response = requests.get('https://public.agaveapi.co/apps/v2', 
							headers=headers, 
							params=params, 
							verify=False)
	return response.json()