from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import csv
from .models import Company

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES['csv_file']:
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage()
        filename = fs.save(csv_file.name, csv_file)
        uploaded_file_url = fs.url(filename)
        
        with open(fs.path(filename), newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Company.objects.create(
                    name=row['name'],
                    address=row['address'],
                    city=row['city'],
                    state=row['state'],
                    country=row['country'],
                    website=row['website']
                )
        
        return render(request, 'upload.html', {'uploaded_file_url': uploaded_file_url})
    return render(request, 'upload.html')

@login_required
def query_builder(request):
    if request.method == 'POST':
        name_filter = request.POST.get('name', '')
        city_filter = request.POST.get('city', '')
        state_filter = request.POST.get('state', '')
        country_filter = request.POST.get('country', '')
        
        companies = Company.objects.all()
        
        if name_filter:
            companies = companies.filter(name__icontains=name_filter)
        if city_filter:
            companies = companies.filter(city__icontains=city_filter)
        if state_filter:
            companies = companies.filter(state__icontains=state_filter)
        if country_filter:
            companies = companies.filter(country__icontains=country_filter)
        
        count = companies.count()
        return render(request, 'query_builder.html', {'count': count, 'companies': companies})
    
    return render(request, 'query_builder.html')
