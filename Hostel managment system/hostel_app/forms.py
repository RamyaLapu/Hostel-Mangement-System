from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Student, Course, Room, Permission

class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Student
        fields = ['regno', 'full_name', 'last_name', 'date_of_birth', 'personal_details', 'image', 'course', 'duration', 'food', 'parent_name', 'parent_contact', 'parent_email', 'proctor_name', 'proctor_contact', 'hostel_incharge_name', 'hostel_incharge_contact']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'personal_details': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields not required for basic registration
        optional_fields = [
            'personal_details', 'image', 'course', 'duration',
            'parent_name', 'parent_contact', 'parent_email',
            'proctor_name', 'proctor_contact',
            'hostel_incharge_name', 'hostel_incharge_contact'
        ]
        for field_name in optional_fields:
            self.fields[field_name].required = False

        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.update({'class': 'form-control'})
            else:
                widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self, commit=True):
        try:
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['full_name'],
                last_name=self.cleaned_data['last_name']
            )
            student = super().save(commit=False)
            student.user = user
            if commit:
                student.save()
            return student
        except Exception as e:
            # If user creation fails, clean up and raise error
            if 'user' in locals():
                user.delete()
            raise forms.ValidationError(f"Registration failed: {str(e)}")

class StudentChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.full_name} ({obj.user.email})"

class CourseForm(forms.ModelForm):
    student = StudentChoiceField(queryset=Student.objects.all(), required=False, label='Student')

    class Meta:
        model = Course
        fields = ['course_name', 'student']

    def save(self, commit=True):
        course = super().save(commit=False)
        if not getattr(course, 'course_code', None):
            base_code = slugify(course.course_name or 'course').upper().replace('-', '_')[:8] or 'COURSE'
            code = base_code
            suffix = 1
            while Course.objects.filter(course_code=code).exists():
                code = f"{base_code[:7]}{suffix}"
                suffix += 1
            course.course_code = code
        if commit:
            course.save()
        return course

class RoomForm(forms.ModelForm):
    student = StudentChoiceField(queryset=Student.objects.all(), required=False, label='Student')

    class Meta:
        model = Room
        fields = ['room_no', 'fee', 'student']

    def save(self, commit=True):
        room = super().save(commit=False)
        # Keep semester blank when not used in the form
        if not hasattr(room, 'semester') or room.semester is None:
            room.semester = ''
        if commit:
            room.save()
        return room

class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['reason', 'date_out', 'date_in']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
            'date_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_out = cleaned_data.get('date_out')
        date_in = cleaned_data.get('date_in')
        if date_out and date_in and date_in <= date_out:
            raise forms.ValidationError("Return date must be after the out date.")
        if date_out:
            from django.utils import timezone
            if date_out <= timezone.now():
                raise forms.ValidationError("Out date must be in the future.")
            # Make datetime timezone-aware if it's naive
            if timezone.is_naive(date_out):
                cleaned_data['date_out'] = timezone.make_aware(date_out)
            if date_in and timezone.is_naive(date_in):
                cleaned_data['date_in'] = timezone.make_aware(date_in)
        return cleaned_data