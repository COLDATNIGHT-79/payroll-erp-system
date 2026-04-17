from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseForbidden
from functools import wraps
from datetime import datetime, time, timedelta

from users.models import User
from attendance.models import Attendance
from leave.models import Leave
from payroll.models import Payroll
from dashboard.models import Announcement


# 🔐 ROLE REQUIRED DECORATOR
def role_required(allowed_roles):

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # 🔹 Check login
            if not request.user.is_authenticated:
                return redirect('login')

            user_role = str(request.user.role).lower()

            if user_role not in [r.lower() for r in allowed_roles]:
                return HttpResponseForbidden("❌ Access Denied")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


# 🔐 LOGIN VIEW
def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


# 🔥 ROLE BASED REDIRECT (FIXED)
def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    role = str(user.role).upper()

    if role == "ADMIN":
        return redirect("admin_dashboard")
    elif role == "HR":
        return redirect("hr_dashboard")
    elif role == "FINANCE":
        return redirect("finance_dashboard")
    elif role == "MANAGER":
        return redirect("manager_dashboard")
    else:
        return redirect("employee_dashboard")


# 👑 ADMIN DASHBOARD
def admin_dashboard(request):
    if not request.user.is_authenticated or str(request.user.role).upper() != "ADMIN":
        return HttpResponseForbidden("❌ Access Denied")

    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title and content:
            Announcement.objects.create(title=title, content=content, posted_by=request.user)
            return redirect('admin_dashboard')

    today = timezone.now().date()
    total_employees = User.objects.filter(role__iexact='employee').count()
    attendance_today = Attendance.objects.filter(date=today).count()
    leaves_pending = Leave.objects.filter(status__iexact='pending').count()
    
    announcements = Announcement.objects.all()[:5]

    context = {
        "total_employees": total_employees,
        "attendance_today": attendance_today,
        "leaves_pending": leaves_pending,
        "announcements": announcements,
    }

    return render(request, "admin_dashboard.html", context)


# 🧑‍💼 HR DASHBOARD
def hr_dashboard(request):
    if not request.user.is_authenticated or str(request.user.role).upper() not in ["HR", "ADMIN"]:
        return HttpResponseForbidden("❌ Access Denied")

    today = timezone.now().date()
    week_start = today - timedelta(days=6)

    total_employees = User.objects.filter(role__iexact='employee').count()
    employees_qs = User.objects.filter(role__iexact='employee').order_by('first_name', 'last_name')[:12]
    
    employee_data = []
    month_start = today.replace(day=1)
    for emp in employees_qs:
        monthly_att = Attendance.objects.filter(employee=emp, date__gte=month_start, date__lte=today)
        pres_count = monthly_att.filter(status__iexact='present').count()
        miss_count = monthly_att.filter(status__iexact='miss_punch').count()
        eff_pres = pres_count + (miss_count * 0.5)
        percentage = (eff_pres / 22.0) * 100
        employee_data.append({
            "user": emp,
            "attendance_percentage": percentage,
            "low_attendance": percentage < 70
        })
    attendance_today = Attendance.objects.filter(date=today).count()
    leaves_pending = Leave.objects.filter(status__iexact='pending').count()
    
    live_feed = Attendance.objects.filter(date=today).order_by('-created_at')[:6]
    pending_leave_requests = Leave.objects.filter(status__iexact='pending').order_by('-applied_at')[:6]
    checkout_alerts = Attendance.objects.filter(date=today, check_in__isnull=False, check_out__isnull=True)
    late_arrivals = Attendance.objects.filter(date=today, check_in__gt=time(9, 0)).order_by('check_in')[:8]

    week_records = Attendance.objects.filter(date__range=(week_start, today), check_in__isnull=False, check_out__isnull=False)
    total_seconds = 0
    for record in week_records:
        total_seconds += (datetime.combine(record.date, record.check_out) - datetime.combine(record.date, record.check_in)).seconds

    avg_hours = round((total_seconds / week_records.count() / 3600), 1) if week_records.exists() else 0

    hardware_inventory = [
        {"asset": "Asus Vivobook", "assigned_to": "Riya Sharma"},
        {"asset": "iPhone 14", "assigned_to": "Amit Kumar"},
        {"asset": "Wireless Mouse", "assigned_to": "Deepa Patel"},
    ]

    context = {
        "total_employees": total_employees,
        "attendance_today": attendance_today,
        "leaves_pending": leaves_pending,
        "employees": employee_data,
        "live_feed": live_feed,
        "pending_leave_requests": pending_leave_requests,
        "checkout_alerts": checkout_alerts,
        "late_arrivals": late_arrivals,
        "avg_hours": avg_hours,
        "hardware_inventory": hardware_inventory,
    }

    return render(request, "hr_dashboard.html", context)


# 🧑‍💼 MANAGER
def manager_dashboard(request):
    if not request.user.is_authenticated or str(request.user.role).upper() not in ["MANAGER", "ADMIN"]:
        return HttpResponseForbidden("❌ Access Denied")
    return hr_dashboard(request)


# 💰 FINANCE
def finance_dashboard(request):
    if not request.user.is_authenticated or str(request.user.role).upper() not in ["FINANCE", "ADMIN"]:
        return HttpResponseForbidden("❌ Access Denied")

    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    employees = User.objects.exclude(role='ADMIN')
    
    payroll_data = []
    total_budget = 0
    total_deductions = 0
    
    for emp in employees:
        # Calculate monthly attendance
        monthly_attendance = Attendance.objects.filter(employee=emp, date__gte=month_start, date__lte=today)
        
        present_count = monthly_attendance.filter(status='PRESENT').count()
        miss_punch_count = monthly_attendance.filter(status='MISS_PUNCH').count()
        absent_count = monthly_attendance.filter(status='ABSENT').count()
        
        # Calculate present days (miss punch = half day present deduction effectively)
        effective_present_days = present_count + (miss_punch_count * 0.5)
        
        # Calculate Base vs Final
        per_day = emp.per_day_salary or 0
        computed_salary = float(effective_present_days) * float(per_day)
        
        # Calculate what they "could" have made to show deduction loss
        potential_working_days = 22 # Approx max monthly
        potential_salary = potential_working_days * float(per_day)
        loss = potential_salary - computed_salary if potential_salary > computed_salary else 0
        
        payroll_data.append({
            "employee": emp,
            "present_days": effective_present_days,
            "absent_days": absent_count,
            "base": per_day,
            "final_salary": computed_salary,
            "deduction_loss": loss
        })
        
        total_budget += computed_salary
        total_deductions += loss

    import json
    payroll_chart_json = json.dumps([
        {
            "name": item["employee"].first_name or item["employee"].username,
            "salary": float(item["final_salary"]),
            "deduction": float(item["deduction_loss"]),
        }
        for item in payroll_data
    ])

    context = {
        "payroll_data": payroll_data,
        "payroll_chart_json": payroll_chart_json,
        "total_budget": total_budget,
        "total_deductions": total_deductions,
        "processed_salaries": len(payroll_data)
    }

    return render(request, "finance_dashboard.html", context)


# 👤 EMPLOYEE
def employee_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = request.user
    today = timezone.now().date()
    month_start = today.replace(day=1)

    attendance = Attendance.objects.filter(employee=user).order_by('-date')[:5]
    payrolls = Payroll.objects.filter(employee=user)
    monthly_attendance = Attendance.objects.filter(employee=user, date__gte=month_start, date__lte=today)

    attendance_today = Attendance.objects.filter(employee=user, date=today).count()
    leaves_pending = Leave.objects.filter(employee=user, status__iexact='pending').count()

    present_count = monthly_attendance.filter(status__iexact='present').count()
    miss_punch_count = monthly_attendance.filter(status__iexact='miss_punch').count()
    absent_count = monthly_attendance.filter(status__iexact='absent').count()
    
    effective_present_days = present_count + (miss_punch_count * 0.5)
    days_present = f"{effective_present_days}/22"

    per_day = user.per_day_salary or 0
    current_month_salary = float(effective_present_days) * float(per_day)

    latest_record = Attendance.objects.filter(employee=user).order_by('-date', '-created_at').first()
    if latest_record and latest_record.check_in:
        if latest_record.check_out:
            duration = datetime.combine(latest_record.date, latest_record.check_out) - datetime.combine(latest_record.date, latest_record.check_in)
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            daily_stats = f"In: {latest_record.check_in.strftime('%I:%M %p')} | Out: {latest_record.check_out.strftime('%I:%M %p')} | Total: {hours}h {minutes}m"
        else:
            daily_stats = f"In: {latest_record.check_in.strftime('%I:%M %p')} | Out: -- | Total: --"
    else:
        daily_stats = "No attendance data for today"

    recent_activity = "No recent scanner activity"
    if latest_record and latest_record.check_in:
        recent_activity = f"You checked in at {latest_record.check_in.strftime('%I:%M %p')} via Scanner ID #1."

    knowledge_links = [
        {"title": "Project Onboarding Guide", "url": "#"},
        {"title": "Company HR Policies", "url": "#"},
        {"title": "Scanner Troubleshooting", "url": "#"},
    ]

    assets = [
        {"item": "Asus Vivobook", "status": "Assigned"},
        {"item": "Wireless Mouse", "status": "Assigned"},
        {"item": "Charger", "status": "Assigned"},
    ]

    latest_announcement = Announcement.objects.first()

    context = {
        "attendance": attendance,
        "attendance_today": attendance_today,
        "leaves_pending": leaves_pending,
        "payroll_total": current_month_salary,
        "daily_stats": daily_stats,
        "days_present": days_present,
        "live_status": "Connected to Scanner",
        "recent_activity": recent_activity,
        "knowledge_links": knowledge_links,
        "assets": assets,
        "profile_title": user.get_full_name() or user.username,
        "profile_role": user.get_role_display(),
        "profile_id": user.employee_id,
        "profile_department": user.department.name if user.department else "N/A",
        "latest_announcement": latest_announcement,
    }

    return render(request, "employee_dashboard.html", context)


def employee_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    context = {
        "profile_title": user.get_full_name() or user.username,
        "profile_role": user.get_role_display(),
        "profile_id": user.employee_id,
        "profile_department": user.department.name if user.department else "N/A",
    }
    return render(request, "employee_profile.html", context)


def employee_assets(request):
    if not request.user.is_authenticated:
        return redirect('login')
    assets = [
        {"item": "Asus Vivobook", "status": "Assigned"},
        {"item": "Wireless Mouse", "status": "Assigned"},
        {"item": "Charger", "status": "Assigned"},
    ]
    context = {
        "assets": assets
    }
    return render(request, "employee_assets.html", context)


def employee_attendance(request):
    if not request.user.is_authenticated:
        return redirect('login')
    today = timezone.now().date()
    current_time = timezone.now().time()
    user = request.user

    # Fetch today's record
    attendance, created = Attendance.objects.get_or_create(
        employee=user,
        date=today,
        defaults={'status': 'ABSENT'}
    )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "check_in":
            if not attendance.check_in:
                attendance.check_in = current_time
                attendance.status = 'PRESENT'
                attendance.save()
        
        elif action == "check_out":
            if attendance.check_in and not attendance.check_out:
                attendance.check_out = current_time
                attendance.save()
            elif not attendance.check_in:
                # Miss Punch logic: unchecked in but trying to checkout
                attendance.check_out = current_time
                attendance.status = 'MISS_PUNCH'
                attendance.save()

        return redirect("employee_attendance")

    context = {
        "attendance": attendance,
        "today": today
    }
    return render(request, "employee_attendance.html", context)


def employee_list(request):
    if str(request.user.role).upper() == "ADMIN":
        employees = User.objects.all().order_by('role', 'first_name')
    else:
        employees = User.objects.filter(role__iexact='employee')

    context = {
        "employees": employees
    }

    return render(request, "employee_list.html", context)


def add_employee(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        employee_id = request.POST.get("employee_id")

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            role='EMPLOYEE'
        )

        return redirect("employee_list")

    return render(request, "add_employee.html")


def delete_employee(request, id):
    emp = User.objects.get(id=id)
    emp.delete()
    return redirect("employee_list")


def logout_view(request):
    logout(request)
    return redirect('login')