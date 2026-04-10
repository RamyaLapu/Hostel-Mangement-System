from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Student, Course, Room, Permission
from .forms import StudentRegistrationForm, CourseForm, RoomForm, PermissionForm

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful!')
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    login_role = 'student'
    if request.method == 'POST':
        login_role = request.POST.get('login_role', 'student')
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if login_role == 'admin':
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Account is not authorized for admin access.')
            else:
                if user.is_staff:
                    messages.error(request, 'Account is not authorized for student access.')
                else:
                    try:
                        student = Student.objects.get(user=user)
                        login(request, user)
                        return redirect('student_dashboard')
                    except Student.DoesNotExist:
                        messages.error(request, 'Student profile not found. Please contact admin.')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html', {'login_role': login_role})

def forgot_password(request):
    if request.method == 'POST':
        if 'new_password' in request.POST:
            email = request.POST.get('email')
            new_password = request.POST['new_password']
            confirm_password = request.POST['confirm_password']
            if new_password == confirm_password:
                try:
                    user = User.objects.get(email=email)
                    user.set_password(new_password)
                    user.save()
                    context = {'success': True}
                    return render(request, 'forgot_password.html', context)
                except User.DoesNotExist:
                    messages.error(request, 'Error: User not found.')
                except Exception as e:
                    messages.error(request, f'Error updating password: {str(e)}')
            else:
                messages.error(request, 'Passwords do not match.')
                context = {'show_form': True, 'email': email}
                return render(request, 'forgot_password.html', context)
        elif 'email' in request.POST:
            email = request.POST['email']
            try:
                user = User.objects.get(email=email)
                context = {'show_form': True, 'email': email}
                return render(request, 'forgot_password.html', context)
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    return render(request, 'forgot_password.html')

@login_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    permissions = Permission.objects.filter(student=student).order_by('-date_out')
    return render(request, 'student_dashboard.html', {
        'student': student,
        'permissions': permissions,
    })

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
    total_students = Student.objects.count()
    total_rooms = Room.objects.count()
    total_courses = Course.objects.count()
    return render(request, 'admin_dashboard.html', {
        'total_students': total_students,
        'total_rooms': total_rooms,
        'total_courses': total_courses,
    })

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Password changed successfully')
            return redirect('login')
        else:
            messages.error(request, 'Old password is incorrect')
    return render(request, 'change_password.html')

@login_required
def my_profile(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'my_profile.html', {'student': student})

@login_required
def student_profile(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'student_profile.html', {'student': student})

@login_required
def my_room(request):
    student = get_object_or_404(Student, user=request.user)
    return render(request, 'my_room.html', {'student': student})

@login_required
def book_hostel(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        room_id = request.POST['room']
        room = get_object_or_404(Room, id=room_id)
        student.room = room
        student.save()
        messages.success(request, 'Room booked successfully')
        return redirect('student_dashboard')
    rooms = Room.objects.filter(student__isnull=True)
    return render(request, 'book_hostel.html', {'rooms': rooms})

@login_required
def room_details(request):
    student = get_object_or_404(Student, user=request.user)
    # Only show the current student's room details
    students = Student.objects.filter(id=student.id, room__isnull=False)
    return render(request, 'room_details.html', {'students': students})

@login_required
def manage_students(request):
    if not request.user.is_staff:
        return redirect('home')
    students = Student.objects.all()
    return render(request, 'manage_students.html', {'students': students})

@login_required
def manage_rooms(request):
    if not request.user.is_staff:
        return redirect('home')
    rooms = Room.objects.all()
    return render(request, 'manage_rooms.html', {'rooms': rooms})

@login_required
def manage_courses(request):
    if not request.user.is_staff:
        return redirect('home')
    courses = Course.objects.all()
    return render(request, 'manage_courses.html', {'courses': courses})

@login_required
def add_course(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            student = form.cleaned_data.get('student')
            if student:
                student.course = course
                student.save()
            return redirect('manage_courses')
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    if not request.user.is_staff:
        return redirect('home')
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('manage_courses')
    else:
        form = CourseForm(instance=course)
    return render(request, 'edit_course.html', {'form': form})

@login_required
def delete_course(request, course_id):
    if not request.user.is_staff:
        return redirect('home')
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    return redirect('manage_courses')

@login_required
def add_room(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            student = form.cleaned_data.get('student')
            if student:
                student.room = room
                student.save()
            return redirect('manage_rooms')
    else:
        form = RoomForm()
    return render(request, 'add_room.html', {'form': form})

@login_required
def edit_room(request, room_id):
    if not request.user.is_staff:
        return redirect('home')
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('manage_rooms')
    else:
        form = RoomForm(instance=room)
    return render(request, 'edit_room.html', {'form': form})

@login_required
def delete_room(request, room_id):
    if not request.user.is_staff:
        return redirect('home')
    room = get_object_or_404(Room, id=room_id)
    room.delete()
    return redirect('manage_rooms')

@login_required
def add_student(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_students')
    else:
        form = StudentRegistrationForm()
    return render(request, 'add_student.html', {'form': form})

@login_required
def edit_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('manage_students')
    else:
        form = StudentRegistrationForm(instance=student)
    return render(request, 'edit_student.html', {'form': form})

@login_required
def delete_student(request, student_id):
    if not request.user.is_staff:
        return redirect('home')
    student = get_object_or_404(Student, id=student_id)
    student.user.delete()
    return redirect('manage_students')

@login_required
def request_permission(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            perm = form.save(commit=False)
            perm.student = student
            perm.save()
            messages.success(request, 'Permission requested')
            return redirect('student_dashboard')
    else:
        form = PermissionForm()
    return render(request, 'request_permission.html', {'form': form})

@login_required
def manage_permissions(request):
    if not request.user.is_staff:
        return redirect('home')
    if request.method == 'POST':
        perm_id = request.POST.get('perm_id')
        remark = request.POST.get('remark')
        if perm_id and remark is not None:
            perm = get_object_or_404(Permission, id=perm_id)
            perm.remark = remark
            perm.save()
            messages.success(request, 'Remark updated successfully.')
        return redirect('manage_permissions')
    permissions = Permission.objects.all()
    return render(request, 'manage_permissions.html', {'permissions': permissions})

@login_required
def approve_permission(request, perm_id):
    if not request.user.is_staff:
        return redirect('home')
    perm = get_object_or_404(Permission, id=perm_id)
    perm.parent_permission = True
    perm.proctor_permission = True
    perm.incharge_permission = True
    perm.status = 'approved'
    perm.save()
    return redirect('manage_permissions')
