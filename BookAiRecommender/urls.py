from django.contrib import admin
from django.urls import path, include  # Make sure to import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('BookAI.urls')),  # Add this line for the root URL
]
