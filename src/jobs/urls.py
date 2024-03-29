from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('jobsetup/', views.setup, name='jobs-setup'),
	path('jobsubmit/', views.submit, name='jobs-submit'),
	path('data/output/<str:jobId>/', views.outputList, name='jobs-output'),
	path('data/output/<str:jobId>/<str:fileName>/', views.getFile, name='jobs-getFile'),
	path('sets/', views.jobSets, name='jobs-job-sets'),
	path('chart/<str:jobName>/', views.chart, name='jobs-chart'),
	path('table/<str:jobName>/', views.tableView, name='jobs-table'),
	path('data/<str:jobName>/', views.getData, name='jobs-getData'),
	path('data/update/color/<str:jobId>', views.updateColor, name='jobs-updateColor'),
	path('data/refresh/job/<str:jobName>/', views.refresh, name='jobs-refresh'),
	path('dataview/', views.dataView, name='jobs-dataview'),
] 