from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            if user.role == "ADMIN":
                return redirect("admin_dashboard")
            elif user.role == "HR":
                return redirect("hr_dashboard")
            elif user.role == "FINANCE":
                return redirect("finance_dashboard")
            elif user.role == "MANAGER":
                return redirect("manager_dashboard")
            else:
                return redirect("employee_dashboard")

        else:
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")