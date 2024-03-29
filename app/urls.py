"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import include, path
from app import views, settings
from trackbook.views import HomeView, SignUpView, LogDebug
# from django.conf.urls import url
# from django.contrib import admin


urlpatterns = [
    # url(r'^admin/', admin.site.urls),

    path('', HomeView.as_view(), name='home'),
    path('auth/signup', SignUpView.as_view(), name='signup'),
    path('auth/', include('django.contrib.auth.urls')),
    path('analytics/', include('trackbook.urls')),
    path('debug/log', LogDebug.as_view(), name='debug_log'),
    #  TODO add url patter for marketing url
    #  TODO add url patter for ads txt
    #  TODO add url patter for privacy policy
    #  TODO add url patter for terms of use
    #  TODO add url patter for support url

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
