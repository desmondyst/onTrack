
from django.contrib import admin
from django.urls import path, include
# give us access to settings.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    #send the user to url file of the base file
    path("", include('base.urls')),

    path('api/', include('base.api.urls'))
]

# set the url and get the file from MEDIA_ROOT
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# for vercel?
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
