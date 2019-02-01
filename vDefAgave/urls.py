from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='vDefAgave-home'),
	path('apps/', views.apps, name='vDefAgave-apps'),
	path('jobsubmit/<str:id>/', views.jobsubmit, name='vDefAgave-jobsubmit')
]