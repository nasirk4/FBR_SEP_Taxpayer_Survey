# survey/apps.py
from django.apps import AppConfig

class SurveyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'survey'

    def ready(self):
        # This ensures the admin configuration is loaded
        import survey.admin