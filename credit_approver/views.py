import datetime
from dateutil.relativedelta import relativedelta
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from credit_approver.models import CustomerData, LoanData

from credit_approver.utility import check_eligibility

@csrf_exempt
def register_view(request):
    try:
        if request.method == "PUT":
            data = json.loads(request.body)
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            monthly_salary = int(data.get("monthly_income"))
            phone_number = int(data.get("phone_number"))

            approved_limit = round(36*monthly_salary)

            # insert data into database with approved limit
            c_data = CustomerData()
            c_data.first_name = first_name
            c_data.last_name = last_name
            c_data.phone_number = phone_number
            c_data.monthly_salary = monthly_salary
            c_data.approved_limit = approved_limit
            c_data.save()

            data_dict = {
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone_number,
                "monthly_salary": monthly_salary,
                "approved_limit": approved_limit,
            }

            return JsonResponse({"status": "SUCCESS", "message": "Customer data saved!", "data": data_dict}, status=200)

        else:
            return JsonResponse({"Incorrect method called"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e), "status": "Failed"}, status=400)


@csrf_exempt
def eligibility_view(request):
    try:
        if request.method == 'GET':
            loan_data = json.loads(request.body)

            input_interest_rate = loan_data.get("interest_rate")
            customer_id = loan_data.get("customer_id")

            approval, corrected_interest_rate = check_eligibility(customer_id, input_interest_rate)

            if not approval:
                monthly_installment = None
            else:
                # simple interest formula
                monthly_installment = (loan_data.get("loan_amount") * (1+(corrected_interest_rate/100)))/int(loan_data.get("tenure"))

            data_dict = {
                "customer_id": loan_data.get("customer_id"),
                "approval": approval,
                "interest_rate": input_interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": loan_data.get("tenure"),
                "monthly_installment": monthly_installment,
            }

            return JsonResponse(
                {
                "status": "SUCCESS",
                "message": "Successfully invested customers eligibility",
                "data": data_dict
                }, status=200)

        else:
            return JsonResponse({"Incorrect method called"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e), "status": "Failed"}, status=400)

@csrf_exempt
def create_loan_view(request):
    try:
        if request.method == 'POST':
            loan_data = json.loads(request.body)

            input_interest_rate = loan_data.get("interest_rate")
            customer_id = loan_data.get("customer_id")

            approval, corrected_interest_rate = check_eligibility(customer_id, input_interest_rate)

            loan_id = None
            msg = ""

            if approval:
                # simple interest formula
                monthly_installment = (loan_data.get("loan_amount") * (1 + (corrected_interest_rate / 100))) / int(
                    loan_data.get("tenure"))

                cust_data = CustomerData.objects.get(customer_id=loan_data.get("customer_id"))

                loan_data_obj = LoanData()
                loan_data_obj.customer_id = cust_data
                loan_data_obj.interest_rate = corrected_interest_rate
                loan_data_obj.loan_amt = float(loan_data.get("loan_amount"))
                loan_data_obj.emi = monthly_installment
                loan_data_obj.tenure = int(loan_data.get("tenure"))
                loan_data_obj.total_timely_emi = 0
                loan_data_obj.approval_date = datetime.date.today()
                loan_data_obj.end_date = datetime.date.today() + relativedelta(months=int(loan_data.get("tenure")))
                loan_data_obj.save()

                loan_id = loan_data_obj.loan_id
            else:
                monthly_installment = None
                msg = "Loan not approved as credit score is less"

            data_dict = {
                "loan_id": loan_id,
                "customer_id": loan_data.get("customer_id"),
                "loan_approved": approval,
                "message": msg,
                "monthly_installment": monthly_installment,
            }

            return JsonResponse(
                {
                    "status": "SUCCESS",
                    "message": "Successfully completed loan creation process",
                    "data": data_dict
                }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e), "status": "Failed"}, status=400)

@csrf_exempt
def view_loan_by_customer_id(request):
    try:
        if request.method == "GET":
            if request.GET.get("customer_id") is not None:
                customer_id = request.GET.get("customer_id")

                loan_data = LoanData.objects.filter(customer_id=customer_id).values(
                    'loan_id',
                    'customer_id',
                    'loan_amt',
                    'interest_rate',
                    'emi',
                    'tenure'
                )
                return JsonResponse({
                    "status": "SUCCESS",
                    "message": "Loan details for given customer fetched!",
                    "data": list(loan_data)
                },status=200)
            else:
                return JsonResponse({"status": "FAILED", "message": "Invalid inputs provided. Please provide valid customer ID"}, status=200)
        else:
            return JsonResponse({"Incorrect method called"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e), "status": "Failed"}, status=400)

@csrf_exempt
def view_loan_by_loan_id(request):
    try:
        if request.method == "GET":
            if request.GET.get("loan_id") is not None:
                loan_id = request.GET.get("loan_id")

                loan_data = LoanData.objects.filter(loan_id=loan_id).values(
                    'loan_id',
                    'customer_id',
                    'loan_amt',
                    'interest_rate',
                    'emi',
                    'tenure'
                )
                return JsonResponse({
                    "status": "SUCCESS",
                    "message": "Loan details for given loan ID fetched!",
                    "data": list(loan_data)
                },status=200)
            else:
                return JsonResponse({"status": "FAILED", "message": "Invalid inputs provided. Please provide valid loan ID"}, status=200)
        else:
            return JsonResponse({"Incorrect method called"}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e), "status": "Failed"}, status=400)
