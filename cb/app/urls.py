from django.conf.urls import url
from . import views
from app.views import list
from app.views import home
from django.conf import settings
from django.contrib.auth.views import logout



urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^search/', views.search),
    url(r'^selections/', views.selections),
    url(r'^index/', home, name = 'home'),
    url(r'^sys_block/', views.blocking, name = 'blocking'),
    url(r'^error_blocking/', views.error_blocking, name = 'is_blocked'),
    url(r'^auth/', views.auth_it, name = 'auth'),
    url(r'^check_rights/', views.get_group, name = 'get_group'),
    url(r'^db_update/$', list, name='list'),
    url(r'^edit/kartochka_kompanii/(?P<id>\w+)/$', views.edit_kartochka, name='edit/kartochka_kompanii'),
    url(r'^edit/korp_kontrol/(?P<id>\w+)/$', views.edit_korp_kontrol, name='edit/korp_kontrol'),
]
