from django.apps import AppConfig

class MeetagainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meetagain' #lost가 없길래 meetagain으로 변경함.

    def ready(self):
        import meetagain.signals # 시그널을 자동으로 불러오기 위해 ready 메서드에서 import
