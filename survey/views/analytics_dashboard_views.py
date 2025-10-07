# /home/nasirk4/FBR_SEP_Taxpayer_Survey/survey/views/analytics_dashboard_views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import get_resolver
from django.db import DatabaseError
import logging
import os
import tempfile

logger = logging.getLogger(__name__)

# Import your analytics class (adjust import path as needed)
from survey.admin_dashboard import SurveyAnalytics

def debug_admin_urls_view(request):
    """Return all URL patterns for debugging"""
    resolver = get_resolver()
    all_patterns = []

    def extract_all_patterns(patterns, namespace='', path_prefix=''):
        for pattern in patterns:
            current_path = f"{path_prefix}{pattern.pattern}"

            if hasattr(pattern, 'url_patterns'):
                new_namespace = f"{namespace}:{pattern.namespace}" if pattern.namespace else namespace
                extract_all_patterns(pattern.url_patterns, new_namespace, current_path)
            else:
                pattern_info = {
                    'pattern': current_path,
                    'name': getattr(pattern, 'name', 'No name'),
                    'namespace': namespace,
                    'full_name': f"{namespace}:{pattern.name}" if pattern.name and namespace else pattern.name
                }
                all_patterns.append(pattern_info)

    extract_all_patterns(resolver.url_patterns)

    admin_patterns = [p for p in all_patterns if 'admin' in p['pattern'] or 'admin' in str(p['namespace'])]

    return JsonResponse({
        'all_urls': all_patterns,
        'admin_urls': admin_patterns
    })

def get_analytics_data(analytics):
    """Prepare analytics data for dashboard and API views.

    Args:
        analytics: SurveyAnalytics instance.

    Returns:
        dict: Analytics data including stats, quotas, and visualizations.
    """
    try:
        if not analytics.load_data():
            raise ValueError("Failed to load survey data from database")

        return {
            'summary_stats': analytics.get_summary_stats() or {},
            'quota_status': analytics.get_quota_status() or {},
            'generic_analysis': analytics.get_generic_questions_analysis() or {},
            'qualitative_insights': analytics.get_qualitative_insights() or {},
            'timeline_data': analytics.get_response_timeline() or {},
            'cross_tabs': analytics.get_cross_tabulations() or {},
            'sql_cross_tabs': analytics.get_sql_based_cross_tabs() or {},
            'advanced_analytics': analytics.get_advanced_analytics() or {},
            'visualizations': {
                'quota_chart': analytics.create_quota_chart() or '',
                **(analytics.create_cross_tab_charts() or {})
            }
        }
    except (DatabaseError, ValueError) as e:
        logger.error(f"Error preparing analytics data: {e}")
        return {}

@staff_member_required
@csrf_protect
def admin_dashboard_view(request):  # CHANGED: Added '_view'
    """Render the admin dashboard with survey analytics and visualizations.

    Args:
        request: HTTP request object.

    Returns:
        Rendered template with analytics data or error page on failure.
    """
    try:
        analytics = SurveyAnalytics()
        data = get_analytics_data(analytics)

        if not data:
            messages.error(request, "Failed to load survey data")
            return redirect('admin:index')

        context = {
            'title': 'Survey Analytics Dashboard',
            'total_responses': data['summary_stats'].get('total_responses', 0),
            **data
        }
        return render(request, 'survey/analytics_dashboard.html', context)

    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('admin:index')

@staff_member_required
def export_data(request):
    """Export survey data to Excel or SPSS format.

    Args:
        request: HTTP request object with optional 'type' parameter ('excel' or 'spss').

    Returns:
        HTTP response with the exported file or redirect on failure.
    """
    export_type = request.GET.get('type', 'excel')
    if export_type not in {'excel', 'spss'}:
        logger.warning(f"Invalid export type: {export_type}")
        messages.error(request, "Invalid export type specified")
        return redirect('admin:index')

    try:
        analytics = SurveyAnalytics()
        suffix = '.xlsx' if export_type == 'excel' else '.csv'
        content_type = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            if export_type == 'excel' else 'text/csv'
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            filename = (
                analytics.export_to_excel() if export_type == 'excel'
                else analytics.export_to_spss_format()
            )
            if not filename or not os.path.exists(filename):
                raise FileNotFoundError("Export file could not be generated")

            with open(filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
            os.remove(filename)
            return response

    except (DatabaseError, FileNotFoundError, IOError) as e:
        logger.error(f"Export error (type={export_type}): {e}")
        messages.error(request, f"Failed to export data: {str(e)}")
        return redirect('admin:index')

@staff_member_required
def api_dashboard_stats(request):
    """API endpoint for real-time dashboard analytics.

    Args:
        request: HTTP request object.

    Returns:
        JSON response with summary stats, quota status, timeline, and advanced analytics.
    """
    try:
        analytics = SurveyAnalytics()
        data = get_analytics_data(analytics)

        if not data:
            return JsonResponse({'error': 'Failed to load analytics data'}, status=500)

        return JsonResponse({
            'summary': data['summary_stats'],
            'quota_status': data['quota_status'],
            'timeline': data['timeline_data'],
            'advanced_analytics': data['advanced_analytics']
        })

    except Exception as e:
        logger.error(f"API stats error: {e}")
        return JsonResponse({'error': f'Error loading stats: {str(e)}'}, status=500)