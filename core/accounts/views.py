from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .utils import log_action
from .utils import log_action
from .models import CustomUser
from . import views

# admin login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            auth.login(request, user)
            return redirect('admin_dashboard')  # or dashboard
        else:
            messages.error(request, "Invalid Admin Credentials")

    return render(request, 'admin_login.html')


def admin_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')

    return render(request, 'admin_dashboard.html')


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')

    return render(request, 'admin_dashboard.html')





def manage_employees(request):
    employees = CustomUser.objects.exclude(role="user")
    

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")

        # ✅ Basic validation
        if not username or not email or not password or not role:
            messages.error(request, "All fields are required")
            return redirect("manage_employees")

        # ✅ Check duplicate username
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("manage_employees")

        # ✅ Check duplicate email
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("manage_employees")

        # ✅ Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        # ✅ Send email
        try:
            send_mail(
                "Account Created",
                f"""
Hello {username},

Your account has been created successfully.

Role: {role}
Username: {username}
password: {password}

👉 Please login and change your password.

Login here: http://127.0.0.1:8000/
""",
                settings.EMAIL_HOST_USER,   # sender (your Gmail)
                [email],                    # receiver (user email)
                fail_silently=False,
            )
            messages.success(request, "User created & email sent ✅")

        except Exception as e:
            messages.warning(request, "User created but email not sent ⚠️")
            print("Email Error:", e)   # for debugging

        return redirect("manage_employees")

    return render(request, "manage_employees.html", {
        "employees": employees
    })
# ✅ DELETE EMPLOYEE
def delete_employee(request, id):
    user = get_object_or_404(CustomUser, id=id)
    user.delete()
    return redirect("manage_employees")

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Only registered users can login")
            return redirect("login")

        user = CustomUser.objects.get(username=username)

        # 🔒 Check if account locked
        if user.is_locked:
            messages.error(request, "Account is locked. Contact admin.")
            return redirect("login")

        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:

            # 🔁 Reset failed attempts
            user.failed_attempts = 0
            user.save()

            login(request, auth_user)
            log_action(auth_user, "Logged in")
            

            # 🎯 ROLE-BASED REDIRECT
            if user.is_superuser:
                return redirect("admin_dashboard")

            elif user.role == "employee":
                return redirect("employee_dashboard")

            elif user.role == "csr":
                return redirect("csr_dashboard")

            elif user.role == "loan_officer":
                return redirect("loan_officer_dashboard")

            elif user.role == "branch_manager":
                return redirect("branch_manager_dashboard")

            else:
                return redirect("user_dashboard")

        else:
            # ❌ Wrong password
            user.failed_attempts += 1

            if user.failed_attempts >= 3:
                user.is_locked = True
                messages.error(request, "Account locked after 3 failed attempts")
            else:
                messages.error(request, f"Invalid password ({user.failed_attempts}/3)")

            user.save()
            return redirect("login")

    return render(request, "login.html")
 
# 🏠 HOME PAGE
def home(request):
    return render(request, "home.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not email or not password:
            messages.error(request, "All fields required")
            return render(request, "signup.html")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, "signup.html")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, "signup.html")

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="user"
        )

        messages.success(request, "Account created successfully ✅")

        return redirect("login")

    return render(request, "signup.html")

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # ❌ check old password
        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
            return redirect("change_password")

        # ❌ confirm match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("change_password")

        # 🔐 update password
        user.set_password(new_password)
        user.must_change_password = False  # optional reset flag
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully")

        # 👇 redirect to correct dashboard after change
        if user.is_superuser:
            return redirect("admin_dashboard")
        elif user.role == "employee":
            return redirect("employee_dashboard")
        elif user.role == "csr":
            return redirect("csr_dashboard")
        elif user.role == "loan_officer":
            return redirect("loan_officer_dashboard")
        elif user.role == "branch_manager":
            return redirect("branch_manager_dashboard")
        else:
            return redirect("user_dashboard")

    return render(request, "change_password.html")


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Loan

@login_required
def loan_officer_dashboard(request):

    # only loan officer OR admin
    if not request.user.is_superuser and request.user.role != "loan_officer":
        return redirect("login")

    loans = Loan.objects.all().order_by("-created_at")

    return render(request, "loan_officer_dashboard.html", {
        "loans": loans
    })


def update_loan_status(request, id, action):
    loan = Loan.objects.get(id=id)

    if action == "approve":
        loan.status = "Approved"

    elif action == "reject":
        loan.status = "Rejected"

    loan.save()

    return redirect("loan_officer_dashboard")


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Loan, CustomUser


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Loan

@login_required
def loan_officer_dashboard(request):

    # 🔒 Superuser OR loan officer only
    if not (request.user.is_superuser or request.user.role == "loan_officer"):
        return redirect("login")

    loans = Loan.objects.all().order_by("-created_at")

    return render(request, "accounts/loan_officer_dashboard.html", {
        "loans": loans
    })

# ➕ ADD LOAN (MANUAL ENTRY BY OFFICER)
@login_required
def add_loan(request):

    if request.method == "POST":
        username = request.POST.get("username")
        amount = request.POST.get("amount")
        loan_type = request.POST.get("loan_type")

        user = CustomUser.objects.get(username=username)

        Loan.objects.create(
            user=user,
            amount=amount,
            loan_type=loan_type,
            status="Pending"
        )

        return redirect("loan_officer_dashboard")

    return render(request, "add_loan.html")


# ✅ APPROVE / REJECT LOAN
@login_required
def update_loan_status(request, id, action):

    loan = get_object_or_404(Loan, id=id)

    if action == "approve":
        loan.status = "Approved"

    elif action == "reject":
        loan.status = "Rejected"

    loan.save()

    return redirect("loan_officer_dashboard")


from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser, Loan

from django.shortcuts import render, redirect
from .models import Loan, CustomUser
from django.contrib import messages


from django.shortcuts import render, redirect
from .models import Loan

def add_loan(request):

    if request.method == "POST":

        username = request.POST.get("username")
        amount = request.POST.get("amount")
        loan_type = request.POST.get("loan_type")

        Loan.objects.create(
            username=username,
            amount=amount,
            loan_type=loan_type,
            status="Pending"
        )

        return redirect("loan_officer_dashboard")

        return render(request, "accounts/add_loan.html")
        # 🔁 GO TO DASHBOARD AFTER ADDING
        return redirect("loan_officer_dashboard")

    return render(request, "add_loan.html")


def loan_officer_dashboard(request):

    loans = Loan.objects.all().order_by("-created_at")

    return render(request, "loan_officer_dashboard.html", {
        "loans": loans
    })


from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect("home")

def home(request):
    return render(request, "home.html")


from django.shortcuts import get_object_or_404, redirect
from .models import Loan

def loan_officer_approve(request, loan_id):

    loan = get_object_or_404(Loan, id=loan_id)

    loan.officer_approved = True
    loan.status = "Approved by Officer"
    loan.save()

    return redirect("loan_officer_dashboard")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Loan

@login_required
def branch_manager_dashboard(request):

    # ONLY show officer-approved loans
    loans = Loan.objects.filter(officer_approved=True).order_by("-created_at")

    return render(request, "branch_manager_dashboard.html", {
        "loans": loans
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Loan

@login_required
def csr_dashboard(request):

    loans = Loan.objects.all().order_by("-created_at")

    return render(request, "csr_dashboard.html", {
        "loans": loans
    })


from django.shortcuts import redirect

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Loan

@login_required
def create_loan(request):

    if request.method == "POST":

        username = request.POST.get("username")
        amount = request.POST.get("amount")
        loan_type = request.POST.get("loan_type")

        Loan.objects.create(
            username=username,
            amount=amount,
            loan_type=loan_type,
            status="Pending"
        )

        return redirect("csr_dashboard")

    # ✅ THIS FIXES YOUR ERROR (GET REQUEST)
    return render(request, "create_loan.html")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Loan

@login_required
def employee_dashboard(request):

    loans = Loan.objects.all().order_by("-created_at")

    return render(request, "employee_dashboard.html", {
        "loans": loans
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def user_dashboard(request):
    return render(request, "user_dashboard.html")
    return redirect("user_dashboard")


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Loan

@login_required
def apply_loan(request):

    if request.method == "POST":

        amount = request.POST.get("amount")
        loan_type = request.POST.get("loan_type")

        Loan.objects.create(
            username=request.user.username,
            amount=amount,
            loan_type=loan_type,
            status="Pending Verification"
        )

        messages.success(request, "Request received and sent for verification.")

        return redirect("user_dashboard")

    return render(request, "apply_loan.html")




from django.shortcuts import get_object_or_404

@login_required
def cancel_loan(request, loan_id):

    loan = get_object_or_404(Loan, id=loan_id)

    # 🔐 Only owner can cancel
    if loan.username != request.user.username:
        return redirect("user_dashboard")

    # ❌ Only allow cancel if still pending
    if loan.status in ["Pending", "Pending Verification"]:
        loan.status = "Cancelled"
        loan.save()

    return redirect("user_dashboard")


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Loan

@login_required
def user_dashboard(request):

    loans = Loan.objects.filter(username=request.user.username)

    return render(request, "user_dashboard.html", {
        "loans": loans
    })

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser


def loginn_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(username=username)

            # 🔒 BLOCKED USER (FIXED HERE)
            if user.is_locked:
                messages.error(request, "Account is locked. Contact admin.")
                return redirect("login")

            # 🚫 NOT APPROVED
            if not user.is_superuser and not user.is_approved:
                return redirect("security_admin")

        except CustomUser.DoesNotExist:
            return redirect("login")

        user_auth = authenticate(request, username=username, password=password)

        if user_auth:
            
            # ✅ RESET ATTEMPTS
            user.failed_attempts = 0
            user.save()

            login(request, user_auth)
        
            log_action(user_auth, "Logged in")

            if user_auth.is_superuser:
                return redirect("admin_dashboard")

            elif user_auth.role == "employee":
                return redirect("employee_dashboard")

            elif user_auth.role == "csr":
                return redirect("csr_dashboard")

            elif user_auth.role == "loan_officer":
                return redirect("loan_officer_dashboard")

            elif user_auth.role == "branch_manager":
                return redirect("branch_manager_dashboard")

        else:
            log_action(user, "Failed login attempt")
            # ❌ WRONG PASSWORD
            try:
                user.failed_attempts += 1

                if user.failed_attempts >= 3:
                    user.is_locked = True
                    log_action(user, "Account locked after 3 failed attempts")

                user.save()

            except:
                pass

            return redirect("login")

    return render(request, "login.html")

  
from django.contrib.auth.decorators import user_passes_test

def is_admin(user):
    return user.is_superuser

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CustomUser

@login_required
def admin_permissions(request):

    # 🔐 ONLY ADMIN
    if not request.user.is_superuser:
        return redirect("login")

    users = CustomUser.objects.filter(is_superuser=False).order_by("-last_login")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        user = CustomUser.objects.get(id=user_id)

        # 🔒 BLOCK USER
        if action == "lock":
            user.is_locked = True

        # 🔓 UNBLOCK USER
        elif action == "unlock":
            user.is_locked = False
            user.failed_attempts = 0

        user.save()

        return redirect("admin_permissions")

    return render(request, "admin_permissions.html", {"users": users})




from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def security_admin(request):
    users = CustomUser.objects.filter(failed_attempts=3)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        user = CustomUser.objects.get(id=user_id)

        if action == "block":
            user.is_locked = True

        elif action == "unblock":
            user.is_locked = False
            user.failed_attempts = 0

        user.save()

        return redirect("security_admin")

    return render(request, "security_alert.html", {"users": users})


from .utils import log_action


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from .utils import log_action


# ---------------- LOGOUT ----------------
def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "Logged out")

    logout(request)
    return redirect("login")


# ---------------- AUDIT LOG VIEW ----------------
@login_required
def audit_logs(request):

    # ONLY ADMIN (SUPERUSER)
    if not request.user.is_superuser:
        return redirect("login")

    logs = AuditLog.objects.all().order_by("-created_at")
    return render(request, "audit_logs.html", {"logs": logs})

def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, "Logged out")

    logout(request)
    return redirect("home")   # ✅ goes to home page


