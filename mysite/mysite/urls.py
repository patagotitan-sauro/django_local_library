"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


import os
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
#from django.views.generic import RedirectView # novo

# Up two folders to serve "site" content
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.join(BASE_DIR, 'site')


urlpatterns = [
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    re_path(r'^site/(?P<path>.*)$', serve,
        {'document_root': SITE_ROOT, 'show_indexes': True},
        name='site_path'
        ),
]

#path("", RedirectView.as_view(url="/polls/")),   # <--- root redirect
'''
urlpatterns = [
    path("admin/", admin.site.urls),
    # incluir as urlpattern dos apps criados
    path("polls/", include("polls.urls")),
    path("catalog/", include("catalog.urls")),
]
'''