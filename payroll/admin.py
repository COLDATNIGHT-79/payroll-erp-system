from django.contrib import admin
from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "year", "base_salary", "final_salary")
    list_filter = ("month", "year")
    search_fields = ("employee__username",)