# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include
from django.urls import path
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from django.views.decorators.csrf import ensure_csrf_cookie
import textwrap

from django.http import HttpResponse
from django.views.generic.base import View
from tritium.apps.contracts.views import GetABI
from tritium.apps.users.views import Dashboard, MyAPICredits
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from tritium.conf import api

urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mgmt/', admin.site.urls),
    path('', include(api.router.urls)),
    path('dashboard', Dashboard.as_view(), name='dashboard'),
    path('get_abi', GetABI.as_view(), name='get_abi'),
    path('accounts/', include('rest_registration.api.urls')),
    path('api_balance', MyAPICredits.as_view(), name='api_balance'),
    

]

