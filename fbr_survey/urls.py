# /home/nasirk4/FBR_SEP_Taxpayer_Survey/fbr_survey/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import the custom admin site
from survey.admin_custom import custom_admin_site   

urlpatterns = [
    path('', include('survey.urls', namespace='survey')),
    path('admin/', custom_admin_site.urls),
    path('legacy-admin/', admin.site.urls),

]
