from django.db import models
from django.contrib.auth.models import AbstractUser


# Company Model
class Company(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

# Branch Model
class Branch(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.city}"
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class User(AbstractUser):

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("HR", "HR"),
        ("MANAGER", "Manager"),
        ("FINANCE", "Finance"),
        ("EMPLOYEE", "Employee"),
    )

    employee_id = models.CharField(max_length=20, unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="EMPLOYEE"
    )

    per_day_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.username} (Role: {self.get_role_display()})"