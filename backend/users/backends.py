from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentIDBackend(ModelBackend):
    def authenticate(self, request, student_id=None, password=None, **kwargs):
        try:
            user = User.objects.get(student_id=student_id)
        except User.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
