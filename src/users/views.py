from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from datetime import timedelta 
from django.utils import timezone
from vDefAgave.agaveRequests import agaveRequestCreateClient, agaveRequestCreateToken, agaveRequestRefreshToken


@login_required
def profile(request):
	return render(request, 'users/profile.html')

class CustomLoginView(LoginView):
	def post(self, request, *args, **kwargs):
		username = request.POST['username']
		password = request.POST['password']
		form = self.get_form()
		print(form)
		user = User.objects.filter(username=username).first()
		if user is None:
			print('User %s does not exists.' % username)
			user = createuser(username,password)
		if user is not None and not form.is_valid():
			print('Logging in user manually')
			login(self.request, user)
			return HttpResponseRedirect(self.get_success_url())
		print('Using super.post')
		if form.is_valid():
			print('Refreshing the token')
			agaveRequestRefreshToken(user)
		return super().post(self, request, *args, **kwargs)

def createuser(username,password):
	user = User.objects.create_user(username=username, password=password)

	clientResponse = agaveRequestCreateClient(username, password)
	print(clientResponse)
	if clientResponse['status'] == 'success':
		user.profile.clientkey = clientResponse['result']['consumerKey']
		user.profile.clientsecret = clientResponse['result']['consumerSecret']

		tokenResponse = agaveRequestCreateToken(username, password, user)
		print(tokenResponse)
		if not 'error' in tokenResponse:
			user.profile.accesstoken = tokenResponse['access_token']
			user.profile.refreshtoken = tokenResponse['refresh_token']
			expiresIn = tokenResponse['expires_in']
			currentTime = timezone.now()
			user.profile.expiresin = expiresIn
			user.profile.timecreated = currentTime
			user.profile.expiresat = currentTime + timedelta(seconds=expiresIn)
			user.save()
			return user
	user.delete()
	return None