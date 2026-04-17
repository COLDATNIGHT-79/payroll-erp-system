from users.models import Company, Branch, Department, User
from attendance.models import Attendance
from leave.models import Leave
from django.utils import timezone
from datetime import timedelta, time
import random

def seed():
    print("Seeding database...")
    
    # 1. Company
    comp, _ = Company.objects.get_or_create(name="Nexus IT Solutions", email="contact@nexusit.com")
    
    # 2. Branch
    branch_hq, _ = Branch.objects.get_or_create(code="HQ01", defaults={"name": "Headquarters", "city": "Mumbai", "company": comp})
    branch_dev, _ = Branch.objects.get_or_create(code="DEV01", defaults={"name": "Development Center", "city": "Pune", "company": comp})
    
    # 3. Department
    dept_hr, _ = Department.objects.get_or_create(name="Human Resources", branch=branch_hq)
    dept_fin, _ = Department.objects.get_or_create(name="Finance", branch=branch_hq)
    dept_dev, _ = Department.objects.get_or_create(name="Engineering", branch=branch_dev)
    dept_sales, _ = Department.objects.get_or_create(name="Sales", branch=branch_hq)
    
    # 4. Users
    roles_config = [
        ("admin_user", "ADMIN", "EMP_A01", dept_dev, 0),
        ("hr_manager", "HR", "EMP_H01", dept_hr, 2500.00),
        ("finance_director", "FINANCE", "EMP_F01", dept_fin, 3000.00),
        ("eng_manager", "MANAGER", "EMP_M01", dept_dev, 3500.00),
        ("dev_john", "EMPLOYEE", "EMP_E01", dept_dev, 1200.00),
        ("dev_alice", "EMPLOYEE", "EMP_E02", dept_dev, 1500.00),
        ("sales_bob", "EMPLOYEE", "EMP_E03", dept_sales, 1100.00),
        ("hr_assistant", "EMPLOYEE", "EMP_H02", dept_hr, 900.00),
        ("designer_riya", "EMPLOYEE", "EMP_E04", dept_dev, 1400.00),
    ]
    
    created_users = []
    
    for username, role, emp_id, dept, pd_salary in roles_config:
        user, created = User.objects.get_or_create(username=username, defaults={
            "employee_id": emp_id,
            "role": role,
            "company": comp,
            "branch": dept.branch,
            "department": dept,
            "per_day_salary": pd_salary,
            "first_name": username.split("_")[1].capitalize() if "_" in username else username.capitalize(),
            "last_name": "Smith" if "dev" in username else "Doe"
        })
        if created:
            user.set_password("password123")
            user.save()
        created_users.append(user)

    print("Users populated.")

    # 5. Attendance for current month
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    days_to_populate = min((today - month_start).days + 1, 25)
    
    employees = [u for u in created_users if u.role == "EMPLOYEE"]
    
    for emp in employees:
        for i in range(days_to_populate):
            att_date = today - timedelta(days=i)
            if att_date.weekday() >= 5: # Skip weekends
                continue
                
            status_choice = random.choices(["PRESENT", "ABSENT", "MISS_PUNCH"], weights=[80, 10, 10])[0]
            
            check_in = time(9, random.randint(0, 45)) if status_choice != "ABSENT" else None
            check_out = time(17, random.randint(0, 59)) if status_choice == "PRESENT" else None
            
            Attendance.objects.get_or_create(employee=emp, date=att_date, defaults={
                "status": status_choice,
                "check_in": check_in,
                "check_out": check_out
            })

    print("Attendance data populated.")

    # 6. Leaves
    Leave.objects.get_or_create(employee=employees[0], start_date=today + timedelta(days=2), end_date=today + timedelta(days=3), defaults={
        "leave_type": "SICK",
        "reason": "Fever and cold",
        "status": "PENDING"
    })
    Leave.objects.get_or_create(employee=employees[1], start_date=today + timedelta(days=1), end_date=today + timedelta(days=4), defaults={
        "leave_type": "ANNUAL",
        "reason": "Family vacation",
        "status": "APPROVED"
    })
    Leave.objects.get_or_create(employee=employees[2], start_date=today + timedelta(days=5), end_date=today + timedelta(days=6), defaults={
        "leave_type": "CASUAL",
        "reason": "Bank work",
        "status": "PENDING"
    })

    print("Leaves populated.")
    print("\n--- Summary ---")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Attendance Records: {Attendance.objects.count()}")
    print(f"Total Companies: {Company.objects.count()}")
    print(f"Total Departments: {Department.objects.count()}")
    print(f"Passwords generated are all: 'password123'")

seed()
