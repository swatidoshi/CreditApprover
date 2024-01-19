from credit_approver.models import CustomerData, LoanData
from datetime import date
from django.db.models.functions import Cast
from django.db.models import DateField



def check_eligibility(customer_id, input_interest_rate):
    cust_data = CustomerData.objects.get(customer_id=customer_id)

    cust_loan_data = LoanData.objects.annotate(
            edd=Cast('end_date', DateField()),
            add=Cast('approval_date', DateField())
        ).filter(customer_id=customer_id).values()

    curr_loan_data = []
    if len(cust_loan_data) > 0:
        # curr_loan_data = (cust_loan_data.end_date > date.today()) and (cust_loan_data.approval_date <= date.today())

        curr_loan_data = LoanData.objects.annotate(
            edd=Cast('end_date', DateField()),
            add=Cast('approval_date', DateField())
        ).filter(
                customer_id=customer_id,
                edd__gte=date.today(),
                add__lte=date.today()
        ).values()

    credit_score = 0
    if len(cust_loan_data) > 0:
        # CONDITION 1
        timely_paid_past_loan = True
        past_loan_taken = False
        good_vol_loan = False
        total_loan_amt = 0
        total_emi = 0

        for each_loan in cust_loan_data:
            if each_loan['edd'] <= date.today() and each_loan['total_timely_emi'] != each_loan['tenure']:
                timely_paid_past_loan = False

            if each_loan['edd'] <= date.today():
                past_loan_taken = True

            # here I am assuming 5L as good volume of loan taken by customer. IF so he can get good credit score
            if each_loan['loan_amt'] > 500000:
                good_vol_loan = True

        for each_curr_loan in curr_loan_data:
            total_loan_amt += each_curr_loan['loan_amt']
            total_emi += each_curr_loan['emi']

        if timely_paid_past_loan:
            credit_score += 20

        # CONDITION 2
        if past_loan_taken:
            credit_score += 20

        # CONDITION 3
        if len(curr_loan_data) > 0:
            credit_score += 20

        # CONDITION 4
        if good_vol_loan:
            credit_score += 20

        # CONDITION 5
        if total_loan_amt > cust_data.approved_limit:
            credit_score = 0

    if credit_score > 50:
        approval = True
        corrected_interest_rate = input_interest_rate
    elif 30 < credit_score < 50:
        approval = True
        corrected_interest_rate = 12
    elif 10 < credit_score < 30:
        approval = True
        corrected_interest_rate = 16
    else:
        approval = False
        corrected_interest_rate = None

    if len(curr_loan_data) > 0 and (total_emi > (cust_data.monthly_salary * 0.5)):
        approval = False
        corrected_interest_rate = None

    return approval, corrected_interest_rate
