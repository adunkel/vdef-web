from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	jobid = models.CharField(max_length=50)
	color = models.CharField(max_length=20, blank=True)
	value = models.IntegerField(null=True, blank=True)
	para1name = models.CharField(max_length=20, blank=True)
	para2name = models.CharField(max_length=20, blank=True)
	para1value = models.IntegerField(null=True, blank=True)
	para2value = models.IntegerField(null=True, blank=True)
	status = models.CharField(max_length=20, blank=True)

	def __str__(self):
		return '%s' % self.jobid