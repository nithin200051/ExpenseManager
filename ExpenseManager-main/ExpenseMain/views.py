from django.shortcuts import render,redirect
from .models import *
from dateutil.parser import parse
from django.utils import timezone
import json
from django.template.defaultfilters import date as django_date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse,HttpResponse
import csv
import datetime
import xlwt
from validate_email import validate_email
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import re
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent



# Create your views here.
def index(request):
    return render(request,'index.html')


def signup(request):
    if request.method=='GET':
        return render(request,'signup.html')
    else:
        name=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        if UserDetail.objects.filter(email=email) or UserDetail.objects.filter(name=name):
            msg = {'msg1' : 'Username or Email already exists!'}
            return render(request, 'signup.html', msg)
        else:
            userData=UserDetail(name=name,email=email,password=password)
            userData.save()
            return render(request,'index.html')
    

def login(request):
    if request.method=='GET':
        return render(request,'login.html')
    else:
        email=request.POST.get('email')
        password=request.POST.get('password')
        userData=UserDetail.objects.filter(email=email,password=password)
        print(userData)
        if userData.filter(email=email,password=password).exists():
            request.session['email']=userData[0].email
            request.session['user_id']=userData[0].id
            request.session['user_name']=userData[0].name
            return redirect("/home")
        else:
            msg={'msg1':"Invalid Username or password!"}
            return render(request,'login.html',msg)


def home(request):
    context={}
    if 'user_id' in request.session:
        user_name=UserDetail.objects.get(email=request.session['email']).name 
        if request.session['user_id']!='':
            context={'user_name':user_name}
        else:
            context={'user_name':''}
        return render(request,'home.html',context)
    else:
        return redirect('/login')

def incomeCalendarView(request):
    incomes=Income.objects.filter(owner=request.session['user_id'])
    event_list=[]
    for income in incomes:
        event_list.append({
            'title':income.description,
            'start':income.date.isoformat(),
            'end':income.date.isoformat(),
        })
    return JsonResponse(event_list,safe=False)


def expenseCalendarView(request):
    expenses=Expense.objects.filter(owner=request.session['user_id'])
    event_list=[]
    for expense in expenses:
        event_list.append({
            'title':expense.description,
            'start':expense.date.isoformat(),
            'end':expense.date.isoformat()
        })
    return JsonResponse(event_list,safe=False)


def profile_settings(request):
    if 'user_id' in request.session:
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        if request.method=='GET':
            context={
                'userDetails':userDetails,
                'user_name':request.session['user_name']
            }
            return render(request,'profile.html',context)
        else:
            user_name=request.POST.get('username')
            password=request.POST.get('password')
            userDetails.name=user_name
            userDetails.password=password
            userDetails.save()
            return redirect('home')
    else:
        return redirect('/login')



def currency_settings(request):
    if 'user_id' in request.session:

        currency_data=[]
        userDetails=UserDetail.objects.get(id=request.session['user_id'])
        file_path=BASE_DIR/'currencies.json'

        with open(file_path,'r') as json_file:
            print(json_file)
            data=json.load(json_file)
            for k,v in data.items():
                currency_data.append({'name':k,'value':v})
        exists=UserPreference.objects.filter(user=request.session['user_id']).exists()
        user_preference=None
        if exists:
            user_preference=UserPreference.objects.get(user=userDetails)
        if request.method=='GET':
            return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
        else:
            currency=request.POST.get('currency')
            #checking if user has already a preference
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=request.POST.get('currency')
                user_preference.currency=currency
                user_preference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
            else:
                savePreference=UserPreference.objects.create(user=userDetails,currency=currency)
                savePreference.save()
                return render(request,'preferences.html',{'currencies':currency_data,'user_preferences':user_preference,'user_name':request.session['user_name']})
    else:
        return redirect('/login')

def expense(request):
    if 'user_id' in request.session:

        if request.method=='GET':
            userDetails=UserDetail.objects.get(id=request.session['user_id'])
            currency=''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=UserPreference.objects.get(user=userDetails).currency
            expenses=Expense.objects.filter(owner=userDetails)
            paginator=Paginator(expenses,5)
            page_number=request.GET.get('page')
            page_obj=Paginator.get_page(paginator,page_number)
            context={
                'expenses':expenses,
                'currency':currency,
                'page_obj':page_obj,
                'user_name':request.session['user_name']
            }
            return render(request,'expenses.html',context)
    else:
        return redirect('/login')
    

def addExpense(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='GET':
        # categories=Category.objects.all()
        context={
            # 'categories':categories,
            'user_name':request.session['user_name']

        }
        return render(request,'add_expense.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        category=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        print(amount,description,category,date)
        expense=Expense.objects.create(amount=amount,description=description,category=category.upper(),date=date,owner=userDetails)
        expense.save()
        return redirect('expense')
    

def editExpense(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expense=Expense.objects.get(pk=id)
    # categories=Category.objects.all()
    if request.method=='GET':
        context={
            'expense':expense,
            # 'categories':categories,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_expense.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        category=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        print(amount,description,category,date)
        expense.amount=amount
        expense.description=description
        expense.category=category.upper()
        expense.date=date
        expense.owner=userDetails
        expense.save()
        return redirect('expense')
    

def deleteExpense(request,id):
    expense=Expense.objects.get(pk=id)
    expense.delete()
    return redirect('expense')
        


def searchExpense(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Expense.objects.filter(
            description__icontains=search_str, owner=userDetails) | Expense.objects.filter(
            category__icontains=search_str, owner=userDetails)
        data=expenses.values()
        return JsonResponse(list(data),safe=False)
    


def income(request):
    if 'user_id' in request.session:

        if request.method=='GET':
            userDetails=UserDetail.objects.get(id=request.session['user_id'])
            currency=''
            if UserPreference.objects.filter(user=userDetails).exists():
                currency=UserPreference.objects.get(user=userDetails).currency
            incomes=Income.objects.filter(owner=userDetails)
            paginator=Paginator(incomes,5)
            page_number=request.GET.get('page')
            page_obj=Paginator.get_page(paginator,page_number)
            context={
                'incomes':incomes,
                'currency':currency,
                'page_obj':page_obj,
                'user_name':request.session['user_name']

            }
            return render(request,'incomes.html',context)
    else:
        return redirect('/login')
    

def addIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='GET':
        # sources=Source.objects.all()
        context={
            # 'sources':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'add_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income=Income.objects.create(amount=amount,description=description,source=source.upper(),date=date,owner=userDetails)
        income.save()
        return redirect('income')
    

def editIncome(request,id):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    income=Income.objects.get(pk=id)
    # sources=Source.objects.all()
    if request.method=='GET':
        context={
            'income':income,
            # 'categories':sources,
            'user_name':request.session['user_name']

        }
        return render(request,'edit_income.html',context)
    else:
        amount=request.POST.get('amount')
        description=request.POST.get('description')
        source=request.POST.get('category')
        date=request.POST.get('date_of_expense')
        income.amount=amount
        income.description=description
        income.category=source.upper()
        income.date=date
        income.owner=userDetails
        income.save()
        return redirect('income')
    

def deleteIncome(request,id):
    income=Income.objects.get(pk=id)
    income.delete()
    return redirect('income')
        


def searchIncome(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        # income=Income.objects.filter(amount__istarts_with=search_str,owner=userDetails) | Income.objects.filter(date_istarts_with=search_str,owner=userDetails)| Income.objects.filter(description__icontains=search_str,owner=userDetails)| Income.objects.filter(category_icontains=search_str,owner=userDetails)
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            date__istartswith=search_str, owner=userDetails) | Income.objects.filter(
            description__icontains=search_str, owner=userDetails) | Income.objects.filter(
            source__icontains=search_str, owner=userDetails)
        data=income.values()
        return JsonResponse(list(data),safe=False)
    

def expenseCategorySummary(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    todaysDate=datetime.date.today()
    sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
    expenses=Expense.objects.filter(owner=userDetails,date__gte=sixMonthsAgo,date__lte=todaysDate)
    finalRepresentation={

    }

    def getCategory(expense):
        return expense.category
    categoryList=list(set(map(getCategory,expenses)))

    def getExpenseCategoryAmount(category):
        amount=0
        filtered_by_category=expenses.filter(category=category)
        for item in filtered_by_category:
            amount+=item.amount
        return amount

    for x in expenses:
        for y in categoryList:
            finalRepresentation[y]=getExpenseCategoryAmount(y)
    return JsonResponse({'expense_category_data':finalRepresentation},safe=False)


# def customIncomeDate(request):
#     fromDate=request.POST.get("fromDate")
#     toDate=request.POST.get('toDate')
#     print(fromDate,toDate)
#     incomeCategorySummary(request,fromDate,toDate)
#     return redirect('/income_stats')

def incomeCategorySummary(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    todaysDate=datetime.date.today()
    sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
    incomes=Income.objects.filter(owner=userDetails,date__gte=sixMonthsAgo,date__lte=todaysDate)
    finalRepresentation={

    }

    def getCategory(incomes):
        return incomes.source
    categoryList=list(set(map(getCategory,incomes)))


    def getIncomeCategoryAmount(source):
        amount=0
        filtered_by_category=incomes.filter(source=source)
        for item in filtered_by_category:
            amount+=item.amount
        return amount
    for x in incomes:
        for y in categoryList:
            finalRepresentation[y]=getIncomeCategoryAmount(y)
    return JsonResponse({'income_category_data':finalRepresentation},safe=False)

# def incomeStatsView(request):
#     if 'user_id' in request.session :
#         todaysDate=datetime.date.today()
#         sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
#         context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
#         return render(request,'incomeStats.html',context)
#     else:
#         return redirect('/login')

def incomeStatsView(request):
    if 'user_id' in request.session :
        todaysDate=timezone.localdate()
        sixMonthsAgo=todaysDate-datetime.timedelta(days=30*6)
        context={'user_name':request.session['user_name'],'from':sixMonthsAgo,'to':todaysDate}
        return render(request,'incomeStats.html',context)
    else:
        return redirect('/login')


def expenseStatsView(request):
    if 'user_id' in request.session:
        context={'user_name':request.session['user_name']}
        return render(request,'expenseStats.html',context)
    else:
        return redirect('/login')


def exportincomeCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])
    incomes=Income.objects.filter(owner=userDetails)
    for income in incomes:
        writer.writerow([income.amount,income.description,income.source,income.date])
    return response


def exportCSV(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.csv'
    writer=csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])
    expenses=Expense.objects.filter(owner=userDetails)
    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])
    return response


def exportincomeExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Source','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Income.objects.filter(owner=userDetails).values_list('amount','description','source','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response

def exportExcel(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    response=HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition']='attachment; filename=Expenses'+str(datetime.datetime.now())+'.xls'
    wb=xlwt.Workbook(encoding='utf-8')
    ws=wb.add_sheet('Expenses')
    row_num=0
    font_style=xlwt.XFStyle()
    font_style.font.bold=True
    columns=['Amount','Description','Category','Date']
    for col_num in range(len(columns)):
        ws.write(row_num,col_num,columns[col_num],font_style)

    font_style=xlwt.XFStyle()
    rows=Expense.objects.filter(owner=userDetails).values_list('amount','description','category','date')

    for row in rows:
        row_num+=1
        for col_num in range(len(row)):
            ws.write(row_num,col_num,str(row[col_num]),font_style)
    wb.save(response)
    return response


def exportincomePdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    incomes=Income.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Source','Description']]
    for income in incomes:
        data.append([income.amount,income.date,income.source,income.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response

def exportPdf(request):
    userDetails=UserDetail.objects.get(id=request.session['user_id'])
    expenses=Expense.objects.filter(owner=userDetails)
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment;filename="expense.pdf"'
    doc=SimpleDocTemplate(response,pagesize=letter)
    elements=[]

    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ])

    data=[['Amount','Date','Category','Description']]
    for expense in expenses:
        data.append([expense.amount,expense.date,expense.category,expense.description])
    table=Table(data)
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response


def profileValidateUsername(request):
        if request.method=='POST':
            data=json.loads(request.body)
            search_str=data['username']
            if not str(search_str).isalnum():
                return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
            if UserDetail.objects.filter(name=search_str).exists():
                 return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


def validateUserName(request):
    if request.method=='POST':
        data=json.loads(request.body)
        search_str=data['username']
        if not str(search_str).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if UserDetail.objects.filter(name=search_str).exists():
                return JsonResponse({'username_error': 'sorry username is in use,choose another one '}, status=409)
    return JsonResponse({'username_valid': True})


def validateUserEmail(request):
    if request.method=='POST':
        data=json.loads(request.body)
        email=data['email']
        if not validate_email(email):
                return JsonResponse({'email_error':'Email is invalid'},status=400)
        if UserDetail.objects.filter(email=email).exists():
                return JsonResponse({'email_error':'Email already exists. please choose another name.'},status=400)
    return JsonResponse({'email_valid':True})


def logout(request):
        if 'user_id' not in request.session or 'user_name' not in request.session :
            return redirect('/login')
   
        del request.session['user_name']

        del request.session['user_id']
    # except:
    #     return index(request)
    
        return redirect('login')



    

