from django.contrib.auth.base_user import BaseUserManager

class UserModelManager(BaseUserManager):
    def create_user(self, hoppy, password, **extra_fields):
        if not hoppy:
            raise ValueError(_("The Hoppy must be set"))
        # Assuming 'hoppy' is a field in your user model
        user = self.model(hoppy=hoppy, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, hoppy, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(hoppy, password, **extra_fields)
