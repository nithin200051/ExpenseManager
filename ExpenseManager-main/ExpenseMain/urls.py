from .views import *
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


urlpatterns = [
    path('',index,name="index"),
    path('signup',signup,name="signup"),
    path('login',login,name='login'),
    path('home',home,name='home'),
    path('account_settings',currency_settings,name='account_settings'),
    path('expense',expense,name='expense'),
    path('addExpense',addExpense,name='addExpense'),
    path('editExpense/<int:id>',editExpense,name='editExpense'),
    path('deleteExpense/<int:id>',deleteExpense,name='deleteExpense'),
    path('searchExpense',csrf_exempt(searchExpense),name='searchExpense'),
    path('validateUserName',csrf_exempt(validateUserName),name='validateUserName'),
    path('validateUserEmail',csrf_exempt(validateUserEmail),name='validateUserEmail'),
    path('income',income,name='income'),
    path('addIncome',addIncome,name='addIncome'),
    path('editIncome/<int:id>',editIncome,name='editIncome'),
    path('deleteIncome/<int:id>',deleteIncome,name='deleteIncome'),
    path('searchIncome',csrf_exempt(searchIncome),name='searchIncome'),
    path('incomeCategorySummary',incomeCategorySummary,name='incomeCategorySummary'),
    # path('customIncomeDate',views.customIncomeDate,name='customIncomeDate'),
    path('expenseCategorySummary',expenseCategorySummary,name='expenseCategorySummary'),
    path('income_stats',incomeStatsView,name='income_stats'),
    path('expense_stats',expenseStatsView,name='expense_stats'),
    path('exportincomeCSV',exportincomeCSV,name='exportincomeCSV'),
    path('exportincomeExcel',exportincomeExcel,name='exportincomeExcel'),
    path('exportincomePdf',exportincomePdf,name='exportincomePdf'),
    path('exportCSV',exportCSV,name='exportCSV'),
    path('exportExcel',exportExcel,name='exportExcel'),
    path('exportPdf',exportPdf,name='exportPdf'),
    path('profile_settings',profile_settings,name='profile_settings'),
    path('profileValidateUsername',csrf_exempt(profileValidateUsername),name='profileValidateUsername'),
    path('incomeCalendarView',incomeCalendarView,name='incomeCalendarView'),
    path('expenseCalendarView',expenseCalendarView,name='expenseCalendarView'),
    path('logout',logout,name='logout')
]


