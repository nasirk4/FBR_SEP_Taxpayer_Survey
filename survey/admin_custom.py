from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.utils.html import format_html
from django.utils import timezone
from .models import SurveyResponse

class CustomAdminSite(admin.AdminSite):
    site_header = "FBR Taxpayer Survey Administration"
    site_title = "FBR Survey Admin Portal" 
    index_title = "Welcome to Survey Analytics Dashboard"
    enable_nav_sidebar = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # Redirect to your existing survey URLs
            path('dashboard/', self.admin_view(lambda request: redirect(reverse('survey:admin_dashboard'))), 
                 name='admin_dashboard_redirect'),
            path('analytics/', self.admin_view(lambda request: redirect(reverse('survey:admin_dashboard'))), 
                 name='analytics_dashboard_redirect'),
        ]
        return custom_urls + urls

    def index(self, request, extra_context=None):
        """Enhanced index page with dashboard integration."""
        extra_context = extra_context or {}
        
        # Basic statistics for all staff users
        total_responses = SurveyResponse.objects.count()
        recent_responses = SurveyResponse.objects.filter(
            submission_date__gte=timezone.now() - timezone.timedelta(days=7)
        ).count()
        
        # Completion metrics
        from .admin_dashboard import SurveyAnalytics
        analytics = SurveyAnalytics()
        quota_status = {}
        if analytics.load_data():
            quota_status = analytics.get_quota_status()
        
        extra_context.update({
            'total_responses': total_responses,
            'recent_responses': recent_responses,
            'quota_status': quota_status,
            'show_dashboard_redirect': request.user.has_perm('survey.view_analytics'),
            'dashboard_url': reverse('survey:admin_dashboard'),  # Use your existing URL
        })
        
        return super().index(request, extra_context)

    def each_context(self, request):
        """Add custom context to all admin pages."""
        context = super().each_context(request)
        
        # Add dashboard link to global context using your existing URL
        context['dashboard_url'] = reverse('survey:admin_dashboard')
        context['has_analytics_permission'] = request.user.has_perm('survey.view_analytics')
        
        return context

    def get_app_list(self, request):
        """Customize the app list in admin."""
        app_list = super().get_app_list(request)
        
        # Add custom dashboard to app list using your existing URL
        if request.user.has_perm('survey.view_analytics'):
            dashboard_app = {
                'name': '📊 Survey Analytics',
                'app_label': 'survey_analytics',
                'app_url': reverse('survey:admin_dashboard'),  # Use your existing URL
                'has_module_perms': True,
                'models': [{
                    'name': 'Analytics Dashboard',
                    'object_name': 'dashboard',
                    'admin_url': reverse('survey:admin_dashboard'),  # Use your existing URL
                    'view_only': True,
                }]
            }
            app_list.insert(0, dashboard_app)
            
        return app_list

# Instantiate custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register models (keep existing UserAdmin and GroupAdmin)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    search_fields = ['username', 'email', 'first_name', 'last_name']

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count']
    search_fields = ['name']
    
    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Users'

custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)