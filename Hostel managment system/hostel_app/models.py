from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    reg_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.course_name

class Room(models.Model):
    room_no = models.CharField(max_length=10, unique=True)
    semester = models.CharField(max_length=20)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    posting_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.room_no

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    regno = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    personal_details = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.CharField(max_length=50, blank=True, null=True)
    food = models.BooleanField(default=False)
    parent_name = models.CharField(max_length=100, blank=True, null=True)
    parent_contact = models.CharField(max_length=20, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)
    proctor_name = models.CharField(max_length=100, blank=True, null=True)
    proctor_contact = models.CharField(max_length=20, blank=True, null=True)
    hostel_incharge_name = models.CharField(max_length=100, blank=True, null=True)
    hostel_incharge_contact = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.full_name

class Permission(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()
    date_out = models.DateTimeField()
    date_in = models.DateTimeField()
    parent_permission = models.BooleanField(default=False)
    proctor_permission = models.BooleanField(default=False)
    incharge_permission = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Permission for {self.student.full_name}"
