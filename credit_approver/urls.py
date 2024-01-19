"""
URL configuration for credit_approver_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from credit_approver.views import register_view, eligibility_view, create_loan_view, view_loan_by_loan_id, view_loan_by_customer_id

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'register$', register_view, name="register"),
    re_path(r'check-eligibility$', eligibility_view, name='check_eligibility'),
    re_path(r'create-loan$', create_loan_view, name='create_loan'),
    re_path(r'view-loan$', view_loan_by_loan_id, name='view_loan'),
    re_path(r'view-loans$', view_loan_by_customer_id, name='view_loan'),
]
