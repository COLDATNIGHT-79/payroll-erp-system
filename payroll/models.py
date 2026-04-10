from django.db import models
from django.conf import settings


class Payroll(models.Model):

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    month = models.IntegerField()

    year = models.IntegerField()

    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    present_days = models.IntegerField(default=0)

    absent_days = models.IntegerField(default=0)

    final_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    generated_at = models.DateTimeField(auto_now_add=True)

    def calculate_salary(self):

        total_working_days = 30

        per_day_salary = self.base_salary / total_working_days

        deduction = per_day_salary * self.absent_days

        self.final_salary = self.base_salary - deduction

    def save(self, *args, **kwargs):

        self.calculate_salary()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year}"