from django import forms
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
        }

class CreateRecordForm(forms.Form):
    diagnosis = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    treatment =forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    notes = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    report = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

       
        
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser 
        fields = ['full_name', 'username','email','password', 'phone_number',  'date_of_birth', 'gender']  
        widgets = {
            'password': forms.PasswordInput(),  
        }

