from django import forms
from django.contrib.auth.hashers import make_password
from .models import CustomUser 

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser 

        fields = ['full_name', 'username', 'email', 'phone_number', 'password','specialization', 'date_of_birth', 'gender'] 
        widgets = {
            'password': forms.PasswordInput(),  
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.password = make_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user

class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser 
        fields = ['full_name', 'username','email','password', 'phone_number',  'date_of_birth', 'gender']  
        widgets = {
            'password': forms.PasswordInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),  
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data["password"]:
            user.password = make_password(self.cleaned_data["password"])  # Hash the password
        if commit:
            user.save()
        return user

from django import forms
from .models import MedicalRecord 

class CreateRecordForm(forms.ModelForm):  # Change to ModelForm
    class Meta:
        model = MedicalRecord  # Specify the model
        fields = ['diagnosis', 'treatment', 'notes', 'report']  # Specify the fields to include
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-control'}),
            'treatment': forms.TextInput(attrs={'class': 'form-control'}),
            'report': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }