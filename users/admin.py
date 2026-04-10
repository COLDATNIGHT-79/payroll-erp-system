from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, Branch, Department, User


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "company")
    list_filter = ("company",)
    search_fields = ("name", "city")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "branch")
    list_filter = ("branch",)
    search_fields = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "employee_id", "role", "branch", "department")
    list_filter = ("role", "branch", "department", "is_staff", "is_active")
    search_fields = ("username", "employee_id")

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Employee Details', {'fields': ('employee_id', 'role', 'per_day_salary', 'company', 'branch', 'department', 'manager')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Employee Details', {'fields': ('employee_id', 'role', 'per_day_salary', 'company', 'branch', 'department', 'manager')}),
    )