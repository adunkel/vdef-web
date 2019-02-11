from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('', views.home, name='vDefAgave-home'),
	path('apps/', views.apps, name='vDefAgave-apps'),
	path('systems/', views.systems, name='vDefAgave-systems'),
	path('jobsetup/', views.jobsetup, name='vDefAgave-jobsetup'),
	path('jobsubmit/', views.jobsubmit, name='vDefAgave-jobsubmit'),
	path('joboutput/<str:jobId>/', views.joboutput, name='vDefAgave-joboutput'),
	path('jobsearch/', views.jobsearch, name='vDefAgave-jobsearch'),
	path('chart', views.chart, name='vDefAgave-chart'),
	path('api/data/', views.getData, name='vDef-getData'),
]


if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

