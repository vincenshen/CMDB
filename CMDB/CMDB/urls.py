"""CMDB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from Asset import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^report/asset_with_no_asset_id/$', views.asset_with_no_asset_id),
    url(r'^report/$', views.asset_report),
    url(r'^index/$', views.Index.as_view(), name="index"),
    url(r'^asset_list/$', views.AssetList.as_view(), name="asset_list"),
    url(r'^asset_detail/(?P<asset_id>\d+)/$', views.AssetDetail.as_view(), name="asset_detail")
]
