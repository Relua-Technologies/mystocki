from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('authentication/', include('apps.authentication.urls')),
    path('', include(('apps.core.urls', 'core'), namespace='core')),
    path(
        'run-migrate/',
        lambda request: (
            call_command('migrate'),
            HttpResponse("✅ Migrations executed successfully!")
        )[1],
        name='run_migrations'
    ),
    path(
        'create-superuser/',
        lambda request: (
            User.objects.filter(username='admin').exists() or
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123'),
            HttpResponse("✅ Superuser created (admin/admin123)")
        )[1],
        name='create_superuser'
    ),
    path(
        'run-collectstatic/',
        lambda request: (
            call_command('collectstatic', '--noinput'),
            HttpResponse("✅ Collectstatic executed successfully!")
        )[1],
        name='run_collectstatic'
    ),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
