from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='vDefAgave-home'),
	path('apps/', views.apps, name='vDefAgave-apps'),
	path('systems/', views.systems, name='vDefAgave-systems'),
	path('apps/pems/<str:appId>/', views.appPemsList, name='vDefAgave-appPems'),
	path('apps/pems/<str:appId>/<str:updateUser>/', views.appPemsUpdate, name='vDefAgave-appPemsUpdate'),
	path('systems/roles/<str:systemId>/', views.systemRolesList, name='vDefAgave-systemRolesList'),
	path('systems/roles/<str:systemId>/<str:updateUser>/<str:role>/', views.systemRoleUpdate, name='vDefAgave-systemRoleUpdate'),
]