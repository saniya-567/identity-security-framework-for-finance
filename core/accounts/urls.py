from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-employees/', views.manage_employees, name='manage_employees'),
    path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup, name='signup'),
    path('loan-officer-dashboard/', views.loan_officer_dashboard, name="loan_officer_dashboard"),
    path('loan-action/<int:id>/<str:action>/', views.update_loan_status, name="loan_action"),
    path('change-password/', views.change_password, name="change_password"),
    path('loan-officer-dashboard/', views.loan_officer_dashboard, name="loan_officer_dashboard"),
    path('add-loan/', views.add_loan, name="add_loan"),
    path('loan-action/<int:id>/<str:action>/', views.update_loan_status, name="loan_action"),
    path('add-loan/', views.add_loan, name="add_loan"),
    path('add-loan/', views.add_loan, name="add_loan"),
    path('loan-dashboard/', views.loan_officer_dashboard, name="loan_officer_dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home, name="home"),
    path("loan-officer-approve/<int:loan_id>/", views.loan_officer_approve, name="loan_officer_approve"),
    path("branch-dashboard/", views.branch_manager_dashboard, name="branch_manager_dashboard"),
    path("csr-dashboard/", views.csr_dashboard, name="csr_dashboard"),
    path("create-loan/", views.create_loan, name="create_loan"),
    path("employee-dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),
    path("user-dashboard/", views.user_dashboard, name="user_dashboard"),
    path("apply-loan/", views.apply_loan, name="apply_loan"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('admin-permissions/', views.admin_permissions, name='admin_permissions'),
    path('security-admin/', views.security_admin, name='security_admin'),
    path("audit-logs/", views.audit_logs, name="audit_logs"),
    path("cancel-loan/<int:loan_id>/", views.cancel_loan, name="cancel_loan"),
    path("", views.home, name="home")
    
]

