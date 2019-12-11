from django.urls import path, reverse

from divineog import views

app_name = 'divineog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('add/', views.AppCreate.as_view(), name='create'),
    path('<int:pk>/', views.AppDetails.as_view(), name='detail'),
    path('edit/<int:pk>/', views.AppUpdate.as_view(), name='update'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # path('<int:pk>/vote/', views.vote, name='vote'),
]
