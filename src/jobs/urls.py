from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('jobsetup/', views.setup, name='jobs-setup'),
	path('jobsubmit/', views.submit, name='jobs-submit'),
	path('joboutput/<str:jobId>/', views.output, name='jobs-output'),
	path('jobsearch/', views.search, name='jobs-search'),
	path('chart/<str:jobName>/', views.chart, name='jobs-chart'),
	path('api/data/<str:jobName>/', views.getData, name='jobs-getData'),
	path('dataview/', views.dataView, name='jobs-dataview'),
]