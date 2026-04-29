from django.contrib.auth.models import AbstractUser
from django.db import models


# 👤 CUSTOM USER MODEL (ONLY ONE)
class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('csr', 'CSR'),
        ('loan_officer', 'Loan Officer'),
        ('branch_manager', 'Branch Manager'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')
    is_locked = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    must_change_password = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    

# 🏦 LOAN MODEL (SEPARATE MODEL)
class Loan(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    loan_type = models.CharField(max_length=50)

    status = models.CharField(max_length=20, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    

    from django.db import models

class Loan(models.Model):

    username = models.CharField(max_length=100)  # 👈 store raw text
    amount = models.FloatField()
    loan_type = models.CharField(max_length=50)

    status = models.CharField(max_length=20, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.amount}"    
    


    from django.db import models

class Loan(models.Model):
    username = models.CharField(max_length=100)
    amount = models.FloatField()
    loan_type = models.CharField(max_length=50)

    # IMPORTANT: track approval stage
    status = models.CharField(max_length=30, default="Pending")

    # NEW FIELD → loan officer approval
    officer_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.amount}"
    
    officer_approved = models.BooleanField(default=False)

class Loan(models.Model):
     username = models.CharField(max_length=100)
     amount = models.FloatField()
     loan_type = models.CharField(max_length=50)

     status = models.CharField(max_length=30, default="Pending")

     officer_approved = models.BooleanField(default=False)
     created_at = models.DateTimeField(auto_now_add=True)

     def __str__(self):
        return f"{self.user.username} - {self.amount}"

     def __str__(self):
        return self.username
    
    
from django.utils import timezone

class AuditLog(models.Model):
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.action}" 

        


    