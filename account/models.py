from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
# from loans.models import RequestsLoan,Offer

class MyAccountManager(BaseUserManager):
    def create_user(self, mobile, username, password=None):
        if not mobile:
            raise ValueError("Users must have a mobile number.")
        if not username:
            raise ValueError("Users must have a username.")
        user = self.model(
            mobile = mobile,
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, mobile, username, password):
        user = self.create_user(
            mobile = mobile,
            username = username,
            password = password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_investor = True
        user.is_borrower = True

        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    mobile          = PhoneNumberField(verbose_name="mobile number",unique=True)
    username        = models.CharField(max_length=30, unique=True)
    is_admin        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_superuser    = models.BooleanField(default=False)
    #our custom users
    is_investor       = models.BooleanField(default=False)
    is_borrower       = models.BooleanField(default=False)
    hide_phone        = models.BooleanField(default=True)

    objects = MyAccountManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True

class Investor(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    def get_user(self):
        return self.user.is_investor == True
    is_investor       = property(get_user)
    investor_email  = models.EmailField(null=True, blank=True)
    invest_money    = models.IntegerField(default=0,null=False,blank=False)
    # your_requests   = models.ForeignKey(RequestsLoan, on_delete=models.CASCADE, null=True,blank=True)
    # loans           = models.ForeignKey(Loan, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Borrower(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, primary_key=True)
    def get_user(self):
        return self.user.is_borrower
    is_borrower       = property(get_user)
    borrower_email  = models.EmailField(null=True, blank=True)
    # loans           = models.ForeignKey(Loan, on_delete=models.CASCADE)
    # offers          = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True,blank=True )
    # requests        = models.ForeignKey(RequestsLoan,on_delete=models.CASCADE, null=True,blank=True )
    def __str__(self):
        return self.user.username
        
#If you want every user to have an automatically generated Token 
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

