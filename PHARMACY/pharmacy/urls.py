from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from admin_tools_stats import urls as admin_tools_stats_urls




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('admin_tools_stats/', include('admin_tools_stats.urls')),

]

handler404 = 'app.views.error_404'

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)