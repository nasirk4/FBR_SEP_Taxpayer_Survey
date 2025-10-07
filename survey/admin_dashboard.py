# /home/nasirk4/FBR_SEP_Taxpayer_Survey/survey/admin_dashboard.py
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db import connection
from plotly.offline import plot

logger = logging.getLogger(__name__)

class SurveyAnalytics:
    """Handles analytics for survey data, including quotas, statistics, and visualizations."""
    def __init__(self):
        """Initialize with empty DataFrame and quota targets."""
        self.df = None
        self.quota_targets = {
            'balochistan': {'legal': 6, 'customs': 6},
            'ict': {'legal': 6, 'customs': 6},
            'kpk': {'legal': 6, 'customs': 6},
            'punjab': {'legal': 6, 'customs': 6},
            'sindh': {'legal': 6, 'customs': 6}
        }

    def load_data(self):
        """Load survey data from the database using a simplified SQL query.

        Returns:
            bool: True if data is loaded successfully, False otherwise.
        """
        try:
            query = """
            SELECT
                id, full_name, email, district, mobile, professional_role, province,
                experience_legal, experience_customs, g1_iris_rating, g2_system_weaknesses,
                g2a_weaknesses_details, g3_iris_limitations, g4_challenged_groups,
                g4_other_text, g5_clients_change, g6_fee_change, g7_digital_literacy_impact,
                g8_regional_differences, g8_regional_differences_text,
                lp1_technical_issues, lp2_common_problems, lp2_other_text,
                lp3_improvement_areas, lp3_other_text, lp4_procedures, lp4_other_procedure,
                lp4_other_sales, lp4_other_income, lp4_other_comment,
                lp5_representation_challenges, lp5_other_text, lp6_filing_efficiency,
                lp7_case_tracking, lp8_notice_communication, lp9_law_accessibility,
                lp10_law_change_impact, lp11_adr_effectiveness, lp12_dispute_transparency,
                lp13_overall_satisfaction, lp13_feedback,
                ca1_training_received, ca1a_training_usefulness, ca2_psw_weboc_integration,
                ca3_procedure_challenges, ca3_other_text, ca4_duty_assessment, ca5_psw_vs_weboc,
                ca6_cargo_efficiency, ca7_system_reliability, ca8_policy_impact,
                ca9_operational_challenges, ca9_other_text, ca9_feedback,
                cross_system_answers, final_remarks, submission_date, reference_number
            FROM survey_surveyresponse
            ORDER BY submission_date DESC
            """
            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data = cursor.fetchall()

            self.df = pd.DataFrame(data, columns=columns)

            # Parse JSON fields
            json_columns = ['g4_challenged_groups', 'lp2_common_problems', 'lp3_improvement_areas',
                           'lp4_procedures', 'lp5_representation_challenges', 'ca3_procedure_challenges',
                           'ca9_operational_challenges', 'cross_system_answers']

            for col in json_columns:
                if col in self.df.columns and self.df[col].notna().any():
                    self.df[col] = self.df[col].apply(
                        lambda x: json.loads(x) if x and x not in ['[]', '{}', ''] else []
                    )

            logger.info(f"Loaded {len(self.df)} survey responses")
            return True

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def get_quota_status(self):
        """Calculate the current status against sampling quotas.

        Returns:
            dict: Quota status by province and role.
        """
        if self.df is None and not self.load_data():
            return {}

        quota_status = {}
        total_achieved = 0
        total_target = 0

        for province, targets in self.quota_targets.items():
            quota_status[province] = {}
            province_df = self.df[self.df['province'] == province]

            for role, target in targets.items():
                achieved = len(province_df[province_df['professional_role'] == role])
                percentage = (achieved / target * 100) if target > 0 else 0
                status = "Completed" if achieved >= target else "In Progress"

                quota_status[province][role] = {
                    'achieved': achieved,
                    'target': target,
                    'percentage': round(percentage, 1),
                    'status': status,
                    'remaining': max(0, target - achieved)
                }

                total_achieved += achieved
                total_target += target

        quota_status['total'] = {
            'achieved': total_achieved,
            'target': total_target,
            'percentage': round((total_achieved / total_target * 100), 1) if total_target > 0 else 0
        }

        return quota_status

    def get_summary_stats(self):
        """Generate overall summary statistics for the survey.

        Returns:
            dict: Summary statistics including response counts and distributions.
        """
        if self.df is None and not self.load_data():
            return {}

        total_responses = len(self.df)
        role_distribution = self.df['professional_role'].value_counts().to_dict()
        province_distribution = self.df['province'].value_counts().to_dict()
        district_distribution = self.df['district'].value_counts().head(10).to_dict()
        
        # Convert datetime to string for JSON serialization
        latest_submission = self.df['submission_date'].max() if 'submission_date' in self.df.columns else "N/A"
        earliest_submission = self.df['submission_date'].min() if 'submission_date' in self.df.columns else "N/A"
        
        if isinstance(latest_submission, pd.Timestamp):
            latest_submission = latest_submission.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(earliest_submission, pd.Timestamp):
            earliest_submission = earliest_submission.strftime('%Y-%m-%d %H:%M:%S')

        return {
            'total_responses': total_responses,
            'role_distribution': role_distribution,
            'province_distribution': province_distribution,
            'district_distribution': district_distribution,
            'latest_submission': latest_submission,
            'earliest_submission': earliest_submission
        }

    def get_response_timeline(self):
        """Get response timeline for the last 7 days.

        Returns:
            dict: Daily response counts for the past week.
        """
        if self.df is None or 'submission_date' not in self.df.columns:
            return {}

        self.df['submission_date'] = pd.to_datetime(self.df['submission_date'])
        last_7_days = datetime.now() - timedelta(days=7)
        recent_df = self.df[self.df['submission_date'] >= last_7_days]
        timeline = recent_df.groupby(recent_df['submission_date'].dt.date).size()
        
        # Convert datetime.date to string for JSON serialization
        return {str(date): int(count) for date, count in timeline.to_dict().items()}

    def get_generic_questions_analysis(self):
        """Analyze responses to generic questions (G1-G8).

        Returns:
            dict: Analysis of generic question responses.
        """
        if self.df is None and not self.load_data():
            return {}

        analysis = {}
        if 'g1_iris_rating' in self.df.columns:
            analysis['g1'] = self.df['g1_iris_rating'].value_counts().to_dict()
        if 'g2_system_weaknesses' in self.df.columns:
            analysis['g2'] = self.df['g2_system_weaknesses'].value_counts().to_dict()
        if 'g4_challenged_groups' in self.df.columns:
            all_groups = []
            for groups in self.df['g4_challenged_groups']:
                if isinstance(groups, list):
                    all_groups.extend(groups)
            from collections import Counter
            analysis['g4'] = dict(Counter(all_groups))
        if 'g5_clients_change' in self.df.columns:
            analysis['g5'] = self.df['g5_clients_change'].value_counts().to_dict()

        return analysis

    def get_qualitative_insights(self):
        """Extract insights from qualitative responses.

        Returns:
            dict: Qualitative insights from remarks, improvements, and challenges.
        """
        if self.df is None and not self.load_data():
            return {}

        insights = {}
        if 'final_remarks' in self.df.columns:
            remarks = self.df[
                self.df['final_remarks'].notna() & (self.df['final_remarks'] != '')
            ]['final_remarks'].tolist()
            insights['final_remarks'] = remarks[:10]
        
        # Use correct column names from your model
        if 'lp3_improvement_areas' in self.df.columns:
            improvements = self.df[
                self.df['lp3_improvement_areas'].notna() &
                (self.df['lp3_improvement_areas'] != '')
            ]['lp3_improvement_areas'].tolist()
            insights['improvements'] = improvements[:10]
        
        # Use correct column names from your model  
        if 'ca3_procedure_challenges' in self.df.columns:
            challenges = self.df[
                self.df['ca3_procedure_challenges'].notna() &
                (self.df['ca3_procedure_challenges'] != '')
            ]['ca3_procedure_challenges'].tolist()
            insights['challenges'] = challenges[:10]

        return insights

    def create_quota_chart(self):
        """Create a bar chart for quota status visualization.

        Returns:
            str: HTML div for Plotly chart.
        """
        quota_status = self.get_quota_status()
        provinces = []
        legal_achieved = []
        legal_target = []
        customs_achieved = []
        customs_target = []

        for province, roles in quota_status.items():
            if province == 'total':
                continue
            provinces.append(province.upper())
            legal_achieved.append(roles['legal']['achieved'])
            legal_target.append(roles['legal']['target'])
            customs_achieved.append(roles['customs']['achieved'])
            customs_target.append(roles['customs']['target'])

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Legal Target', x=provinces, y=legal_target, marker_color='lightblue'))
        fig.add_trace(go.Bar(name='Legal Achieved', x=provinces, y=legal_achieved, marker_color='blue'))
        fig.add_trace(go.Bar(name='Customs Target', x=provinces, y=customs_target, marker_color='lightgreen'))
        fig.add_trace(go.Bar(name='Customs Achieved', x=provinces, y=customs_achieved, marker_color='green'))
        fig.update_layout(
            title='Sampling Quota Status by Province',
            barmode='group',
            xaxis_title='Province',
            yaxis_title='Number of Responses'
        )

        return plot(fig, output_type='div')

    def get_cross_tabulations(self):
        """Generate cross-tabulations for analysis.

        Returns:
            dict: Cross-tabulations for role, IRIS rating, weaknesses, and experience.
        """
        if self.df is None and not self.load_data():
            return {}

        cross_tabs = {}
        if 'professional_role' in self.df.columns and 'province' in self.df.columns:
            role_province_ct = pd.crosstab(self.df['professional_role'], self.df['province'], margins=True)
            cross_tabs['role_by_province'] = role_province_ct.to_dict()
        if 'g1_iris_rating' in self.df.columns and 'professional_role' in self.df.columns:
            iris_role_ct = pd.crosstab(self.df['g1_iris_rating'], self.df['professional_role'], margins=True)
            cross_tabs['iris_by_role'] = iris_role_ct.to_dict()
        if 'g2_system_weaknesses' in self.df.columns and 'province' in self.df.columns:
            weaknesses_province_ct = pd.crosstab(self.df['g2_system_weaknesses'], self.df['province'], margins=True)
            cross_tabs['weaknesses_by_province'] = weaknesses_province_ct.to_dict()
        if 'experience_legal' in self.df.columns and 'professional_role' in self.df.columns:
            # Map categorical strings to numeric values
            experience_map = {
                '1-5 years': 3,  # Midpoint of 1-5
                '6-10 years': 8,  # Midpoint of 6-10
                'More than 10 years': 15,  # Representative value
                '10+ years': 15  # Handle potential variations
            }
            self.df['experience_legal_numeric'] = self.df['experience_legal'].map(experience_map).fillna(0)
            self.df['experience_category'] = pd.cut(
                self.df['experience_legal_numeric'],
                bins=[0, 5, 10, 100],
                labels=['1-5 years', '6-10 years', 'More than 10 years'],
                include_lowest=True
            )
            exp_role_ct = pd.crosstab(self.df['experience_category'], self.df['professional_role'], margins=True)
            cross_tabs['experience_by_role'] = exp_role_ct.to_dict()
        if 'experience_customs' in self.df.columns and 'professional_role' in self.df.columns:
            # Apply same mapping for experience_customs
            self.df['experience_customs_numeric'] = self.df['experience_customs'].map(experience_map).fillna(0)
            self.df['experience_customs_category'] = pd.cut(
                self.df['experience_customs_numeric'],
                bins=[0, 5, 10, 100],
                labels=['1-5 years', '6-10 years', 'More than 10 years'],
                include_lowest=True
            )
            exp_customs_ct = pd.crosstab(self.df['experience_customs_category'], self.df['professional_role'], margins=True)
            cross_tabs['experience_customs_by_role'] = exp_customs_ct.to_dict()

        return cross_tabs

    def get_sql_based_cross_tabs(self):
        """Generate cross-tabulations using raw SQL for efficiency.

        Returns:
            dict: SQL-based cross-tabulations for role and IRIS rating by province.
        """
        try:
            cross_tabs = {}
            role_province_query = """
            SELECT
                professional_role,
                province,
                COUNT(*) as count
            FROM survey_surveyresponse
            WHERE professional_role IS NOT NULL AND province IS NOT NULL
            GROUP BY professional_role, province
            ORDER BY professional_role, province
            """
            with connection.cursor() as cursor:
                cursor.execute(role_province_query)
                results = cursor.fetchall()
            role_province_data = {}
            for role, province, count in results:
                if role not in role_province_data:
                    role_province_data[role] = {}
                role_province_data[role][province] = count
            cross_tabs['sql_role_by_province'] = role_province_data

            iris_province_query = """
            SELECT
                g1_iris_rating,
                province,
                COUNT(*) as count
            FROM survey_surveyresponse
            WHERE g1_iris_rating IS NOT NULL AND province IS NOT NULL
            GROUP BY g1_iris_rating, province
            ORDER BY g1_iris_rating, province
            """
            with connection.cursor() as cursor:
                cursor.execute(iris_province_query)
                results = cursor.fetchall()
            iris_province_data = {}
            for rating, province, count in results:
                if rating not in iris_province_data:
                    iris_province_data[rating] = {}
                iris_province_data[rating][province] = count
            cross_tabs['sql_iris_by_province'] = iris_province_data

            return cross_tabs

        except Exception as e:
            logger.error(f"Error in SQL cross-tabs: {e}")
            return {}

    def create_cross_tab_charts(self):
        """Create visualizations for cross-tabulations.

        Returns:
            dict: HTML divs for Plotly charts.
        """
        cross_tabs = self.get_cross_tabulations()
        charts = {}
        if 'role_by_province' in cross_tabs:
            df_role_province = pd.DataFrame(cross_tabs['role_by_province'])
            fig = px.imshow(
                df_role_province.iloc[:-1, :-1],
                title="Professional Role Distribution by Province",
                labels=dict(x="Province", y="Professional Role", color="Count"),
                aspect="auto"
            )
            charts['role_province_heatmap'] = plot(fig, output_type='div')
        if 'iris_by_role' in cross_tabs:
            df_iris_role = pd.DataFrame(cross_tabs['iris_by_role'])
            fig = px.bar(
                df_iris_role.iloc[:-1],
                title="IRIS Rating Distribution by Professional Role",
                barmode='group'
            )
            charts['iris_role_barchart'] = plot(fig, output_type='div')

        return charts

    def export_to_excel(self):
        """Export survey data to Excel for advanced analysis.

        Returns:
            str: Path to the generated Excel file or None if failed.
        """
        if self.df is None and not self.load_data():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fbr_survey_export_{timestamp}.xlsx"
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                self.df.to_excel(writer, sheet_name='Raw Data', index=False)
                summary_data = []
                stats = self.get_summary_stats()
                for key, value in stats.items():
                    if isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            summary_data.append([f"{key}_{subkey}", subvalue])
                    else:
                        summary_data.append([key, value])
                summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                quota_data = []
                quota_status = self.get_quota_status()
                for province, roles in quota_status.items():
                    if province == 'total':
                        quota_data.append(['TOTAL', 'All Roles', roles['achieved'], roles['target'], f"{roles['percentage']}%"])
                    else:
                        for role, status in roles.items():
                            quota_data.append([province.upper(), role.title(), status['achieved'], status['target'], f"{status['percentage']}%"])
                quota_df = pd.DataFrame(quota_data, columns=['Province', 'Role', 'Achieved', 'Target', 'Percentage'])
                quota_df.to_excel(writer, sheet_name='Quota Status', index=False)
                generic_analysis = self.get_generic_questions_analysis()
                generic_data = []
                for question, results in generic_analysis.items():
                    if isinstance(results, dict):
                        for option, count in results.items():
                            generic_data.append([question, option, count])
                    else:
                        generic_data.append([question, 'N/A', results])
                generic_df = pd.DataFrame(generic_data, columns=['Question', 'Option', 'Count'])
                generic_df.to_excel(writer, sheet_name='Generic Questions', index=False)

            return filename

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None

    def export_to_spss_format(self):
        """Export data in a format compatible with SPSS.

        Returns:
            str: Path to the generated CSV file or None if failed.
        """
        if self.df is None and not self.load_data():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fbr_survey_spss_{timestamp}.csv"
            spss_df = self.df.copy()
            # Use correct JSON column names from your model
            json_columns = ['g4_challenged_groups', 'lp2_common_problems', 'lp3_improvement_areas', 
                           'lp4_procedures', 'lp5_representation_challenges', 'ca3_procedure_challenges',
                           'ca9_operational_challenges', 'cross_system_answers']
            for col in json_columns:
                if col in spss_df.columns:
                    spss_df[col] = spss_df[col].apply(lambda x: str(x) if x else '')
            spss_df.to_csv(filename, index=False, encoding='utf-8')
            return filename

        except Exception as e:
            logger.error(f"Error exporting to SPSS format: {e}")
            return None

    def get_advanced_analytics(self):
        """Generate advanced analytics with multi-dimensional cross-tabulations.

        Returns:
            dict: Nested dictionary with role, province, and IRIS rating analytics.
        """
        try:
            advanced_query = """
            SELECT
                professional_role,
                province,
                g1_iris_rating,
                COUNT(*) as response_count
            FROM survey_surveyresponse
            WHERE professional_role IS NOT NULL
              AND province IS NOT NULL
              AND g1_iris_rating IS NOT NULL
            GROUP BY professional_role, province, g1_iris_rating
            ORDER BY professional_role, province, g1_iris_rating
            """
            with connection.cursor() as cursor:
                cursor.execute(advanced_query)
                results = cursor.fetchall()

            advanced_data = {}
            for role, province, iris_rating, count in results:
                if role not in advanced_data:
                    advanced_data[role] = {}
                if province not in advanced_data[role]:
                    advanced_data[role][province] = {}
                advanced_data[role][province][iris_rating] = {
                    'count': count
                }

            return advanced_data

        except Exception as e:
            logger.error(f"Error in advanced analytics: {e}")
            return {}