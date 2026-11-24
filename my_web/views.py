
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from random import randint
from .models import Task, EmailConfirm

User = get_user_model()



def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return redirect('registration')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('registration')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('registration')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        code = str(randint(100000, 999999))
        EmailConfirm.objects.update_or_create(user=user,defaults={'code': code})
        try:
            send_mail(
                'Confirm Your Email',
                f'Your verification code is: {code}',
                None,
                [email],
                fail_silently=False
            )
        except Exception:
            user.delete()
            messages.error(request, 'Email could not be sent.')
            return redirect('registration')
        request.session['confirm_username'] = username
        messages.success(
            request,
            'Verification code sent to your email.'
        )
        return redirect('confirm_email')
    return render(request, 'registration.html')




def confirm_email(request):
    if request.method == 'POST':
        username = request.session.get('confirm_username')
        code = request.POST.get('code', '').strip()
        if not username:
            messages.error(request, 'Please register first.')
            return redirect('registration')
        user = User.objects.filter(username=username).first()
        if not user:
            messages.error(request, 'User not found.')
            return redirect('registration')
        code_obj = EmailConfirm.objects.filter(user=user).first()
        if code_obj and code_obj.code == code:
            user.is_active = True
            user.save()
            code_obj.delete()
            login(request,user,backend='django.contrib.auth.backends.ModelBackend')
            request.session.pop('confirm_username', None)
            return redirect('dashboard')
        messages.error(request, 'Invalid verification code.')
    return render(request, 'confirm_email.html')




def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        messages.error(request,'Invalid username or password.')
    return render(request, 'login.html')





@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')




@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    if status in dict(Task.STATUS_CHOICES):
        tasks = tasks.filter(status=status)
    if priority in dict(Task.PRIORITY_CHOICES):
        tasks = tasks.filter(priority=priority)
    context = {
        'tasks': tasks,
        'search': search,
        'selected_status': status,
        'selected_priority': priority,
        'total_tasks': Task.objects.filter(
            user=request.user
        ).count(),
        'pending_tasks': Task.objects.filter(
            user=request.user,
            status='pending'
        ).count(),
        'finished_tasks': Task.objects.filter(
            user=request.user,
            status='finished'
        ).count(),

        'cancelled_tasks': Task.objects.filter(
            user=request.user,
            status='cancelled'
        ).count(),
    }
    return render(request, 'dashboard.html', context)




@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        priority = request.POST.get('priority', 'medium')
        deadline = request.POST.get('deadline', '')
        if not title:
            messages.error(request, 'Title is required.')
            return redirect('create_task')
        if priority not in dict(Task.PRIORITY_CHOICES):
            priority = 'medium'
        Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            priority=priority,
            deadline=parse_date(deadline) if deadline else None
        )
        messages.success(request, 'Task created successfully.')
        return redirect('dashboard')
    return render(request, 'create_task.html')



@login_required
def task_detail(request, pk):
    task = get_object_or_404( Task, pk=pk, user=request.user)
    return render(request,'task_detail.html',{'task': task})



@login_required
def edit_task(request, pk):
    task = get_object_or_404(Task,pk=pk,user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        priority = request.POST.get('priority', 'medium')
        status = request.POST.get('status', 'pending')
        deadline = request.POST.get('deadline', '')
        if not title:
            messages.error(request, 'Title is required.')
            return redirect('edit_task', pk=pk)
        if priority not in dict(Task.PRIORITY_CHOICES):
            priority = task.priority
        if status not in dict(Task.STATUS_CHOICES):
            status = task.status
        task.title = title
        task.description = request.POST.get('description', '')
        task.priority = priority
        task.status = status
        task.deadline = parse_date(deadline) if deadline else None
        task.save()
        messages.success(request, 'Task updated successfully.')
        return redirect('dashboard')
    return render( request, 'edit_task.html', {'task': task})





@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task,pk=pk,user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully.')
    return redirect('dashboard')




@login_required
def finish_task(request, pk):
    task = get_object_or_404(Task,pk=pk,user=request.user)
    if request.method == 'POST':
        task.status = 'finished'
        task.save()
        messages.success(request, 'Task finished successfully.')
    return redirect('dashboard')




@login_required
def cancel_task(request, pk):
    task = get_object_or_404(Task,pk=pk,user=request.user)
    if request.method == 'POST':
        task.status = 'cancelled'
        task.save()
        messages.success(request, 'Task cancelled.')
    return redirect('dashboard')




@login_required
def profile(request):
    tasks = Task.objects.filter(user=request.user)
    context = {'user': request.user,'tasks': tasks,'total_tasks': tasks.count(),'finished_tasks': tasks.filter(status='finished').count(),
        'pending_tasks': tasks.filter(status='pending').count(),}
    return render(request, 'profile.html', context)



@login_required
@user_passes_test(lambda user: user.is_staff)
def send_announcement(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        if not subject or not message:
            messages.error(request, 'All fields are required.')
            return redirect('send_announcement')
        emails = User.objects.filter(is_active=True).exclude(
            email=''
        ).values_list('email', flat=True)
        sent_count = 0
        for email in emails:
            try:
                send_mail(  subject,  message,  None,  [email],  fail_silently=False)
                sent_count += 1
            except Exception:
                continue
        messages.success(request,f'Email sent successfully to {sent_count} users.')
        return redirect('dashboard')
    return render(request, 'send_announcement.html')
