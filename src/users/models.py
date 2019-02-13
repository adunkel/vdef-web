from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	clientkey = models.CharField(max_length=50, blank=True)
	clientsecret = models.CharField(max_length=50, blank=True)
	accesstoken = models.CharField(max_length=50, blank=True)
	refreshtoken = models.CharField(max_length=50, blank=True)
	timecreated = models.DateTimeField(default=timezone.now, null=True, blank=True)
	expiresin = models.PositiveSmallIntegerField(null=True, blank=True) # Values from 0 to 32767
	expiresat = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return '%s Profile' % self.user.username