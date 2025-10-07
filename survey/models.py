from django.db import models
import uuid
import json

class SurveyResponse(models.Model):
    # Basic Information
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    district = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Professional Information
    PROFESSIONAL_CHOICES = [
        ('legal', 'Legal Practitioner'),
        ('customs', 'Customs Agent'),
        ('both', 'Both'),
    ]
    professional_role = models.CharField(max_length=10, choices=PROFESSIONAL_CHOICES)
    experience_legal = models.CharField(max_length=20, blank=True, null=True)
    experience_customs = models.CharField(max_length=20, blank=True, null=True)
    
    # Geographic Information
    PROVINCE_CHOICES = [
        ('balochistan', 'Balochistan'),
        ('ict', 'ICT'),
        ('kpk', 'KPK'),
        ('punjab', 'Punjab'),
        ('sindh', 'Sindh'),
    ]
    province = models.CharField(max_length=20, choices=PROVINCE_CHOICES)
    
    # Generic Questions (G1-G8)
    g1_iris_rating = models.CharField(max_length=20, blank=True)
    g2_system_weaknesses = models.CharField(max_length=3, blank=True)
    g2a_weaknesses_details = models.TextField(blank=True)
    g3_iris_limitations = models.TextField(blank=True)
    g4_challenged_groups = models.JSONField(default=list)  # Store multiple selections
    g4_other_text = models.TextField(blank=True)
    g5_clients_change = models.CharField(max_length=30, blank=True)
    g6_fee_change = models.CharField(max_length=30, blank=True)
    g7_digital_literacy_impact = models.CharField(max_length=30, blank=True)
    g8_regional_differences = models.CharField(max_length=30, blank=True)
    g8_regional_differences_text = models.TextField(blank=True)
    
    # Legal Practitioner Questions (LP1-LP13)
    lp1_technical_issues = models.CharField(max_length=30, blank=True)
    lp2_common_problems = models.JSONField(default=list, blank=True)
    lp2_other_text = models.TextField(blank=True)
    lp3_improvement_areas = models.JSONField(default=list, blank=True)
    lp3_other_text = models.TextField(blank=True)
    lp4_procedures = models.JSONField(default=dict, blank=True)  # {sales: [], income: [], comments: {}}
    lp4_other_procedure = models.CharField(max_length=200, blank=True)
    lp4_other_sales = models.BooleanField(default=False)
    lp4_other_income = models.BooleanField(default=False)
    lp4_other_comment = models.TextField(blank=True)
    lp5_representation_challenges = models.JSONField(default=list, blank=True)
    lp5_other_text = models.TextField(blank=True)
    lp6_filing_efficiency = models.CharField(max_length=30, blank=True)
    lp7_case_tracking = models.CharField(max_length=30, blank=True)
    lp8_notice_communication = models.CharField(max_length=30, blank=True)
    lp9_law_accessibility = models.CharField(max_length=30, blank=True)
    lp10_law_change_impact = models.CharField(max_length=30, blank=True)
    lp11_adr_effectiveness = models.CharField(max_length=30, blank=True)
    lp12_dispute_transparency = models.CharField(max_length=30, blank=True)
    lp13_overall_satisfaction = models.CharField(max_length=30, blank=True)
    lp13_feedback = models.TextField(blank=True)
    
    # Customs Agent Questions (CA1-CA9)
    ca1_training_received = models.CharField(max_length=50, blank=True)
    ca1a_training_usefulness = models.CharField(max_length=20, blank=True)
    ca2_psw_weboc_integration = models.CharField(max_length=50, blank=True)
    ca3_procedure_challenges = models.JSONField(default=list, blank=True)
    ca3_other_text = models.TextField(blank=True)
    ca4_duty_assessment = models.CharField(max_length=50, blank=True)
    ca5_psw_vs_weboc = models.CharField(max_length=50, blank=True)
    ca6_cargo_efficiency = models.CharField(max_length=30, blank=True)
    ca7_system_reliability = models.CharField(max_length=30, blank=True)
    ca8_policy_impact = models.CharField(max_length=30, blank=True)
    ca9_operational_challenges = models.JSONField(default=list, blank=True)
    ca9_other_text = models.TextField(blank=True)
    ca9_feedback = models.TextField(blank=True)
    
    # Cross-System Perspectives (XS1-XS3)
    cross_system_answers = models.JSONField(default=dict, blank=True)  # Store all cross-system data as JSON
    
    # Final Remarks
    final_remarks = models.TextField(blank=True)
    
    # Metadata
    submission_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.reference_number}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate a more unique reference number
            self.reference_number = f"FBR{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def get_professional_role_display_name(self):
        return dict(self.PROFESSIONAL_CHOICES).get(self.professional_role, self.professional_role)
    
    def get_province_display_name(self):
        return dict(self.PROVINCE_CHOICES).get(self.province, self.province)
    
    def get_g4_challenged_groups_display(self):
        """Return formatted challenged groups for display"""
        group_mapping = {
            'limited_tax_understanding': 'People with limited tax understanding',
            'business_community': 'Business community',
            'salaried_class': 'Salaried class',
            'women_taxpayers': 'Women taxpayers',
            'differently_abled': 'Differently-abled taxpayers',
            'low_it_literacy': 'People with low IT literacy',
            'senior_citizens': 'Senior Citizens',
            'others': 'Others',
        }
        if isinstance(self.g4_challenged_groups, list):
            return [group_mapping.get(group, group) for group in self.g4_challenged_groups]
        return []
    
    def get_lp2_common_problems_display(self):
        """Return formatted LP2 problems for display"""
        problem_mapping = {
            'system_downtime': 'System downtime or slow performance',
            'login_failures': 'Login failures or session timeouts',
            'document_upload_errors': 'Document upload errors',
            'access_issues': 'Inability to access case records or notices',
            'data_mismatches': 'Data mismatches in client records',
            'audit_trail_issues': 'Lack of audit trail for actions taken',
            'vague_notices': 'Vague or inconsistent system-generated notices',
            'client_management': 'Limited functionality for managing multiple clients',
            'other': 'Other',
        }
        if isinstance(self.lp2_common_problems, list):
            return [problem_mapping.get(problem, problem) for problem in self.lp2_common_problems]
        return []
    
    def get_lp3_improvement_areas_display(self):
        """Return formatted LP3 improvement areas for display"""
        area_mapping = {
            'system_stability': 'System stability and uptime',
            'user_interface': 'User interface for legal filings',
            'document_management': 'Document management and submission',
            'case_tracking': 'Case status tracking and updates',
            'appellate_integration': 'Integration with appellate tribunal systems',
            'legal_research': 'Legal research and database access',
            'notification_system': 'Notification and alert system',
            'other': 'Other',
        }
        if isinstance(self.lp3_improvement_areas, list):
            return [area_mapping.get(area, area) for area in self.lp3_improvement_areas]
        return []
    
    def get_lp5_representation_challenges_display(self):
        """Return formatted LP5 challenges for display"""
        challenge_mapping = {
            'commissioner_appeals': 'Appeal filings before Commissioner (Appeals)',
            'appellate_tribunal': 'Appellate Tribunal representations',
            'high_court': 'High Court/Supreme Court references',
            'audit_response': 'Audit response proceedings',
            'show_cause': 'Show cause notice responses',
            'refund_processing': 'Refund claim processing',
            'settlement': 'Settlement applications',
            'adr': 'Alternate Dispute Resolution (ADR)',
            'other': 'Other',
        }
        if isinstance(self.lp5_representation_challenges, list):
            return [challenge_mapping.get(challenge, challenge) for challenge in self.lp5_representation_challenges]
        return []
    
    def get_ca3_procedure_challenges_display(self):
        """Return formatted CA3 challenges for display"""
        challenge_mapping = {
            'goods_declaration': 'Goods declaration filing',
            'classification': 'Classification under PCT codes',
            'customs_valuation': 'Customs valuation of goods',
            'duty_calculation': 'Duty and tax calculation',
            'document_verification': 'Document verification and submission',
            'cargo_examination': 'Cargo examination and release coordination',
            'refund_processing': 'Refund or drawback processing',
            'no_challenges': 'No significant challenges',
            'other': 'Other',
        }
        if isinstance(self.ca3_procedure_challenges, list):
            return [challenge_mapping.get(challenge, challenge) for challenge in self.ca3_procedure_challenges]
        return []
    
    def get_ca9_operational_challenges_display(self):
        """Return formatted CA9 challenges for display"""
        challenge_mapping = {
            'system_reliability': 'System reliability and downtime',
            'policy_changes': 'Frequent policy and procedure changes',
            'unpredictable_assessments': 'Unpredictable duty assessments',
            'cargo_delays': 'Cargo examination and release delays',
            'document_bottlenecks': 'Document processing bottlenecks',
            'client_management': 'Client management and communication',
            'inter_agency_coordination': 'Inter-agency coordination',
            'lack_training': 'Lack of adequate training',
            'other': 'Other',
        }
        if isinstance(self.ca9_operational_challenges, list):
            return [challenge_mapping.get(challenge, challenge) for challenge in self.ca9_operational_challenges]
        return []
    
    def get_cross_system_data(self):
        """Return formatted cross-system data"""
        if isinstance(self.cross_system_answers, dict):
            return self.cross_system_answers
        try:
            return json.loads(self.cross_system_answers) if self.cross_system_answers else {}
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @property
    def has_legal_answers(self):
        """Check if legal practitioner questions were answered"""
        return self.professional_role in ['legal', 'both'] and any([
            self.lp1_technical_issues,
            self.lp2_common_problems,
            self.lp3_improvement_areas,
            self.lp4_procedures,
            self.lp5_representation_challenges,
            self.lp6_filing_efficiency,
            self.lp7_case_tracking,
            self.lp8_notice_communication,
            self.lp9_law_accessibility,
            self.lp10_law_change_impact,
            self.lp11_adr_effectiveness,
            self.lp12_dispute_transparency,
            self.lp13_overall_satisfaction
        ])
    
    @property
    def has_customs_answers(self):
        """Check if customs agent questions were answered"""
        return self.professional_role in ['customs', 'both'] and any([
            self.ca1_training_received,
            self.ca1a_training_usefulness,
            self.ca2_psw_weboc_integration,
            self.ca3_procedure_challenges,
            self.ca4_duty_assessment,
            self.ca5_psw_vs_weboc,
            self.ca6_cargo_efficiency,
            self.ca7_system_reliability,
            self.ca8_policy_impact,
            self.ca9_operational_challenges
        ])
    
    @property
    def has_cross_system_answers(self):
        """Check if cross-system perspectives were provided"""
        cross_data = self.get_cross_system_data()
        return bool(cross_data and not cross_data.get('skipped'))
    
    class Meta:
        verbose_name = "Survey Response"
        verbose_name_plural = "Survey Responses"
        ordering = ['-submission_date']