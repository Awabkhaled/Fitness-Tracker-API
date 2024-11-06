from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """Class for managing user creation"""

    def normalize_email(cls, email):
        """Normalize the email address by lowercasing the domain part"""
        try:
            email.index('@')
        except Exception:
            raise ValueError("Email is not valid")
        else:
            return email.lower()

    def create_user(self, email, password, **extra_kwargs):
        if not email:
            raise ValueError("Email is required")
        user = self.model(email=self.normalize_email(email), **extra_kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_kwargs):
        user = self.create_user(email, password, **extra_kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)
    password = models.CharField(max_length=254)
    name = models.CharField(max_length=254, null=False, default='You')
    age = models.SmallIntegerField(null=True, blank=False)
    gender = models.CharField(max_length=10,
                              choices=[('Male', 'Male'),
                                       ('Female', 'Female'),
                                       ('Other', 'Other')
                                       ], blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2,
                                 blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2,
                                 blank=True, null=True)
    bmi = models.DecimalField(max_digits=4, decimal_places=1,
                              blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
