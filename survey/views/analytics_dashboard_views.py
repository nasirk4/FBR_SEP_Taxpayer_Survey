import csv
import json
import logging
import os
import tempfile

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import get_resolver
from django.db import DatabaseError
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder

# Third-party libraries (assuming pandas and numpy are used by SurveyAnalytics)
import pandas as pd
import numpy as np


# Local application imports
from survey.admin_dashboard import SurveyAnalytics


logger = logging.getLogger(__name__)

# --- Custom Decorator ---

def staff_member_required_api(view_func):
    """Custom decorator that returns JSON errors for API endpoints."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not request.user.is_staff:
            return JsonResponse({'error': 'Staff membership required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


# --- Utility Functions ---

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
                all_patterns.append({
                    'pattern': current_path,
                    'name': getattr(pattern, 'name', 'No name'),
                    'namespace': namespace,
                    'full_name': f"{namespace}:{pattern.name}" if pattern.name and namespace else pattern.name
                })

    extract_all_patterns(resolver.url_patterns)
    admin_patterns = [p for p in all_patterns if 'admin' in p['pattern'] or 'admin' in str(p['namespace'])]

    return JsonResponse({'all_urls': all_patterns, 'admin_urls': admin_patterns})


def get_analytics_data(analytics):
    """Prepare analytics data for dashboard and API views."""
    try:
        if not analytics.load_data():
            raise ValueError("Failed to load survey data from database")

        data = {
            'summary_stats': analytics.get_summary_stats() or {},
            'quota_status': analytics.get_quota_status() or {},
            'generic_analysis': analytics.get_generic_questions_analysis() or {},
            'qualitative_insights': analytics.get_qualitative_insights() or {},
            'timeline_data': analytics.get_response_timeline() or {},
            'cross_tabs': safe_cross_tabs(analytics),
            'sql_cross_tabs': analytics.get_sql_based_cross_tabs() or {},
            'advanced_analytics': analytics.get_advanced_analytics() or {},
            'visualizations': {
                'quota_chart': analytics.create_quota_chart() or '',
                **(analytics.create_cross_tab_charts() or {})
            }
        }
        logger.debug(f"Qualitative insights sections: {list(data['qualitative_insights'].keys())}")
        return data

    except (DatabaseError, ValueError) as e:
        logger.error(f"Error preparing analytics data: {e}")
        return {}

def safe_cross_tabs(analytics):
    """Safely format cross-tab percentages."""
    try:
        ct = analytics.get_cross_tabulations()
        if not ct or 'percentages' not in ct:
            return ct or {}
        raw = ct['percentages']
        
        # Check if the object has a .map method (Pandas Series) or .apply (Pandas DataFrame)
        # Note: If pandas is not imported, this will raise a NameError, but assuming it is used by SurveyAnalytics.
        if hasattr(raw, 'map'):
            formatted = raw.map(lambda x: f"{x:.1%}")
        else:
            # Assumes it is a dictionary of Series (from to_dict) or a DataFrame
            formatted = raw.apply(lambda col: col.map(lambda x: f"{x:.1%}"))
            
        ct['percentages'] = formatted.to_dict()
        return ct
    except Exception as e:
        logger.warning(f"Cross-tab formatting failed: {e}")
        return {}
        
# --- View Functions ---

@staff_member_required
@csrf_protect
def admin_dashboard_view(request):
    """Render the admin dashboard with survey analytics and visualizations."""
    try:
        analytics = SurveyAnalytics()
        data = get_analytics_data(analytics)

        if not data:
            messages.error(request, "Failed to load survey data")
            return redirect('admin:index')

        context = {
            'title': 'Survey Analytics Dashboard',
            'total_responses': data['summary_stats'].get('total_responses', 0),
            'total_target': data['quota_status'].get('total', {}).get('target', 60),
            **data
        }
        return render(request, 'survey/analytics_dashboard.html', context)

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        messages.error(request, f"Error loading dashboard: {str(e)}")
        return redirect('admin:index')


@staff_member_required_api
def api_dashboard_stats(request):
    """API endpoint for real-time dashboard analytics (Deduplicated and uses custom decorator)."""
    try:
        analytics = SurveyAnalytics()
        data = get_analytics_data(analytics)

        if not data:
            return JsonResponse({'error': 'Failed to load analytics data'}, status=500)

        # Convert data to JSON-serializable format (Consolidated logic for clarity)
        def make_serializable(obj):
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            # Fallback for complex objects that DjangoJSONEncoder might handle or should be stringified
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                return str(obj)

        serializable_data = {
            'summary': make_serializable(data['summary_stats']),
            'quota_status': make_serializable(data['quota_status']),
            'timeline': make_serializable(data['timeline_data']),
            'advanced_analytics': make_serializable(data['advanced_analytics'])
        }

        # Note: JsonResponse uses DjangoJSONEncoder by default, but the manual serialization 
        # using make_serializable handles numpy/pandas objects directly for safety.
        return JsonResponse(serializable_data)

    except Exception as e:
        logger.error(f"API stats error: {e}")
        return JsonResponse({'error': f'Error loading stats: {str(e)}'}, status=500)


@staff_member_required
def export_data(request):
    """Export survey data to Excel or SPSS format."""
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

        # Use tempfile to ensure cleanup
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # The analytics export methods are expected to write to a file and return its path
            filename = (
                analytics.export_to_excel() if export_type == 'excel'
                else analytics.export_to_spss_format()
            )
            
            if not filename or not os.path.exists(filename):
                raise FileNotFoundError("Export file could not be generated")

            # Read the generated file and prepare the response
            with open(filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type=content_type)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
            
            # Clean up the generated file after sending the response
            os.remove(filename)
            return response

    except (DatabaseError, FileNotFoundError, IOError) as e:
        logger.error(f"Export error (type={export_type}): {e}")
        messages.error(request, f"Failed to export data: {str(e)}")
        return redirect('admin:index')


@staff_member_required
def export_qualitative_data(request):
    """Export qualitative insights to CSV format."""
    try:
        analytics = SurveyAnalytics()
        if not analytics.load_data():
            messages.error(request, "Failed to load survey data for export")
            return redirect('survey:admin_dashboard')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="qualitative_insights.csv"'
        writer = csv.writer(response)
        writer.writerow(['Section', 'Insight', 'Word Count', 'Sentiment'])

        qualitative_insights = analytics.get_qualitative_insights()
        for section, insights in qualitative_insights.items():
            # Iterate over the responses within the section, limiting to the first 10 as in original
            for insight in insights.get('responses', [])[:10]:
                word_count = len(insight.split())
                
                # Basic sentiment analysis logic (as provided in original)
                sentiment = 'neutral'
                if any(word in insight.lower() for word in ['good', 'great', 'excellent', 'positive']):
                    sentiment = 'positive'
                elif any(word in insight.lower() for word in ['bad', 'poor', 'issue', 'problem']):
                    sentiment = 'negative'
                    
                writer.writerow([section, insight, word_count, sentiment])

        return response

    except Exception as e:
        logger.error(f"Qualitative export error: {str(e)}")
        messages.error(request, f"Failed to export qualitative data: {str(e)}")
        return redirect('survey:admin_dashboard')