from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('survey', '0008_surveyresponse_survey_feedback')]  # Replace with latest migration, e.g., '0001_initial'
    operations = [
        migrations.AlterField(
            model_name='SurveyResponse',
            name='mobile',
            field=models.CharField(max_length=20, blank=True, null=True, help_text="RI3: Mobile number (optional)"),
        ),
        migrations.AlterField(
            model_name='SurveyResponse',
            name='practice_areas',
            field=models.CharField(max_length=100, blank=True, null=True, help_text="RI7: Primary practice areas as comma-separated values (e.g., 'income_tax,sales_tax')"),
        ),
        migrations.AlterField(
            model_name='SurveyResponse',
            name='kii_consent',
            field=models.CharField(
                max_length=3,
                choices=[('yes', 'Yes'), ('no', 'No')],
                blank=True,
                null=True,
                help_text="RI10: Consent for follow-up interview"
            ),
        ),
    ]