from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Custom error handlers — active when DEBUG=False
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'

urlpatterns = [
    path('', include('core.urls')),
    path('admin-panel/', include('adminpanel.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
