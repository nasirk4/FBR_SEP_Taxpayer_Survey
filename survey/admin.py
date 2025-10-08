# /home/nasirk4/FBR_SEP_Taxpayer_Survey/survey/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SurveyResponse

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'professional_role', 'province', 'submission_date', 'reference_number', 'survey_completion_status']
    list_filter = ['professional_role', 'province', 'submission_date']
    search_fields = ['full_name', 'email', 'reference_number']
    readonly_fields = ['submission_date', 'reference_number', 'survey_completion_status_display']
    ordering = ['-submission_date']

    fieldsets = (
        ('Respondent Information', {
            'fields': ('full_name', 'email', 'district', 'mobile', 'professional_role', 'province')
        }),
        ('Experience', {
            'fields': ('experience_legal', 'experience_customs')
        }),
        ('Generic Questions', {
            'fields': ('g1_iris_rating', 'g2_system_weaknesses', 'g2a_weaknesses_details',
                      'g3_iris_limitations', 'g4_challenged_groups', 'g4_other_text',
                      'g5_clients_change', 'g6_fee_change', 'g7_digital_literacy_impact',
                      'g8_regional_differences', 'g8_regional_differences_text')
        }),
        ('Legal Practitioner Questions', {
            'fields': (
                'lp1_technical_issues',
                'lp2_common_problems', 'lp2_other_text',
                'lp3_improvement_areas', 'lp3_other_text',
                'lp4_procedures', 'lp4_other_procedure', 'lp4_other_sales', 'lp4_other_income', 'lp4_other_comment',
                'lp5_representation_challenges', 'lp5_other_text',
                'lp6_filing_efficiency', 'lp6_qualitative_text', 'lp6_qualitative_visible',
                'lp7_case_tracking', 'lp8_notice_communication', 'lp8_qualitative_text', 'lp8_qualitative_visible',
                'lp9_law_accessibility', 'lp10_law_change_impact', 'lp10_qualitative_text', 'lp10_qualitative_visible',
                'lp11_adr_effectiveness', 'lp12_dispute_transparency', 'lp13_overall_satisfaction', 'final_feedback'
            ),
            'classes': ('collapse',)
        }),
        ('Customs Agent Questions', {
            'fields': (
                'ca1_training_received', 'ca1a_training_usefulness',
                'ca2_psw_weboc_integration', 'ca3_psw_comparison',
                'ca4_procedure_challenges', 'ca4_other_text',
                'ca5_duty_assessment', 'ca6_cargo_efficiency',
                'ca7_document_verification', 'ca8_agency_coordination',
                'ca9_system_reliability', 'ca10_policy_impact',
                'ca11_client_representation', 'ca12_operational_challenges', 'ca12_other_text',
                'ca13_biggest_challenge', 'ca13_other_text'
            ),
            'classes': ('collapse',)
        }),
        ('Cross-System Perspectives', {
            'fields': ('cross_system_answers',),
            'classes': ('collapse',)
        }),
        ('Final Remarks', {
            'fields': ('final_remarks',)
        }),
        ('Metadata', {
            'fields': ('submission_date', 'reference_number', 'survey_completion_status_display'),
            'classes': ('collapse',)
        })
    )

    def survey_completion_status(self, obj):
        """Display completion status in list view"""
        status_parts = []

        if obj.professional_role in ['legal', 'both'] and obj.has_legal_answers:
            status_parts.append('LP')
        if obj.professional_role in ['customs', 'both'] and obj.has_customs_answers:
            status_parts.append('CA')
        if obj.has_cross_system_answers:
            status_parts.append('XS')
        if obj.final_remarks:
            status_parts.append('FR')

        if status_parts:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ {}</span>',
                '/'.join(status_parts)
            )
        else:
            return format_html('<span style="color: orange;">In Progress</span>')

    survey_completion_status.short_description = 'Completion'

    def survey_completion_status_display(self, obj):
        """Display detailed completion status in change form"""
        status_details = []

        # Generic questions
        if obj.g1_iris_rating and obj.g2_system_weaknesses:
            status_details.append('✓ Generic Questions')
        else:
            status_details.append('❌ Generic Questions')

        # Role-specific questions
        if obj.professional_role in ['legal', 'both']:
            if obj.has_legal_answers:
                status_details.append('✓ Legal Practitioner Questions')
            else:
                status_details.append('❌ Legal Practitioner Questions')

        if obj.professional_role in ['customs', 'both']:
            if obj.has_customs_answers:
                status_details.append('✓ Customs Agent Questions')
            else:
                status_details.append('❌ Customs Agent Questions')

        # Cross-system perspectives
        if obj.has_cross_system_answers:
            status_details.append('✓ Cross-System Perspectives')
        else:
            cross_data = obj.get_cross_system_data()
            if cross_data and cross_data.get('skipped'):
                status_details.append('⏭️ Cross-System Perspectives (Skipped)')
            else:
                status_details.append('❌ Cross-System Perspectives')

        # Final remarks
        if obj.final_remarks:
            status_details.append('✓ Final Remarks')
        else:
            status_details.append('❌ Final Remarks')

        return format_html('<br>'.join(status_details))

    survey_completion_status_display.short_description = 'Survey Completion Status'

    def get_readonly_fields(self, request, obj=None):
        """Make all fields readonly for existing objects to prevent data corruption"""
        if obj:  # editing an existing object
            return [field.name for field in self.model._meta.fields] + ['survey_completion_status_display']
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        return urls

    def changelist_view(self, request, extra_context=None):
        # Add dashboard link to the change list page
        extra_context = extra_context or {}
        try:
            dashboard_url = reverse('survey:admin_dashboard')
        except:
            dashboard_url = '/admin/dashboard/'

        extra_context['dashboard_link'] = format_html(
            '<div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; text-align: center;">'
            '<a href="{}" style="color: #4CAF50; text-decoration: none; font-weight: bold; font-size: 16px;">'
            '📊 View Analytics Dashboard'
            '</a>'
            '</div>',
            dashboard_url
        )
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        """Disable adding survey responses from admin (should only be created via survey)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser

    def get_queryset(self, request):
        """Optimize queryset for admin performance"""
        return super().get_queryset(request).select_related().prefetch_related()

    def formatted_json_display(self, value):
        """Helper to display JSON fields in a readable format"""
        if not value:
            return "-"

        if isinstance(value, list):
            if not value:
                return "-"
            return format_html("<ul>{}</ul>",
                "".join([f"<li>{item}</li>" for item in value])
            )
        elif isinstance(value, dict):
            if not value:
                return "-"
            return format_html("<ul>{}</ul>",
                "".join([f"<li><strong>{k}:</strong> {v}</li>" for k, v in value.items()])
            )
        return str(value)

    # Custom display methods for JSON fields
    def g4_challenged_groups_display(self, obj):
        return self.formatted_json_display(obj.get_g4_challenged_groups_display())
    g4_challenged_groups_display.short_description = "Challenged Groups"

    def lp2_common_problems_display(self, obj):
        return self.formatted_json_display(obj.get_lp2_common_problems_display())
    lp2_common_problems_display.short_description = "Technical Issues"

    def lp3_improvement_areas_display(self, obj):
        return self.formatted_json_display(obj.get_lp3_improvement_areas_display())
    lp3_improvement_areas_display.short_description = "Improvement Areas"

    def lp5_representation_challenges_display(self, obj):
        return self.formatted_json_display(obj.get_lp5_representation_challenges_display())
    lp5_representation_challenges_display.short_description = "Representation Challenges"

    def ca4_procedure_challenges_display(self, obj):
        return self.formatted_json_display(obj.get_ca4_procedure_challenges_display())
    ca4_procedure_challenges_display.short_description = "Procedure Challenges"

    def ca12_operational_challenges_display(self, obj):
        return self.formatted_json_display(obj.get_ca12_operational_challenges_display())
    ca12_operational_challenges_display.short_description = "Operational Challenges"

    def cross_system_answers_display(self, obj):
        cross_data = obj.get_cross_system_data()
        if not cross_data or cross_data.get('skipped'):
            return "Skipped" if cross_data and cross_data.get('skipped') else "-"

        display_items = []
        if cross_data.get('xs1_coordination_gap'):
            display_items.append(f"<strong>XS1:</strong> {cross_data['xs1_coordination_gap'][:100]}...")
        if cross_data.get('xs2_single_change'):
            display_items.append(f"<strong>XS2:</strong> {cross_data['xs2_single_change'][:100]}...")
        if cross_data.get('xs3_systemic_feedback'):
            display_items.append(f"<strong>XS3:</strong> {cross_data['xs3_systemic_feedback'][:100]}...")

        if display_items:
            return format_html("<ul>{}</ul>", "".join([f"<li>{item}</li>" for item in display_items]))
        return "-"

    cross_system_answers_display.short_description = "Cross-System Perspectives"