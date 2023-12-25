from django.apps import AppConfig


class PersonalInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'PersonalInfo'

    # make sure Django knows about these signals
    def ready(self):
        import PersonalInfo.signals
        
