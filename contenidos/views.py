from django.shortcuts import render

# Create your views here.
def apuntes(request):
    return render(request, 'apuntes/apuntes.html', {})