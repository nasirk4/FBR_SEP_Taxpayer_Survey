from django.urls import path
from django.contrib import admin
from .views import (
    welcome_view, respondent_info_view, generic_questions_view, role_specific_questions_view,
    cross_system_perspectives_view, final_remarks_view, confirmation_view, save_progress_view,
    debug_admin_urls_view
)
from .views.analytics_dashboard_views import admin_dashboard_view, export_data, api_dashboard_stats 

app_name = 'survey'

urlpatterns = [
    # Public survey URLs
    path('', welcome_view, name='welcome'),
    path('respondent-info/', respondent_info_view, name='respondent_info'),
    path('generic-questions/', generic_questions_view, name='generic_questions'),
    path('role-specific-questions/', role_specific_questions_view, name='role_specific_questions'),
    path('cross-system-perspectives/', cross_system_perspectives_view, name='cross_system_perspectives'),
    path('final-remarks/', final_remarks_view, name='final_remarks'),
    path('confirmation/', confirmation_view, name='confirmation'),
    path('save-progress/', save_progress_view, name='save_progress'),
    path('debug-admin-urls/', debug_admin_urls_view, name='debug_admin_urls'),
    
    # Admin dashboard URLs
    path('admin/dashboard/', admin.site.admin_view(admin_dashboard_view), name='admin_dashboard'),
    path('admin/export/', admin.site.admin_view(export_data), name='export_survey_data'),
    path('admin/api/stats/', admin.site.admin_view(api_dashboard_stats), name='api_dashboard_stats'),
    
    # for qualitative data export
    path('admin/export/qualitative/', admin.site.admin_view(export_data), name='export_qualitative_data'),
]