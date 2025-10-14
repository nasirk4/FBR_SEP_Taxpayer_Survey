from django.db import models
import uuid
import json

class SurveyResponse(models.Model):
    # Basic Information
    full_name = models.CharField(max_length=200, help_text="RI1: Respondent's full name")
    email = models.EmailField(help_text="RI2: Respondent's email address")
    mobile = models.CharField(max_length=20, blank=True, null=True, help_text="RI3: Mobile number (optional)")  # O - FIXED: Added null=True
    province = models.CharField(
        max_length=20,
        choices=[
            ('ajk', 'Azad Jammu and Kashmir'),
            ('balochistan', 'Balochistan'),
            ('gb', 'Gilgit-Baltistan'),
            ('ict', 'ICT'),
            ('kpk', 'Khyber Pakhtunkhwa'),
            ('punjab', 'Punjab'),
            ('sindh', 'Sindh'),
        ],
        help_text="RI4: Province of residence"
    )
    district = models.CharField(max_length=100, help_text="RI5: District of residence (standard or custom)")

    # Professional Information
    professional_role = models.CharField(max_length=20, help_text="RI6: Professional role(s) as comma-separated values (e.g., 'legal', 'customs', 'legal,customs')")  # R
    experience_legal = models.CharField(max_length=20, blank=True, null=True, help_text="RI8: Years of experience as Legal Practitioner (if applicable)")  # O - CORRECT
    experience_customs = models.CharField(max_length=20, blank=True, null=True, help_text="RI9: Years of experience as Customs Agent (if applicable)")  # O - CORRECT
    practice_areas = models.CharField(max_length=100, blank=True, null=True, help_text="RI7: Primary practice areas as comma-separated values (e.g., 'income_tax,sales_tax')")  # O - FIXED: Added null=True
    kii_consent = models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True, help_text="RI10: Consent for follow-up interview")  # O - FIXED: Added null=True

    # Generic Questions (G1-G5)
    g1_policy_impact = models.JSONField(default=dict, help_text="G1: Policy impact matrix (e.g., {'service_delivery': 'positive', ...})")  # R
    g2_system_impact = models.JSONField(default=dict, help_text="G2: System impact matrix (e.g., {'workflow_efficiency': 'positive', ...})")  # R
    g3_technical_issues = models.CharField(max_length=20, help_text="G3: Frequency of technical issues (e.g., 'daily', 'never')")  # R
    g4_disruption = models.CharField(max_length=20, blank=True, null=True, help_text="G4: Significance of disruptions (e.g., 'very_significantly', null if skipped)")  # O - CORRECT
    g5_digital_literacy = models.CharField(max_length=20, help_text="G5: Digital literacy needs (e.g., 'neutral')")  # R

    # --- LEGAL PRACTITIONER QUESTIONS ---
    # LP1: Overall Digital Support
    lp1_digital_support = models.CharField(max_length=30, help_text="LP1: Overall digital support rating")  # R
    
    # LP2: Representation & Appeals Challenges Grid
    lp2_challenges = models.JSONField(default=dict, help_text="LP2: Representation challenges grid data")  # R
    
    # LP3: Compliance & Advisory Challenges Grid
    lp3_challenges = models.JSONField(default=dict, help_text="LP3: Compliance challenges grid data")  # R
    
    # LP4: Dispute Resolution & Documentation Challenges Grid
    lp4_challenges = models.JSONField(default=dict, help_text="LP4: Dispute resolution challenges grid data")  # R
    
    # LP5: Tax-Type Impact (conditional)
    lp5_tax_types = models.JSONField(default=dict, help_text="LP5: Tax-type impact for challenging functions")  # R
    lp5_visible = models.BooleanField(default=False, help_text="LP5: Whether tax-type section was visible")
    
    # LP6: Priority Improvement
    lp6_priority_improvement = models.TextField(blank=True, help_text="LP6: Priority improvement suggestion")  # O - CORRECT

    # --- CUSTOMS AGENT QUESTIONS ---
    # CA1: Training
    ca1_training = models.CharField(max_length=50, help_text="CA1: Training received")  # R
    
    # CA2: System Integration
    ca2_system_integration = models.CharField(max_length=50, help_text="CA2: System integration rating")  # R
    
    # CA3: Customs Function Challenges Grid
    ca3_challenges = models.JSONField(default=dict, help_text="CA3: Customs function challenges grid data")  # R
    
    # CA4: Process Effectiveness Grid
    ca4_effectiveness = models.JSONField(default=dict, help_text="CA4: Process effectiveness grid data")  # R
    
    # CA5: Policy Impact
    ca5_policy_impact = models.CharField(max_length=30, help_text="CA5: Policy impact rating")  # R
    
    # CA6: Combined Challenge & Improvement
    ca6_biggest_challenge = models.CharField(max_length=50, help_text="CA6: Biggest operational challenge")  # R
    ca6_improvement = models.TextField(blank=True, help_text="CA6: Specific improvement needed")  # O - CORRECT

    # Cross-System Perspectives (XS1-XS3)
    cross_system_answers = models.JSONField(default=dict, blank=True)  # O - CORRECT

    # Final Remarks
    final_remarks = models.TextField(blank=True)  # O - CORRECT
    
    # Survey Feedback
    survey_feedback = models.TextField(
        blank=True, 
        help_text="Feedback provided by the respondent on the survey questionnaire itself."
    )  # O - CORRECT

    # Metadata
    submission_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.full_name} - {self.reference_number}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"FBR{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    # Display Methods for G1-G5
    def get_g1_policy_impact_display(self):
        mapping = {
            'very_positive': 'Very Positive', 'positive': 'Positive', 'neutral': 'Neutral',
            'negative': 'Negative', 'very_negative': 'Very Negative', 'na': 'N/A', 'dont_know': 'Don\'t Know'
        }
        return {k: mapping.get(v, v) for k, v in (self.g1_policy_impact or {}).items()}

    def get_g2_system_impact_display(self):
        mapping = {
            'very_positive': 'Very Positive', 'positive': 'Positive', 'neutral': 'Neutral',
            'negative': 'Negative', 'very_negative': 'Very Negative', 'na': 'N/A', 'dont_know': 'Don\'t Know'
        }
        return {k: mapping.get(v, v) for k, v in (self.g2_system_impact or {}).items()}

    def get_g3_technical_issues_display(self):
        mapping = {
            'daily': 'Daily', 'weekly': 'Weekly', 'monthly': 'Monthly', 'rarely': 'Rarely',
            'never': 'Never', 'dont_know': 'Don\'t Know'
        }
        return mapping.get(self.g3_technical_issues, self.g3_technical_issues)

    def get_g4_disruption_display(self):
        mapping = {
            'very_significantly': 'Very significantly', 'significantly': 'Significantly',
            'minimally': 'Minimally', 'not_at_all': 'Not at all'
        }
        return mapping.get(self.g4_disruption, self.g4_disruption) if self.g4_disruption else ''

    def get_g5_digital_literacy_display(self):
        mapping = {
            'very_significantly': 'Very significantly', 'significantly': 'Significantly', 'neutral': 'Neutral',
            'minimally': 'Minimally', 'not_at_all': 'Not at all', 'dont_know': 'Don\'t Know'
        }
        return mapping.get(self.g5_digital_literacy, self.g5_digital_literacy)

    # Display Methods for Legal Practitioner Questions
    def get_lp1_digital_support_display(self):
        mapping = {
            'great_extent': 'To a great extent',
            'considerable_extent': 'To a considerable extent', 
            'moderate_extent': 'To a moderate extent',
            'slight_extent': 'To a slight extent',
            'not_at_all': 'Not at all'
        }
        return mapping.get(self.lp1_digital_support, self.lp1_digital_support)

    def get_lp2_challenges_display(self):
        """Format LP2 grid data for display"""
        if not self.lp2_challenges:
            return {}
        
        function_mapping = {
            'appeals_commissioner': 'Appeal filings before Commissioner (S.127)',
            'appellate_tribunal': 'Appellate Tribunal representations (S.132)',
            'high_court': 'High Court/Supreme Court references',
            'audit_responses': 'Audit responses & compliance (S.177)',
            'show_cause': 'Show cause notice responses (S.122)'
        }
        
        level_mapping = {
            'no_challenge': 'No Challenge',
            'minor_challenge': 'Minor Challenge', 
            'moderate_challenge': 'Moderate Challenge',
            'major_challenge': 'Major Challenge',
            'dont_perform': "Don't Perform"
        }
        
        return {
            function_mapping.get(func, func): level_mapping.get(level, level)
            for func, level in self.lp2_challenges.items()
        }

    def get_lp3_challenges_display(self):
        """Format LP3 grid data for display"""
        if not self.lp3_challenges:
            return {}
        
        function_mapping = {
            'return_filing': 'Return filing & compliance (S.114)',
            'amendments': 'Return amendments & rectifications',
            'withholding': 'Withholding statements & compliance', 
            'risk_assessment': 'Risk assessment procedures (S.122A)',
            'tax_planning': 'Tax planning advisory services'
        }
        
        level_mapping = {
            'no_challenge': 'No Challenge',
            'minor_challenge': 'Minor Challenge',
            'moderate_challenge': 'Moderate Challenge',
            'major_challenge': 'Major Challenge', 
            'dont_perform': "Don't Perform"
        }
        
        return {
            function_mapping.get(func, func): level_mapping.get(level, level)
            for func, level in self.lp3_challenges.items()
        }

    def get_lp4_challenges_display(self):
        """Format LP4 grid data for display"""
        if not self.lp4_challenges:
            return {}
        
        function_mapping = {
            'adr': 'Alternate Dispute Resolution (S.134A)',
            'settlement': 'Settlement procedures',
            'epayments': 'e-Payments & refund processing',
            'cpr_corrections': 'CPR corrections',
            'correspondence': 'FBR correspondence management'
        }
        
        level_mapping = {
            'no_challenge': 'No Challenge',
            'minor_challenge': 'Minor Challenge',
            'moderate_challenge': 'Moderate Challenge',
            'major_challenge': 'Major Challenge',
            'dont_perform': "Don't Perform"
        }
        
        return {
            function_mapping.get(func, func): level_mapping.get(level, level)
            for func, level in self.lp4_challenges.items()
        }

    def get_lp5_tax_types_display(self):
        """Format LP5 tax-type data for display"""
        if not self.lp5_tax_types:
            return {}
        
        function_mapping = {
            'appeals_commissioner': 'Appeal filings before Commissioner',
            'appellate_tribunal': 'Appellate Tribunal representations',
            'high_court': 'High Court/Supreme Court references',
            'audit_responses': 'Audit responses & compliance',
            'show_cause': 'Show cause notice responses',
            'return_filing': 'Return filing & compliance',
            'amendments': 'Return amendments & rectifications',
            'withholding': 'Withholding statements & compliance',
            'risk_assessment': 'Risk assessment procedures',
            'tax_planning': 'Tax planning advisory services',
            'adr': 'Alternate Dispute Resolution',
            'settlement': 'Settlement procedures',
            'epayments': 'e-Payments & refund processing',
            'cpr_corrections': 'CPR corrections',
            'correspondence': 'FBR correspondence management'
        }
        
        return {
            function_mapping.get(func, func): {
                'income_tax': data.get('income_tax', False),
                'sales_tax': data.get('sales_tax', False)
            }
            for func, data in self.lp5_tax_types.items()
        }

    # Display Methods for Customs Agent Questions
    def get_ca1_training_display(self):
        mapping = {
            'effective_both': 'Yes, effective training on both WeBOC and PSW',
            'needs_improvement': 'Yes, but training needs improvement',
            'no_training': 'No formal training received',
            'not_applicable': 'Not applicable'
        }
        return mapping.get(self.ca1_training, self.ca1_training)

    def get_ca2_system_integration_display(self):
        mapping = {
            'very_well': 'Very well integrated',
            'well': 'Well integrated',
            'moderately': 'Moderately integrated',
            'poorly': 'Poorly integrated',
            'not_integrated': 'Not integrated'
        }
        return mapping.get(self.ca2_system_integration, self.ca2_system_integration)

    def get_ca3_challenges_display(self):
        """Format CA3 grid data for display"""
        if not self.ca3_challenges:
            return {}
        
        function_mapping = {
            'goods_declaration': 'Goods Declaration (S.79)',
            'duty_assessment': 'Duty Assessment (S.81)',
            'cargo_examination': 'Cargo Examination (S.26)',
            'document_processing': 'Document Processing (S.79(2))',
            'transit_warehousing': 'Transit/Warehousing (S.13, S.15)',
            'record_keeping': 'Record Keeping (S.155(6))',
            'audit_compliance': 'Audit Compliance (S.26A)',
            'license_compliance': 'License Compliance (S.155(4))'
        }
        
        level_mapping = {
            'no_challenge': 'No Challenge',
            'minor_challenge': 'Minor',
            'moderate_challenge': 'Moderate', 
            'major_challenge': 'Major',
            'not_applicable': 'N/A'
        }
        
        return {
            function_mapping.get(func, func): level_mapping.get(level, level)
            for func, level in self.ca3_challenges.items()
        }

    def get_ca4_effectiveness_display(self):
        """Format CA4 grid data for display"""
        if not self.ca4_effectiveness:
            return {}
        
        process_mapping = {
            'duty_assessment': 'Duty assessment',
            'cargo_examination': 'Cargo examination',
            'system_reliability': 'System reliability',
            'client_representation': 'Client representation'
        }
        
        level_mapping = {
            'very_effective': 'Very Effective',
            'effective': 'Effective',
            'neutral': 'Neutral',
            'ineffective': 'Ineffective',
            'very_ineffective': 'Very Ineffective'
        }
        
        return {
            process_mapping.get(process, process): level_mapping.get(level, level)
            for process, level in self.ca4_effectiveness.items()
        }

    def get_ca5_policy_impact_display(self):
        mapping = {
            'very_positively': 'Very positively',
            'positively': 'Positively',
            'neutral': 'Neutral', 
            'negatively': 'Negatively',
            'very_negatively': 'Very negatively'
        }
        return mapping.get(self.ca5_policy_impact, self.ca5_policy_impact)

    def get_ca6_biggest_challenge_display(self):
        mapping = {
            'system_issues': 'System reliability and performance issues',
            'policy_changes': 'Frequent policy or procedural changes',
            'assessment_unpredictability': 'Unpredictable assessment outcomes',
            'documentation_delays': 'Documentation processing delays',
            'cargo_bottlenecks': 'Cargo examination bottlenecks',
            'compliance_burden': 'Compliance and record-keeping burden',
            'coordination_issues': 'Inter-agency coordination challenges',
            'training_gaps': 'Training and knowledge gaps'
        }
        return mapping.get(self.ca6_biggest_challenge, self.ca6_biggest_challenge)

    # Display Method for Cross-System Questions
    def get_cross_system_answers_display(self):
        """Format Cross-System grid data for display (XS1 and XS2)"""
        cross_data = self.get_cross_system_data()
        if not cross_data or cross_data.get('skipped'):
            return {'status': 'Section Skipped'}
            
        level_mapping = {
            'always': 'Always / Almost Always',
            'often': 'Often',
            'sometimes': 'Sometimes',
            'rarely': 'Rarely',
            'never': 'Never / Almost Never',
            'not_applicable': 'Not Applicable / Don\'t know'
        }
        
        display_data = {}
        
        # XS1: Data Discrepancy/Reconciliation
        xs1_key = 'xs1_data_discrepancy'
        if xs1_key in cross_data:
            display_data['XS1. Data Discrepancy/Reconciliation'] = level_mapping.get(cross_data[xs1_key], cross_data[xs1_key])
            
        # XS2: Unified Legal/Policy Interpretation
        xs2_key = 'xs2_policy_consistency'
        if xs2_key in cross_data:
            display_data['XS2. Policy Consistency'] = level_mapping.get(cross_data[xs2_key], cross_data[xs2_key])
            
        return display_data

    # Utility Methods
    def get_cross_system_data(self):
        if isinstance(self.cross_system_answers, dict):
            return self.cross_system_answers
        try:
            return json.loads(self.cross_system_answers) if self.cross_system_answers else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def has_legal_answers(self):
        """Check if legal practitioner questions were answered"""
        return self.professional_role in ['legal', 'both'] and any([
            self.lp1_digital_support,
            self.lp2_challenges,
            self.lp3_challenges,
            self.lp4_challenges,
            self.lp5_tax_types,
            self.lp6_priority_improvement
        ])

    def has_customs_answers(self):
        """Check if customs agent questions were answered"""
        return self.professional_role in ['customs', 'both'] and any([
            self.ca1_training,
            self.ca2_system_integration,
            self.ca3_challenges,
            self.ca4_effectiveness,
            self.ca5_policy_impact,
            self.ca6_biggest_challenge,
            self.ca6_improvement
        ])

    def has_cross_system_answers(self):
        """Check if cross-system perspectives were provided"""
        cross_data = self.get_cross_system_data()
        # Checks if data exists and is not explicitly marked as skipped
        return bool(cross_data and not cross_data.get('skipped'))

    class Meta:
        verbose_name = "Survey Response"
        verbose_name_plural = "Survey Responses"
        ordering = ['-submission_date']