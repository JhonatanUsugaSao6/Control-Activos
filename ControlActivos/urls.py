"""
URL configuration for ControlActivos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from ControlActivos.views import login_view, validarTri, logout_view, listadoValidaciones, listadoValidacionesManuales, filtrarConsecutivo, listadoLlantas, filtrarConsecutivoLlantas
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('Tri/validarTri/', validarTri, name='validarTri'),
    path('Tri/listadoTri/', listadoValidaciones, name='listadoTri'),
    path('Tri/listadoLlantas/', listadoLlantas, name='listadoLlantas'),
    path('Tri/listadoManuales/', listadoValidacionesManuales, name='listadoManuales'),
    path('logout/', logout_view, name='logout'),
    path('ajax/filtrarConsecutivo/', filtrarConsecutivo, name='filtrarConsecutivo'),
    path('ajax/filtrarConsecutivoLlantas/', filtrarConsecutivoLlantas, name='filtrarConsecutivoLlantas'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)