from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Payroll


def generate_payslip(request, payroll_id):

    payroll = Payroll.objects.get(id=payroll_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="payslip.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, "Employee Payslip")

    p.drawString(100, 760, f"Employee: {payroll.employee.username}")
    p.drawString(100, 740, f"Month: {payroll.month}/{payroll.year}")

    p.drawString(100, 700, f"Base Salary: {payroll.base_salary}")
    p.drawString(100, 680, f"Absent Days: {payroll.absent_days}")

    p.drawString(100, 660, f"Final Salary: {payroll.final_salary}")

    p.showPage()
    p.save()

    return response