from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    # Django Admin
    path('admin/', admin.site.urls),

    # Dashboard app handles everything
    path('', include('dashboard.urls')),

]