from django.shortcuts import render

def index(request):
    """
    The Global Central Hub for the Upzunction platform.
    """
    return render(request, 'index.html')