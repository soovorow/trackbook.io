from django.urls import path, reverse

from trackbook import views

app_name = 'trackbook'
urlpatterns = [
    path('', views.AppList.as_view(), name='index'),
    path('add/', views.AppCreate.as_view(), name='create'),
    path('<int:pk>/', views.AppDetails.as_view(), name='detail'),
    path('edit/<int:pk>/', views.AppUpdate.as_view(), name='update'),
    path('log', views.LogEvent.as_view(), name='log'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:pk>/vote/', views.vote, name='vote'),
]
