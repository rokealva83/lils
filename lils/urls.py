from django.conf.urls import include, url
from django.contrib import admin

import debug_toolbar

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include('core.urls')),
    url(r'^', include('products.urls')),
    url(r'^__debug__/', include(debug_toolbar.urls)),
]
