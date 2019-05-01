from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('jobsetup/', views.setup, name='jobs-setup'),
	path('jobsubmit/', views.submit, name='jobs-submit'),
	path('data/output/<str:jobId>/', views.output, name='jobs-output'),
	path('joblist/', views.listJobs, name='jobs-list'),
	path('chart/<str:jobName>/', views.chart, name='jobs-chart'),
	path('data/<str:jobName>/', views.getData, name='jobs-getData'),
	path('data/update/color/<str:jobId>', views.updateColor, name='jobs-updateColor'),
	path('data/refresh/job/<str:jobName>/', views.refresh, name='jobs-refresh'),
	path('dataview/', views.dataView, name='jobs-dataview'),
]