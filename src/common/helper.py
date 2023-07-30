from common.models import User

class CommonHelper:
    @staticmethod
    def user_exists(**kwargs):
        model = User
        try:
            user = model.objects.get(**kwargs)
        except model.DoesNotExist:
            return False
        return user