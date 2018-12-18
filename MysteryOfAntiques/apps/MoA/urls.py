from django.conf.urls import url

from . import views

app_name = 'MysterOfAntiques'

urlpatterns = [
    url(r'^Home/$', views.Home, name='Home'),
    url(r'^CreateGame/$', views.CreateGame, name='CreateGame'),
    url(r'^RecoverPlayer/$', views.RecoverPlayer, name='RecoverPlayer'),
    url(r'^SetupGame/$', views.SetupGame, name='SetupGame'),
    url(r'^SetPlayerName/$', views.SetPlayerName, name='SetPlayerName'),
    url(r'^GetConnectedPlayerColors/$', views.GetConnectedPlayerColors, name='GetConnectedPlayerColors'),
    url(r'^IamAlive/$', views.IamAlive, name='IamAlive'),
    url(r'^GetAlivePlayerColors/$', views.GetAlivePlayerColors, name='GetAlivePlayerColors'),
    url(r'^GameMoA/$', views.GameMoA, name='GameMoA'),
    url(r'^EndGame/$', views.EndGame, name='EndGame'),
]