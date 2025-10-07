# survey/admin_custom.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from .views import analytics_dashboard_views
from django.contrib.auth.models import User, Group
from .models import SurveyResponse

class CustomAdminSite(admin.AdminSite):
    site_header = "FBR Survey Administration"
    site_title = "FBR Survey Admin Portal"
    index_title = "Survey Analytics Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(analytics_dashboard_views.admin_dashboard_view), name='admin_dashboard'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        # Redirect to custom dashboard instead of default admin index
        return redirect(reverse('admin:admin_dashboard'))

# Replace the default admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models with the custom admin site
custom_admin_site.register(User)
custom_admin_site.register(Group)
custom_admin_site.register(SurveyResponse)