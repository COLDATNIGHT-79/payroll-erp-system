from django.urls import path
from . import views
from . import demo_views

urlpatterns = [

    # 🔐 LOGIN
    path('login/', views.login_view, name='login'),

    # 🔥 DEFAULT (ROLE BASED REDIRECT)
    path('', views.dashboard_redirect, name='dashboard_redirect'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('finance-dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('profile/', views.employee_profile, name='employee_profile'),
    path('assets/', views.employee_assets, name='employee_assets'),
    path('attendance/', views.employee_attendance, name='employee_attendance'),
    path('employees/', views.employee_list, name='employee_list'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('logout/', views.logout_view, name='logout'),
    
    # 🌟 DEMO DASHBOARDS
    path('demo/', demo_views.demo_index, name='demo_index'),
    path('demo/admin/', demo_views.demo_admin, name='demo_admin'),
    path('demo/hr/', demo_views.demo_hr, name='demo_hr'),
    path('demo/finance/', demo_views.demo_finance, name='demo_finance'),
    path('demo/employee/', demo_views.demo_employee, name='demo_employee'),
    
]