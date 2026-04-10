from django.contrib import admin
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
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "employee_id", "role", "branch", "department")
    list_filter = ("role", "branch", "department")
    search_fields = ("username", "employee_id")