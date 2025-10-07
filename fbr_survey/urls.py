# /home/nasirk4/FBR_SEP_Taxpayer_Survey/fbr_survey/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('survey.urls', namespace='survey')),
    path('admin/', admin.site.urls),


]