from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='vDefAgave-home'),
	path('apps/', views.apps, name='vDefAgave-apps'),
	path('systems/', views.systems, name='vDefAgave-systems'),
	path('jobsubmit/<str:appId>/', views.jobsubmit, name='vDefAgave-jobsubmit'),
	path('joboutput/<str:jobId>/', views.joboutput, name='vDefAgave-joboutput'),
	path('jobsearch/', views.jobsearch, name='vDefAgave-jobsearch'),
	path('chart', views.chart, name='vDefAgave-chart'),
	path('api/data/', views.getData, name='vDef-getData'),
]