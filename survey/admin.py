# /home/nasirk4/FBR_SEP_Taxpayer_Survey/survey/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Q
import json
from .models import SurveyResponse

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'professional_role', 'province', 'submission_date', 
        'reference_number', 'completion_percentage', 'survey_completion_status'
    ]
    list_filter = [
        'professional_role', 'province', 'submission_date', 'kii_consent',
        #'completion_status'
    ]
    search_fields = ['full_name', 'email', 'reference_number', 'mobile', 'district']
    readonly_fields = [
        'submission_date', 'reference_number', 'survey_completion_status_display',
        'completion_percentage_display', 'data_quality_indicators'
    ]
    ordering = ['-submission_date']
    actions = ['export_selected_responses', 'mark_for_kii_followup', 'calculate_completion_metrics']
    
    # Enhanced list display configuration
    list_per_page = 50
    list_max_show_all = 200
    show_full_result_count = True

    fieldsets = (
        ('Respondent Information', {
            'fields': (
                'full_name', 'email', 'district', 'mobile', 'professional_role', 
                'province', 'practice_areas', 'kii_consent'
            )
        }),
        ('Experience', {
            'fields': ('experience_legal', 'experience_customs'),
            'classes': ('collapse',)
        }),
        ('Generic Questions', {
            'fields': (
                'g1_policy_impact_display', 'g2_system_impact_display', 
                'g3_technical_issues', 'g4_disruption', 'g5_digital_literacy'
            )
        }),
        ('Legal Practitioner Questions', {
            'fields': (
                'lp1_digital_support', 'lp2_challenges_display', 'lp3_challenges_display', 
                'lp4_challenges_display', 'lp5_tax_types_display', 'lp5_visible', 
                'lp6_priority_improvement'
            ),
            'classes': ('collapse',)
        }),
        ('Customs Agent Questions', {
            'fields': (
                'ca1_training', 'ca2_system_integration', 'ca3_challenges_display', 
                'ca4_effectiveness_display', 'ca5_policy_impact', 'ca6_biggest_challenge', 
                'ca6_improvement'
            ),
            'classes': ('collapse',)
        }),
        ('Cross-System Perspectives', {
            'fields': ('cross_system_answers_display',),
            'classes': ('collapse',)
        }),
        ('Final Remarks and Feedback', {
            'fields': ('final_remarks', 'survey_feedback')
        }),
        ('Completion Analytics', {
            'fields': (
                'completion_percentage_display', 'survey_completion_status_display', 
                'data_quality_indicators'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('submission_date', 'reference_number'),
            'classes': ('collapse',)
        })
    )

    def get_list_display(self, request):
        """Dynamic list display based on user permissions."""
        base_display = [
            'full_name', 'professional_role', 'province', 'submission_date', 
            'reference_number'
        ]
        
        if request.user.has_perm('survey.view_completion_metrics'):
            base_display.extend(['completion_percentage', 'survey_completion_status'])
        else:
            base_display.append('survey_completion_status')
            
        return base_display

    def completion_percentage(self, obj):
        """Display completion percentage with progress bar in list view."""
        percentage = self._calculate_completion_percentage(obj)
        
        color = "green" if percentage >= 80 else "orange" if percentage >= 50 else "red"
        
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 3px; height: 20px; position: relative;">'
            '<div style="width: {}%; background: {}; height: 100%; border-radius: 3px;"></div>'
            '<div style="position: absolute; top: 0; left: 0; width: 100%; text-align: center; '
            'font-size: 11px; font-weight: bold; color: #333; line-height: 20px;">{}%</div>'
            '</div>',
            percentage, color, percentage
        )
    completion_percentage.short_description = 'Completion %'

    def _calculate_completion_percentage(self, obj):
        """Calculate precise completion percentage."""
        total_weight = 0
        completed_weight = 0
        
        # Generic questions (weight: 30%)
        generic_fields = ['g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 'g5_digital_literacy']
        generic_weight = 30 / len(generic_fields)
        for field in generic_fields:
            total_weight += generic_weight
            if getattr(obj, field):
                completed_weight += generic_weight

        # Role-specific questions (weight: 50%)
        role_weight = 50
        if obj.professional_role in ['legal', 'both']:
            legal_fields = ['lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 'lp4_challenges', 'lp5_tax_types']
            legal_field_weight = role_weight / len(legal_fields)
            for field in legal_fields:
                total_weight += legal_field_weight
                if getattr(obj, field):
                    completed_weight += legal_field_weight
                    
        if obj.professional_role in ['customs', 'both']:
            customs_fields = ['ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness', 'ca5_policy_impact', 'ca6_biggest_challenge']
            customs_field_weight = role_weight / len(customs_fields)
            for field in customs_fields:
                total_weight += customs_field_weight
                if getattr(obj, field):
                    completed_weight += customs_field_weight

        # Cross-system and final remarks (weight: 20%)
        final_fields = ['cross_system_answers', 'final_remarks']
        final_weight = 20 / len(final_fields)
        for field in final_fields:
            total_weight += final_weight
            if getattr(obj, field):
                completed_weight += final_weight

        return round((completed_weight / total_weight) * 100) if total_weight > 0 else 0

    def survey_completion_status(self, obj):
        """Enhanced completion status with detailed indicators."""
        status_parts = []
        percentage = self._calculate_completion_percentage(obj)

        # Generic questions
        if any([obj.g1_policy_impact, obj.g2_system_impact, obj.g3_technical_issues, obj.g5_digital_literacy]):
            status_parts.append('G')

        # Role-specific questions
        if obj.professional_role in ['legal', 'both']:
            if any([obj.lp1_digital_support, obj.lp2_challenges, obj.lp3_challenges, 
                   obj.lp4_challenges, obj.lp5_tax_types]):
                status_parts.append('LP')

        if obj.professional_role in ['customs', 'both']:
            if any([obj.ca1_training, obj.ca2_system_integration, obj.ca3_challenges, 
                   obj.ca4_effectiveness, obj.ca5_policy_impact, obj.ca6_biggest_challenge]):
                status_parts.append('CA')

        # Additional sections
        if obj.cross_system_answers:
            status_parts.append('XS')
        if obj.final_remarks or obj.survey_feedback:
            status_parts.append('FR')

        if status_parts:
            color = "green" if percentage >= 80 else "orange" if percentage >= 50 else "red"
            return format_html(
                '<span style="color: {}; font-weight: bold;">✓ {} ({}%)</span>',
                color, '/'.join(status_parts), percentage
            )
        return format_html('<span style="color: gray;">Not Started</span>')

    survey_completion_status.short_description = 'Status'

    def completion_percentage_display(self, obj):
        """Display detailed completion breakdown in change form."""
        percentage = self._calculate_completion_percentage(obj)
        
        breakdown = [
            f"Overall Completion: <strong>{percentage}%</strong>",
            f"Generic Questions: {self._section_completion(obj, 'generic')}%",
            f"Role-Specific Questions: {self._section_completion(obj, 'role')}%",
            f"Final Sections: {self._section_completion(obj, 'final')}%"
        ]
        
        return format_html("<br>".join(breakdown))
    completion_percentage_display.short_description = 'Completion Breakdown'

    def _section_completion(self, obj, section):
        """Calculate completion percentage for specific sections."""
        if section == 'generic':
            fields = ['g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 'g5_digital_literacy']
        elif section == 'role':
            fields = []
            if obj.professional_role in ['legal', 'both']:
                fields.extend(['lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 'lp4_challenges', 'lp5_tax_types'])
            if obj.professional_role in ['customs', 'both']:
                fields.extend(['ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness', 'ca5_policy_impact', 'ca6_biggest_challenge'])
        elif section == 'final':
            fields = ['cross_system_answers', 'final_remarks']
        else:
            return 0
            
        completed = sum(1 for field in fields if getattr(obj, field))
        return round((completed / len(fields)) * 100) if fields else 0

    def survey_completion_status_display(self, obj):
        """Enhanced detailed completion status in change form."""
        status_details = []
        percentage = self._calculate_completion_percentage(obj)

        # Generic questions with individual field status
        generic_fields = [
            ('G1 Policy Impact', obj.g1_policy_impact),
            ('G2 System Impact', obj.g2_system_impact),
            ('G3 Technical Issues', obj.g3_technical_issues),
            ('G5 Digital Literacy', obj.g5_digital_literacy)
        ]
        
        generic_complete = any(field[1] for field in generic_fields)
        status_details.append(
            f"✅ Generic Questions ({self._section_completion(obj, 'generic')}%)" 
            if generic_complete else 
            f"❌ Generic Questions ({self._section_completion(obj, 'generic')}%)"
        )

        # Role-specific questions
        if obj.professional_role in ['legal', 'both']:
            legal_complete = any([
                obj.lp1_digital_support, obj.lp2_challenges, obj.lp3_challenges,
                obj.lp4_challenges, obj.lp5_tax_types
            ])
            status_details.append(
                f"✅ Legal Practitioner Questions ({self._section_completion(obj, 'role')}%)" 
                if legal_complete else 
                f"❌ Legal Practitioner Questions ({self._section_completion(obj, 'role')}%)"
            )

        if obj.professional_role in ['customs', 'both']:
            customs_complete = any([
                obj.ca1_training, obj.ca2_system_integration, obj.ca3_challenges,
                obj.ca4_effectiveness, obj.ca5_policy_impact, obj.ca6_biggest_challenge
            ])
            status_details.append(
                f"✅ Customs Agent Questions ({self._section_completion(obj, 'role')}%)" 
                if customs_complete else 
                f"❌ Customs Agent Questions ({self._section_completion(obj, 'role')}%)"
            )

        # Cross-system perspectives
        if obj.cross_system_answers:
            cross_data = obj.cross_system_answers
            if isinstance(cross_data, dict) and cross_data.get('skipped'):
                status_details.append('⏭️ Cross-System Perspectives (Skipped)')
            else:
                status_details.append('✅ Cross-System Perspectives')
        else:
            status_details.append('❌ Cross-System Perspectives')

        # Final remarks and feedback
        final_complete = obj.final_remarks or obj.survey_feedback
        status_details.append(
            '✅ Final Remarks/Feedback' if final_complete else '❌ Final Remarks/Feedback'
        )

        # Add overall percentage
        status_details.insert(0, f"<strong>Overall Completion: {percentage}%</strong>")

        return format_html('<br>'.join(status_details))
    survey_completion_status_display.short_description = 'Detailed Completion Status'

    def data_quality_indicators(self, obj):
        """Display data quality indicators."""
        indicators = []
        
        # Check for required fields
        required_fields = ['full_name', 'email', 'professional_role', 'province']
        missing_required = [field for field in required_fields if not getattr(obj, field)]
        if missing_required:
            indicators.append(f"❌ Missing required fields: {', '.join(missing_required)}")
        else:
            indicators.append("✅ All required fields completed")

        # Check JSON field validity
        json_fields = [
            'g1_policy_impact', 'g2_system_impact', 'lp2_challenges', 'lp3_challenges',
            'lp4_challenges', 'lp5_tax_types', 'ca3_challenges', 'ca4_effectiveness'
        ]
        invalid_json = []
        for field in json_fields:
            value = getattr(obj, field)
            if value and isinstance(value, str):
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    invalid_json.append(field)
        
        if invalid_json:
            indicators.append(f"⚠️ Invalid JSON in: {', '.join(invalid_json)}")
        else:
            indicators.append("✅ All JSON fields valid")

        # Role-specific field completeness
        if obj.professional_role in ['legal', 'both']:
            legal_fields = ['lp1_digital_support', 'lp2_challenges', 'lp3_challenges', 'lp4_challenges']
            missing_legal = [field for field in legal_fields if not getattr(obj, field)]
            if missing_legal:
                indicators.append(f"⚠️ Missing legal fields: {len(missing_legal)}")
            else:
                indicators.append("✅ Legal fields complete")

        if obj.professional_role in ['customs', 'both']:
            customs_fields = ['ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness']
            missing_customs = [field for field in customs_fields if not getattr(obj, field)]
            if missing_customs:
                indicators.append(f"⚠️ Missing customs fields: {len(missing_customs)}")
            else:
                indicators.append("✅ Customs fields complete")

        return format_html('<br>'.join(indicators))
    data_quality_indicators.short_description = 'Data Quality'

    def get_readonly_fields(self, request, obj=None):
        """Enhanced readonly fields management."""
        if obj:  # Existing object - make most fields readonly
            base_readonly = [field.name for field in self.model._meta.fields]
            additional_readonly = [
                'survey_completion_status_display', 
                'completion_percentage_display',
                'data_quality_indicators'
            ]
            
            # Allow editing of certain fields even for existing objects
            editable_fields = ['kii_consent', 'survey_feedback']  # Admin can update these
            readonly_fields = [f for f in base_readonly if f not in editable_fields] + additional_readonly
            return readonly_fields
            
        return self.readonly_fields

    def get_queryset(self, request):
        """Optimized queryset with performance enhancements."""
        queryset = super().get_queryset(request)
        
        # Prefetch related data and defer large fields if not needed
        return queryset.select_related().prefetch_related().defer(
            'lp6_priority_improvement', 'ca6_improvement', 'final_remarks', 'survey_feedback'
        )

    # Enhanced JSON field display methods using model's display methods
    def formatted_json_display(self, value, max_items=10):
        """Enhanced JSON display with truncation for large datasets."""
        if not value:
            return format_html('<span style="color: #666;">-</span>')

        if isinstance(value, list):
            if not value:
                return format_html('<span style="color: #666;">-</span>')
            items = value[:max_items]
            display_items = "".join([f"<li>{item}</li>" for item in items])
            if len(value) > max_items:
                display_items += f"<li><em>... and {len(value) - max_items} more</em></li>"
            return format_html("<ul style='margin: 0; padding-left: 20px;'>{}</ul>", display_items)
            
        elif isinstance(value, dict):
            if not value:
                return format_html('<span style="color: #666;">-</span>')
            items = list(value.items())[:max_items]
            display_items = "".join([f"<li><strong>{k}:</strong> {v}</li>" for k, v in items])
            if len(value) > max_items:
                display_items += f"<li><em>... and {len(value) - max_items} more items</em></li>"
            return format_html("<ul style='margin: 0; padding-left: 20px;'>{}</ul>", display_items)
            
        return format_html('<span>{}</span>', str(value))

    def g1_policy_impact_display(self, obj):
        display_data = obj.get_g1_policy_impact_display()
        return self.formatted_json_display(display_data)
    g1_policy_impact_display.short_description = "G1 - Policy Impact"

    def g2_system_impact_display(self, obj):
        display_data = obj.get_g2_system_impact_display()
        return self.formatted_json_display(display_data)
    g2_system_impact_display.short_description = "G2 - System Impact"

    def lp2_challenges_display(self, obj):
        display_data = obj.get_lp2_challenges_display()
        return self.formatted_json_display(display_data)
    lp2_challenges_display.short_description = "LP2 - Representation Challenges"

    def lp3_challenges_display(self, obj):
        display_data = obj.get_lp3_challenges_display()
        return self.formatted_json_display(display_data)
    lp3_challenges_display.short_description = "LP3 - Compliance Challenges"

    def lp4_challenges_display(self, obj):
        display_data = obj.get_lp4_challenges_display()
        return self.formatted_json_display(display_data)
    lp4_challenges_display.short_description = "LP4 - Dispute Resolution Challenges"

    def lp5_tax_types_display(self, obj):
        display_data = obj.get_lp5_tax_types_display()
        return self.formatted_json_display(display_data)
    lp5_tax_types_display.short_description = "LP5 - Tax Type Impact"

    def ca3_challenges_display(self, obj):
        display_data = obj.get_ca3_challenges_display()
        return self.formatted_json_display(display_data)
    ca3_challenges_display.short_description = "CA3 - Customs Function Challenges"

    def ca4_effectiveness_display(self, obj):
        display_data = obj.get_ca4_effectiveness_display()
        return self.formatted_json_display(display_data)
    ca4_effectiveness_display.short_description = "CA4 - Process Effectiveness"

    def cross_system_answers_display(self, obj):
        cross_data = obj.cross_system_answers
        if not cross_data or (isinstance(cross_data, dict) and cross_data.get('skipped')):
            status = "Skipped" if cross_data and cross_data.get('skipped') else "Not Completed"
            return format_html('<span style="color: #666;">{}</span>', status)

        display_data = obj.get_cross_system_answers_display()
        return self.formatted_json_display(display_data)
    cross_system_answers_display.short_description = "Cross-System Perspectives"

    # Admin Actions
    def export_selected_responses(self, request, queryset):
        """Admin action to export selected responses."""
        from .admin_dashboard import SurveyAnalytics
        
        try:
            analytics = SurveyAnalytics()
            if analytics.load_data():
                filename = analytics.export_to_excel()
                if filename:
                    self.message_user(
                        request, 
                        f"Successfully exported {queryset.count()} responses to {filename}", 
                        messages.SUCCESS
                    )
                else:
                    self.message_user(
                        request, 
                        "Failed to export responses", 
                        messages.ERROR
                    )
            else:
                self.message_user(
                    request, 
                    "Failed to load data for export", 
                    messages.ERROR
                )
        except Exception as e:
            self.message_user(
                request, 
                f"Export error: {str(e)}", 
                messages.ERROR
            )
    export_selected_responses.short_description = "Export selected responses to Excel"

    def mark_for_kii_followup(self, request, queryset):
        """Mark selected responses for KII follow-up."""
        updated = queryset.update(kii_consent='yes')
        self.message_user(
            request, 
            f"Marked {updated} responses for KII follow-up", 
            messages.SUCCESS
        )
    mark_for_kii_followup.short_description = "Mark for KII follow-up"

    def calculate_completion_metrics(self, request, queryset):
        """Recalculate completion metrics for selected responses."""
        for obj in queryset:
            # Trigger completion calculation
            self._calculate_completion_percentage(obj)
        
        self.message_user(
            request, 
            f"Recalculated completion metrics for {queryset.count()} responses", 
            messages.SUCCESS
        )
    calculate_completion_metrics.short_description = "Recalculate completion metrics"

    def changelist_view(self, request, extra_context=None):
        """Enhanced change list with analytics dashboard link."""
        extra_context = extra_context or {}
        
        # Add dashboard link
        try:
            dashboard_url = reverse('survey:admin_dashboard')
            extra_context['dashboard_link'] = format_html(
                '<div style="margin: 10px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
                'border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">'
                '<a href="{}" style="color: white; text-decoration: none; font-weight: bold; font-size: 16px; '
                'display: inline-block; padding: 10px 20px; border: 2px solid white; border-radius: 4px;">'
                '📊 View Analytics Dashboard'
                '</a>'
                '<p style="color: white; margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">'
                'Access detailed analytics, quotas, and export functionality'
                '</p>'
                '</div>',
                dashboard_url
            )
        except:
            pass  # Dashboard URL not configured

        # Add quick stats
        total_responses = SurveyResponse.objects.count()
        completed_responses = SurveyResponse.objects.filter(
            Q(g1_policy_impact__isnull=False) & 
            Q(g2_system_impact__isnull=False) &
            Q(g3_technical_issues__isnull=False)
        ).count()
        
        extra_context['quick_stats'] = format_html(
            '<div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; '
            'border-left: 4px solid #4CAF50;">'
            '<strong>Quick Stats:</strong> {} Total Responses, {} Substantially Complete'
            '</div>',
            total_responses, completed_responses
        )

        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        """Disable adding survey responses from admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers."""
        return request.user.is_superuser

    def get_ordering(self, request):
        """Default ordering for the admin list."""
        return ['-submission_date']

    class Media:
        """Custom CSS for admin interface."""
        css = {
            'all': ('admin/css/survey_admin.css',)
        }