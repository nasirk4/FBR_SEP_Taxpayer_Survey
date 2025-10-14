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
        # Field mappings validated against data
        self.field_mappings = {
            'g1_policy_impact_keys': ['service_delivery', 'compliance_burden', 'dispute_resolution', 'client_satisfaction'],
            'g2_system_impact_keys': ['workflow_efficiency', 'data_accuracy', 'system_reliability', 'user_experience'],
            'experience_categories': {
                'Less than 1 year': (0, 1),
                '1-5 years': (1, 5),
                '6-10 years': (6, 10),
                'More than 10 years': (11, 50)
            },
            'sentiment_scores': {
                'very_positive': 2, 'positive': 1, 'neutral': 0,
                'negative': -1, 'very_negative': -2, 'n/a': 0, 'dont_know': 0
            }
        }
        # Cache for JSON key validation
        self.json_keys_cache = {'g1_policy_impact': set(), 'g2_system_impact': set()}

    def load_data(self, force_reload=False, columns=None):
        """Load survey data from the database with selective column loading.

        Args:
            force_reload (bool): If True, reload data even if already loaded.
            columns (list): Optional list of columns to load (default: all).

        Returns:
            bool: True if data is loaded successfully, False otherwise.
        """
        if self.df is not None and not force_reload:
            return True

        try:
            all_columns = [
                'id', 'full_name', 'email', 'district', 'mobile', 'professional_role', 'province',
                'experience_legal', 'experience_customs', 'practice_areas', 'kii_consent',
                'g1_policy_impact', 'g2_system_impact', 'g3_technical_issues', 'g4_disruption',
                'g5_digital_literacy', 'lp1_digital_support', 'lp2_challenges', 'lp3_challenges',
                'lp4_challenges', 'lp5_tax_types', 'lp5_visible', 'lp6_priority_improvement',
                'ca1_training', 'ca2_system_integration', 'ca3_challenges', 'ca4_effectiveness',
                'ca5_policy_impact', 'ca6_biggest_challenge', 'ca6_improvement',
                'cross_system_answers', 'final_remarks', 'survey_feedback', 'submission_date',
                'reference_number'
            ]
            selected_columns = columns if columns else all_columns
            query = f"SELECT {', '.join(selected_columns)} FROM survey_surveyresponse ORDER BY submission_date DESC"

            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data = cursor.fetchall()

            self.df = pd.DataFrame(data, columns=columns)
            
            # Enhanced data processing
            self._enhance_data_processing()
            
            logger.info(f"Successfully loaded {len(self.df)} survey responses with {len(self.df.columns)} fields")
            return True

        except Exception as e:
            logger.error(f"Error loading survey data: {str(e)}", exc_info=True)
            return False

    def _enhance_data_processing(self):
        """Enhanced data processing with better NULL handling and type conversions."""
        if self.df is None:
            return

        # Parse JSON fields and update key cache
        json_columns = [
            'g1_policy_impact', 'g2_system_impact', 'lp2_challenges', 'lp3_challenges',
            'lp4_challenges', 'lp5_tax_types', 'ca3_challenges', 'ca4_effectiveness',
            'cross_system_answers'
        ]

        for col in json_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(
                    lambda x: self._safe_json_loads(x, col) if pd.notna(x) and x not in ['[]', '{}', ''] else {}
                )

        # Convert datetime with timezone handling
        if 'submission_date' in self.df.columns:
            self.df['submission_date'] = pd.to_datetime(self.df['submission_date'], errors='coerce')
            
        # Create derived columns
        self._create_derived_columns()

    def _safe_json_loads(self, json_str, column):
        """Safely parse JSON strings and update key cache."""
        if not json_str or not isinstance(json_str, str):
            return {}
        
        try:
            data = json.loads(json_str)
            if isinstance(data, dict) and column in self.json_keys_cache:
                self.json_keys_cache[column].update(data.keys())
            return data
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse JSON in {column}: {json_str[:100]}... Error: {e}")
            return {}

    def _create_derived_columns(self):
        """Create derived columns for enhanced analysis."""
        # Role categorization
        if 'professional_role' in self.df.columns:
            self.df['role_category'] = self.df['professional_role'].map({
                'legal': 'Legal Only',
                'customs': 'Customs Only',
                'both': 'Dual Role'
            }).fillna('Unknown')
            
        # Experience numeric mapping
        experience_map = {k: (v[0] + v[1]) / 2 for k, v in self.field_mappings['experience_categories'].items()}
        
        if 'experience_legal' in self.df.columns:
            self.df['experience_legal_numeric'] = (
                self.df['experience_legal']
                .map(experience_map)
                .fillna(0)
            )
            
        if 'experience_customs' in self.df.columns:
            self.df['experience_customs_numeric'] = (
                self.df['experience_customs']
                .map(experience_map)
                .fillna(0)
            )

    def get_quota_status(self):
        """Calculate the current status against sampling quotas with enhanced reporting.

        Returns:
            dict: Quota status by province and role with detailed metrics.
        """
        if self.df is None and not self.load_data():
            return {}

        quota_status = {}
        total_achieved = 0
        total_target = 0
        completion_rates = []

        for province, targets in self.quota_targets.items():
            quota_status[province] = {}
            province_df = self.df[self.df['province'] == province]

            for role, target in targets.items():
                if role == 'legal':
                    achieved = len(province_df[province_df['professional_role'].isin(['legal', 'both'])])
                elif role == 'customs':
                    achieved = len(province_df[province_df['professional_role'].isin(['customs', 'both'])])
                else:
                    achieved = len(province_df[province_df['professional_role'] == role])
                    
                percentage = (achieved / target * 100) if target > 0 else 0
                status = "Completed" if achieved >= target else "In Progress"
                remaining = max(0, target - achieved)
                days_estimate = remaining / 2 if remaining > 0 else 0

                quota_status[province][role] = {
                    'achieved': achieved,
                    'target': target,
                    'percentage': round(percentage, 1),
                    'status': status,
                    'remaining': remaining,
                    'days_estimate': round(days_estimate, 1),
                    'completion_risk': 'High' if percentage < 50 else 'Medium' if percentage < 80 else 'Low'
                }

                total_achieved += achieved
                total_target += target
                completion_rates.append(percentage)

        overall_completion = round((total_achieved / total_target * 100), 1) if total_target > 0 else 0
        avg_completion = round(sum(completion_rates) / len(completion_rates), 1) if completion_rates else 0
        
        quota_status['total'] = {
            'achieved': total_achieved,
            'target': total_target,
            'percentage': overall_completion,
            'average_province_completion': avg_completion,
            'remaining_total': max(0, total_target - total_achieved),
            'completion_status': 'On Track' if overall_completion >= 80 else 'Needs Attention'
        }

        return quota_status

    def get_summary_stats(self):
        """Generate comprehensive summary statistics for the survey.

        Returns:
            dict: Enhanced summary statistics with additional metrics.
        """
        if self.df is None and not self.load_data():
            return {}

        total_responses = len(self.df)
        role_distribution = self.df['professional_role'].value_counts().to_dict()
        province_distribution = self.df['province'].value_counts().to_dict()
        district_distribution = self.df['district'].value_counts().head(10).to_dict()
        
        response_dates = pd.to_datetime(self.df['submission_date'])
        daily_responses = response_dates.dt.date.value_counts()
        avg_daily_responses = round(daily_responses.mean(), 1) if not daily_responses.empty else 0
        max_daily_responses = daily_responses.max() if not daily_responses.empty else 0

        kii_consent_rate = round(
            (self.df['kii_consent'] == 'yes').sum() / total_responses * 100, 1
        ) if total_responses > 0 else 0

        completeness_metrics = {}
        key_columns = ['professional_role', 'province', 'g1_policy_impact', 'g2_system_impact']
        for column in key_columns:
            if column in self.df.columns:
                completeness = round(self.df[column].notna().sum() / total_responses * 100, 1)
                completeness_metrics[column] = completeness

        return {
            'total_responses': total_responses,
            'role_distribution': role_distribution,
            'province_distribution': province_distribution,
            'district_distribution': district_distribution,
            'latest_submission': self._format_datetime(self.df['submission_date'].max()),
            'earliest_submission': self._format_datetime(self.df['submission_date'].min()),
            'avg_daily_responses': avg_daily_responses,
            'max_daily_responses': max_daily_responses,
            'kii_consent_rate': kii_consent_rate,
            'data_completeness': completeness_metrics,
            'survey_duration_days': (
                (self.df['submission_date'].max() - self.df['submission_date'].min()).days 
                if len(self.df) > 1 else 0
            )
        }

    def _format_datetime(self, dt):
        """Safely format datetime objects for JSON serialization."""
        if pd.isna(dt):
            return "N/A"
        if isinstance(dt, pd.Timestamp):
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return str(dt)

    def get_response_timeline(self, days=7):
        """Get enhanced response timeline with trend analysis.

        Args:
            days (int): Number of days to include in timeline.

        Returns:
            dict: Daily response counts with trend metrics.
        """
        if self.df is None or 'submission_date' not in self.df.columns:
            return {}

        self.df['submission_date'] = pd.to_datetime(self.df['submission_date'], errors='coerce')
        start_date = datetime.now() - timedelta(days=days)
        recent_df = self.df[self.df['submission_date'] >= start_date]
        
        timeline = recent_df.groupby(recent_df['submission_date'].dt.date).size()
        
        trend = "Stable"
        if len(timeline) >= 2:
            values = list(timeline.values)
            if values[-1] > values[0]:
                trend = "Increasing"
            elif values[-1] < values[0]:
                trend = "Decreasing"

        return {
            'daily_counts': {str(date): int(count) for date, count in timeline.to_dict().items()},
            'total_period_responses': int(timeline.sum()),
            'trend': trend,
            'period_days': days
        }

    def get_generic_questions_analysis(self):
        """Enhanced analysis of responses to generic questions (G1-G5).

        Returns:
            dict: Comprehensive analysis with aggregated metrics.
        """
        if self.df is None and not self.load_data():
            return {}

        analysis = {}
        
        # G1: Policy Impact
        if 'g1_policy_impact' in self.df.columns:
            g1_analysis = self._analyze_json_field(self.df['g1_policy_impact'], 'G1 Policy Impact')
            analysis['g1_policy_impact'] = g1_analysis

        # G2: System Impact
        if 'g2_system_impact' in self.df.columns:
            g2_analysis = self._analyze_json_field(self.df['g2_system_impact'], 'G2 System Impact')
            analysis['g2_system_impact'] = g2_analysis

        # Single-choice questions
        single_choice_fields = {
            'g3_technical_issues': 'G3 Technical Issues',
            'g4_disruption': 'G4 Disruption',
            'g5_digital_literacy': 'G5 Digital Literacy'
        }
        
        for field, label in single_choice_fields.items():
            if field in self.df.columns:
                counts = self.df[field].value_counts().to_dict()
                analysis[field] = {
                    'distribution': counts,
                    'total_responses': sum(counts.values()),
                    'most_common': max(counts.items(), key=lambda x: x[1])[0] if counts else 'N/A',
                    'completion_rate': round(self.df[field].notna().sum() / len(self.df) * 100, 1)
                }

        return analysis

    def _analyze_json_field(self, series, field_name):
        """Enhanced analysis for JSON field data."""
        if series.empty:
            return {}
            
        all_responses = []
        key_distributions = {}
        
        for response in series:
            if isinstance(response, dict) and response:
                all_responses.append(response)
                for key, value in response.items():
                    if key not in key_distributions:
                        key_distributions[key] = {}
                    key_distributions[key][value] = key_distributions[key].get(value, 0) + 1
        
        total_score = 0
        total_rated = 0
        sentiment_scores = self.field_mappings['sentiment_scores']
        
        for response in all_responses:
            for value in response.values():
                if value in sentiment_scores:
                    total_score += sentiment_scores[value]
                    total_rated += 1
        
        avg_sentiment = round(total_score / total_rated, 2) if total_rated > 0 else 0
        
        return {
            'key_distributions': key_distributions,
            'total_responses': len(all_responses),
            'average_sentiment': avg_sentiment,
            'completion_rate': round(len(all_responses) / len(series) * 100, 1),
            'most_common_rating': self._get_most_common_rating(key_distributions)
        }

    def _get_most_common_rating(self, key_distributions):
        """Find the most common rating across all keys in a JSON field."""
        all_ratings = {}
        for key_dist in key_distributions.values():
            for rating, count in key_dist.items():
                all_ratings[rating] = all_ratings.get(rating, 0) + count
        return max(all_ratings.items(), key=lambda x: x[1])[0] if all_ratings else 'N/A'

    def get_qualitative_insights(self, max_responses=10):
        """Enhanced extraction of insights from qualitative responses.

        Args:
            max_responses (int): Maximum number of responses to return per category.

        Returns:
            dict: Qualitative insights with sentiment indicators.
        """
        if self.df is None and not self.load_data():
            return {}

        insights = {}
        qualitative_fields = {
            'final_remarks': 'Final Remarks',
            'lp6_priority_improvement': 'Legal Priority Improvements',
            'ca6_improvement': 'Customs Priority Improvements',
            'survey_feedback': 'Survey Feedback'
        }
        
        for field, label in qualitative_fields.items():
            if field in self.df.columns:
                responses = self.df[
                    self.df[field].notna() & (self.df[field].str.strip() != '')
                ][field].tolist()
                
                insights[field] = {
                    'responses': responses[:max_responses],
                    'total_qualitative': len(responses),
                    'response_rate': round(len(responses) / len(self.df) * 100, 1),
                    'sample_responses': responses[:3]
                }

        return insights

    def create_quota_chart(self):
        """Create enhanced bar chart for quota status visualization.

        Returns:
            str: HTML div for Plotly chart.
        """
        quota_status = self.get_quota_status()
        if not quota_status:
            return "<div>No data available for quota chart</div>"

        provinces = []
        legal_achieved = []
        legal_target = []
        customs_achieved = []
        customs_target = []
        legal_percentages = []
        customs_percentages = []

        for province, roles in quota_status.items():
            if province == 'total':
                continue
            provinces.append(province.upper())
            legal_achieved.append(roles['legal']['achieved'])
            legal_target.append(roles['legal']['target'])
            customs_achieved.append(roles['customs']['achieved'])
            customs_target.append(roles['customs']['target'])
            legal_percentages.append(f"{roles['legal']['percentage']}%")
            customs_percentages.append(f"{roles['customs']['percentage']}%")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Legal Target', x=provinces, y=legal_target, marker_color='lightblue', opacity=0.6
        ))
        fig.add_trace(go.Bar(
            name='Customs Target', x=provinces, y=customs_target, marker_color='lightgreen', opacity=0.6
        ))
        fig.add_trace(go.Bar(
            name='Legal Achieved', x=provinces, y=legal_achieved, marker_color='blue',
            text=legal_percentages, textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Customs Achieved', x=provinces, y=customs_achieved, marker_color='green',
            text=customs_percentages, textposition='auto'
        ))
        
        fig.update_layout(
            title='Sampling Quota Status by Province',
            barmode='group',
            xaxis_title='Province',
            yaxis_title='Number of Responses',
            showlegend=True,
            hovermode='x unified',
            height=500
        )

        return plot(fig, output_type='div')

    def get_cross_tabulations(self):
        """Generate enhanced cross-tabulations for multi-dimensional analysis.

        Returns:
            dict: Comprehensive cross-tabulations with derived metrics.
        """
        if self.df is None and not self.load_data():
            return {}

        cross_tabs = {}
        if 'professional_role' in self.df.columns and 'province' in self.df.columns:
            role_province_ct = pd.crosstab(
                self.df['professional_role'], self.df['province'], margins=True, normalize='index'
            )
            cross_tabs['role_by_province'] = {
                'counts': pd.crosstab(self.df['professional_role'], self.df['province'], margins=True).to_dict(),
                'percentages': role_province_ct.applymap(lambda x: f"{x:.1%}").to_dict()
            }

        if 'g1_policy_impact' in self.df.columns and 'professional_role' in self.df.columns:
            policy_flat = self.df['g1_policy_impact'].apply(
                lambda x: next(iter(x.values())) if isinstance(x, dict) and x else 'N/A'
            )
            policy_role_ct = pd.crosstab(policy_flat, self.df['professional_role'], margins=True)
            cross_tabs['policy_impact_by_role'] = policy_role_ct.to_dict()

        experience_analyses = [
            ('experience_legal', 'experience_legal_numeric', 'Legal Experience'),
            ('experience_customs', 'experience_customs_numeric', 'Customs Experience')
        ]
        
        for exp_field, exp_numeric, label in experience_analyses:
            if exp_field in self.df.columns and 'professional_role' in self.df.columns:
                exp_ct = pd.crosstab(
                    self.df[exp_field].fillna('Not specified'), self.df['professional_role'], margins=True
                )
                cross_tabs[f'{exp_field}_by_role'] = exp_ct.to_dict()
                
                if exp_numeric in self.df.columns:
                    exp_stats = self.df.groupby('professional_role')[exp_numeric].agg([
                        'count', 'mean', 'median', 'min', 'max'
                    ]).round(1)
                    cross_tabs[f'{exp_numeric}_stats'] = exp_stats.to_dict()

        return cross_tabs

    def get_sql_based_cross_tabs(self):
        """Generate enhanced SQL-based cross-tabulations for better performance.

        Returns:
            dict: SQL-based cross-tabulations with additional dimensions.
        """
        try:
            cross_tabs = {}
            role_province_query = """
            SELECT
                professional_role,
                province,
                COUNT(*) as count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY professional_role), 1) as percentage
            FROM survey_surveyresponse
            WHERE professional_role IS NOT NULL AND province IS NOT NULL
            GROUP BY professional_role, province
            ORDER BY professional_role, province
            """
            with connection.cursor() as cursor:
                cursor.execute(role_province_query)
                results = cursor.fetchall()
                
            role_province_data = {}
            for role, province, count, percentage in results:
                if role not in role_province_data:
                    role_province_data[role] = {}
                role_province_data[role][province] = {'count': count, 'percentage': percentage}
            cross_tabs['sql_role_by_province_enhanced'] = role_province_data

            for key in self.json_keys_cache['g1_policy_impact']:
                policy_query = f"""
                SELECT
                    json_extract(g1_policy_impact, '$.{key}') as policy_impact,
                    professional_role,
                    COUNT(*) as count
                FROM survey_surveyresponse
                WHERE g1_policy_impact IS NOT NULL 
                  AND professional_role IS NOT NULL
                  AND json_extract(g1_policy_impact, '$.{key}') IS NOT NULL
                GROUP BY json_extract(g1_policy_impact, '$.{key}'), professional_role
                ORDER BY json_extract(g1_policy_impact, '$.{key}'), professional_role
                """
                with connection.cursor() as cursor:
                    cursor.execute(policy_query)
                    results = cursor.fetchall()
                    
                policy_data = {}
                for rating, role, count in results:
                    rating = rating or 'N/A'
                    if rating not in policy_data:
                        policy_data[rating] = {}
                    policy_data[rating][role] = count
                cross_tabs[f'sql_policy_{key}_by_role'] = policy_data

            return cross_tabs

        except Exception as e:
            logger.error(f"Error in enhanced SQL cross-tabs: {e}")
            return {}

    def create_cross_tab_charts(self):
        """Create enhanced visualizations for cross-tabulations.

        Returns:
            dict: HTML divs for Plotly charts with improved styling.
        """
        cross_tabs = self.get_cross_tabulations()
        charts = {}
        
        if 'role_by_province' in cross_tabs and 'counts' in cross_tabs['role_by_province']:
            df_role_province = pd.DataFrame(cross_tabs['role_by_province']['counts'])
            df_clean = df_role_province.iloc[:-1, :-1]
            fig = px.imshow(
                df_clean,
                title="Professional Role Distribution by Province",
                labels=dict(x="Province", y="Professional Role", color="Count"),
                aspect="auto",
                color_continuous_scale="Blues"
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            charts['role_province_heatmap'] = plot(fig, output_type='div')

        if 'policy_impact_by_role' in cross_tabs:
            df_policy_role = pd.DataFrame(cross_tabs['policy_impact_by_role'])
            df_clean = df_policy_role.iloc[:-1]
            fig = px.bar(
                df_clean,
                title="Policy Impact Rating Distribution by Professional Role",
                barmode='stack',
                labels={'value': 'Count', 'variable': 'Professional Role'}
            )
            fig.update_layout(xaxis_title="Policy Impact Rating", yaxis_title="Number of Responses", showlegend=True)
            charts['policy_role_stacked_barchart'] = plot(fig, output_type='div')

        return charts

    def export_to_excel(self, include_raw_data=True):
        """Enhanced export to Excel with additional analysis sheets.

        Args:
            include_raw_data (bool): Whether to include raw data sheet.

        Returns:
            str: Path to the generated Excel file or None if failed.
        """
        if self.df is None and not self.load_data():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fbr_survey_export_{timestamp}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                if include_raw_data:
                    export_df = self.df.copy()
                    for col in ['g1_policy_impact', 'g2_system_impact', 'lp2_challenges', 'lp3_challenges',
                                'lp4_challenges', 'lp5_tax_types', 'ca3_challenges', 'ca4_effectiveness',
                                'cross_system_answers']:
                        if col in export_df.columns:
                            export_df[col] = export_df[col].apply(lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else x)
                    export_df.to_excel(writer, sheet_name='Raw Data', index=False)

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
                        total_info = roles
                        quota_data.append(['TOTAL', 'All Roles', total_info['achieved'], total_info['target'],
                                         f"{total_info['percentage']}%", total_info.get('completion_status', 'N/A')])
                    else:
                        for role, status in roles.items():
                            quota_data.append([
                                province.upper(), role.title(), status['achieved'], status['target'],
                                f"{status['percentage']}%", status['completion_risk']
                            ])
                quota_df = pd.DataFrame(quota_data, columns=['Province', 'Role', 'Achieved', 'Target', 'Percentage', 'Risk'])
                quota_df.to_excel(writer, sheet_name='Quota Status', index=False)

                generic_analysis = self.get_generic_questions_analysis()
                generic_data = []
                for question, results in generic_analysis.items():
                    if 'key_distributions' in results:
                        for key, distributions in results['key_distributions'].items():
                            for rating, count in distributions.items():
                                generic_data.append([question, key, rating, count])
                    elif 'distribution' in results:
                        for option, count in results['distribution'].items():
                            generic_data.append([question, 'Overall', option, count])
                
                if generic_data:
                    generic_df = pd.DataFrame(generic_data, columns=['Question', 'Dimension', 'Option', 'Count'])
                    generic_df.to_excel(writer, sheet_name='Generic Questions', index=False)

                cross_tabs = self.get_cross_tabulations()
                for tab_name, tab_data in cross_tabs.items():
                    if isinstance(tab_data, dict):
                        tab_df = pd.DataFrame(tab_data)
                        sheet_name = tab_name[:31] if len(tab_name) > 31 else tab_name
                        tab_df.to_excel(writer, sheet_name=sheet_name)

            logger.info(f"Successfully exported data to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return None

    def export_to_spss_format(self):
        """Enhanced export to SPSS-compatible format with better variable handling.

        Returns:
            str: Path to the generated CSV file or None if failed.
        """
        if self.df is None and not self.load_data():
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fbr_survey_spss_{timestamp}.csv"
            
            spss_df = self.df.copy()
            json_columns = [
                'g1_policy_impact', 'g2_system_impact', 'lp2_challenges', 'lp3_challenges',
                'lp4_challenges', 'lp5_tax_types', 'ca3_challenges', 'ca4_effectiveness',
                'cross_system_answers'
            ]
            
            for col in json_columns:
                if col in spss_df.columns:
                    spss_df[f'{col}_simplified'] = spss_df[col].apply(
                        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) and x else ''
                    )
            
            spss_df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"Successfully exported SPSS format to {filename}")
            return filename

        except Exception as e:
            logger.error(f"Error exporting to SPSS format: {e}")
            return None

    def get_advanced_analytics(self):
        """Generate comprehensive advanced analytics with multi-dimensional insights.

        Returns:
            dict: Nested analytics with role, province, policy impact, and experience dimensions.
        """
        try:
            advanced_query = """
            SELECT
                professional_role,
                province,
                json_extract(g1_policy_impact, '$.service_delivery') as policy_impact,
                json_extract(g2_system_impact, '$.workflow_efficiency') as system_impact,
                experience_legal,
                COUNT(*) as response_count
            FROM survey_surveyresponse
            WHERE professional_role IS NOT NULL
              AND province IS NOT NULL
              AND g1_policy_impact IS NOT NULL
              AND JSON_VALID(g1_policy_impact)
            GROUP BY professional_role, province, 
                     json_extract(g1_policy_impact, '$.service_delivery'),
                     json_extract(g2_system_impact, '$.workflow_efficiency'),
                     experience_legal
            ORDER BY professional_role, province, 
                     json_extract(g1_policy_impact, '$.service_delivery')
            """
            with connection.cursor() as cursor:
                cursor.execute(advanced_query)
                results = cursor.fetchall()

            advanced_data = {}
            for role, province, policy_impact, system_impact, experience, count in results:
                policy_impact = policy_impact or 'N/A'
                system_impact = system_impact or 'N/A'
                experience = experience or 'Not specified'
                
                if role not in advanced_data:
                    advanced_data[role] = {}
                if province not in advanced_data[role]:
                    advanced_data[role][province] = {}
                if policy_impact not in advanced_data[role][province]:
                    advanced_data[role][province][policy_impact] = {}
                
                advanced_data[role][province][policy_impact][system_impact] = {
                    'count': count,
                    'experience': experience
                }

            return advanced_data

        except Exception as e:
            logger.error(f"Error in advanced analytics: {e}")
            return {}

    def get_data_quality_report(self):
        """Generate comprehensive data quality report.

        Returns:
            dict: Data quality metrics and issues.
        """
        if self.df is None and not self.load_data():
            return {}

        quality_report = {
            'completeness': {},
            'consistency': {},
            'anomalies': []
        }
        
        # Completeness analysis
        for column in self.df.columns:
            non_null_count = self.df[column].notna().sum()
            completeness = round(non_null_count / len(self.df) * 100, 1)
            quality_report['completeness'][column] = {
                'non_null_count': non_null_count,
                'completeness_percentage': completeness,
                'status': 'Good' if completeness >= 90 else 'Acceptable' if completeness >= 75 else 'Needs Attention'
            }
        
        # Consistency checks
        if 'professional_role' in self.df.columns:
            valid_roles = ['legal', 'customs', 'both']
            invalid_roles = self.df[~self.df['professional_role'].isin(valid_roles)]['professional_role'].unique()
            if len(invalid_roles) > 0:
                quality_report['anomalies'].append(f"Invalid professional roles found: {list(invalid_roles)}")

        # JSON validity checks
        json_columns = [
            'g1_policy_impact', 'g2_system_impact', 'lp2_challenges', 'lp3_challenges',
            'lp4_challenges', 'lp5_tax_types', 'ca3_challenges', 'ca4_effectiveness',
            'cross_system_answers'
        ]
        with connection.cursor() as cursor:
            for col in json_columns:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM survey_surveyresponse 
                    WHERE {col} IS NOT NULL AND NOT JSON_VALID({col})
                """)
                invalid_count = cursor.fetchone()[0]
                if invalid_count > 0:
                    quality_report['anomalies'].append(f"Invalid JSON in {col}: {invalid_count} records")

        # Date range validation
        if 'submission_date' in self.df.columns:
            min_date = self.df['submission_date'].min()
            max_date = self.df['submission_date'].max()
            if pd.notna(min_date) and pd.notna(max_date):
                date_range = (max_date - min_date).days
                if date_range < 0:
                    quality_report['anomalies'].append("Invalid date range: max date before min date")
                quality_report['consistency']['submission_date_range'] = {
                    'min_date': self._format_datetime(min_date),
                    'max_date': self._format_datetime(max_date),
                    'days': date_range
                }

        return quality_report