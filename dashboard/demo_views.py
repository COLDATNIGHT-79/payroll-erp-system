from django.shortcuts import render
from django.utils import timezone
import json


class MockDept:
    def __init__(self, name):
        self.name = name


class MockUser:
    """Lightweight stand-in for the real User model, enough for base.html rendering."""
    is_authenticated = True

    def __init__(self, first_name, username, role, employee_id="NEX-000", department="N/A"):
        self.first_name = first_name
        self.last_name = "User"
        self.username = username
        self.role = role
        self.employee_id = employee_id
        self.department = MockDept(department)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_role_display(self):
        return self.role.title()

    # Django compat helpers
    @property
    def pk(self):
        return 0

    @property
    def id(self):
        return 0


def _inject_demo_user(request, role, name="Demo"):
    """Attach a mock user to the real request so base.html sidebar works."""
    request.user = MockUser(name, "DemoUser", role)


# ─────────────────────────────────────────
# LANDING
# ─────────────────────────────────────────
def demo_index(request):
    _inject_demo_user(request, "ADMIN")
    return render(request, "demo_landing.html", {"demo_mode": True})


# ─────────────────────────────────────────
# ADMIN
# ─────────────────────────────────────────
def demo_admin(request):
    _inject_demo_user(request, "ADMIN")

    context = {
        "demo_mode": True,
        "total_employees": 124,
        "attendance_today": 118,
        "leaves_pending": 7,
        "announcements": [
            {"title": "Office closed on Friday", "content": "Just a reminder we are closed for the public holiday this Friday. Enjoy your long weekend!", "created_at": timezone.now()},
            {"title": "New IT policy", "content": "Please review the updated IT hardware guidelines on the company portal before end of week.", "created_at": timezone.now()},
        ],
    }
    return render(request, "admin_dashboard.html", context)


# ─────────────────────────────────────────
# HR
# ─────────────────────────────────────────
def demo_hr(request):
    _inject_demo_user(request, "HR")

    mock_employees = [
        {"user": MockUser("Riya", "rsharma", "Employee"), "attendance_percentage": 98.5, "low_attendance": False},
        {"user": MockUser("Amit", "akumar", "Employee"), "attendance_percentage": 100.0, "low_attendance": False},
        {"user": MockUser("Deepa", "dpatel", "Employee"), "attendance_percentage": 65.0, "low_attendance": True},
        {"user": MockUser("Sahil", "sgupta", "Employee"), "attendance_percentage": 88.0, "low_attendance": False},
    ]

    mock_live_feed = [
        {"employee": MockUser("Riya", "rsharma", "Employee"), "check_in": "08:50 AM"},
        {"employee": MockUser("Amit", "akumar", "Employee"), "check_in": "09:05 AM"},
        {"employee": MockUser("Deepa", "dpatel", "Employee"), "check_in": "09:15 AM"},
    ]

    mock_hardware = [
        {"asset": "MacBook Pro", "assigned_to": "Riya Sharma"},
        {"asset": "Dell XPS 15", "assigned_to": "Amit Kumar"},
        {"asset": "Logitech MX Master", "assigned_to": "Deepa Patel"},
    ]

    context = {
        "demo_mode": True,
        "total_employees": 124,
        "attendance_today": 118,
        "leaves_pending": 7,
        "avg_hours": 8.4,
        "employees": mock_employees,
        "live_feed": mock_live_feed,
        "pending_leave_requests": [
            {"employee": MockUser("Sahil", "sgupta", "Employee"), "leave_type": "Sick", "start_date": "Apr 15", "end_date": "Apr 16"}
        ],
        "checkout_alerts": [],
        "late_arrivals": [],
        "hardware_inventory": mock_hardware,
    }
    return render(request, "hr_dashboard.html", context)


# ─────────────────────────────────────────
# EMPLOYEE
# ─────────────────────────────────────────
def demo_employee(request):
    _inject_demo_user(request, "EMPLOYEE", name="Riya")

    class MockStatus:
        """Provides get_status_display() for attendance records."""
        def __init__(self, date, check_in, check_out, status, display):
            self.date = date
            self.check_in = check_in
            self.check_out = check_out
            self.status = status
            self._display = display

        def get_status_display(self):
            return self._display

    mock_attendance = [
        MockStatus("Apr 11, 2026", "09:00 AM", "05:00 PM", "PRESENT", "Present"),
        MockStatus("Apr 10, 2026", "08:55 AM", "05:15 PM", "PRESENT", "Present"),
        MockStatus("Apr 09, 2026", "09:10 AM", None, "MISS_PUNCH", "Miss Punch"),
    ]

    mock_calendar_days = []
    for i in range(1, 31):
        status = 'present'
        if i % 7 == 0:
            status = 'holiday'
        elif i == 9:
            status = 'absent'
        elif i == 14:
            status = 'late'
        mock_calendar_days.append({"day": i, "status": status})

    context = {
        "demo_mode": True,
        "payroll_total": 45000,
        "days_present": "20/22",
        "leaves_pending": 1,
        "daily_stats": "In: 09:00 AM | Out: 05:00 PM | Total: 8h 0m",
        "recent_activity": "You checked in at 09:00 AM via Scanner ID #1.",
        "attendance": mock_attendance,
        "calendar_days": mock_calendar_days,
        "knowledge_links": [
            {"title": "Company Handbook", "url": "#"},
            {"title": "Reimbursement Form", "url": "#"},
        ],
        "profile_title": "Riya Sharma",
        "profile_role": "Employee",
        "profile_id": "NEX-101",
        "profile_department": "Engineering",
        "latest_announcement": {"title": "Welcome to Nexus ERP", "content": "You are seeing the new employee dashboard with the revamped Cafe/Green UI.", "created_at": timezone.now()},
    }
    return render(request, "employee_dashboard.html", context)


# ─────────────────────────────────────────
# FINANCE
# ─────────────────────────────────────────
def demo_finance(request):
    _inject_demo_user(request, "FINANCE")

    mock_payroll_data = [
        {
            "employee": MockUser("Riya", "rsharma", "Employee"),
            "present_days": 21,
            "absent_days": 1,
            "base": 1500,
            "final_salary": 31500,
            "deduction_loss": 1500
        },
        {
            "employee": MockUser("Amit", "akumar", "Employee"),
            "present_days": 22,
            "absent_days": 0,
            "base": 2000,
            "final_salary": 44000,
            "deduction_loss": 0
        },
        {
            "employee": MockUser("Deepa", "dpatel", "Employee"),
            "present_days": 18,
            "absent_days": 4,
            "base": 2500,
            "final_salary": 45000,
            "deduction_loss": 10000
        },
    ]

    payroll_chart_json = json.dumps([
        {"name": item["employee"].first_name, "salary": item["final_salary"], "deduction": item["deduction_loss"]}
        for item in mock_payroll_data
    ])

    context = {
        "demo_mode": True,
        "payroll_data": mock_payroll_data,
        "payroll_chart_json": payroll_chart_json,
        "total_budget": 120500,
        "total_deductions": 11500,
        "processed_salaries": len(mock_payroll_data),
    }
    return render(request, "finance_dashboard.html", context)
