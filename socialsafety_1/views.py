from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def fun_1(request):
    return HttpResponse("hello world ")