from django.db import models


class CustomerData(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    phone_number = models.IntegerField(null=False, blank=False)
    monthly_salary = models.FloatField(max_length=50, null=True, blank=True)
    approved_limit = models.IntegerField(null=True, blank=True)
    current_debt = models.FloatField(max_length=50, null=True, blank=True)


class LoanData(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(CustomerData, on_delete=models.CASCADE)
    loan_amt = models.FloatField(max_length=50, null=False, blank=False)
    tenure = models.FloatField(max_length=50, null=False, blank=False)
    interest_rate = models.FloatField(max_length=5, null=False, blank=False)
    emi = models.FloatField(max_length=50, null=False, blank=False)
    total_timely_emi = models.IntegerField(null=True, blank='True')
    approval_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)

    # past_loan = LoanData.objects.filter
