from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from ..forms import LoginForm

class UserLoginView(View):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_superuser:
                    return redirect('/admin')
                elif hasattr(user, 'is_admin') and user.is_admin():
                    return redirect('admin_dashboard')
                elif hasattr(user, 'is_doctor') and user.is_doctor():
                    return redirect(f'/doctor_dashboard?user_id={user.id}')
            else:
                return render(request, self.template_name, {'form': form, 'error': 'Invalid credentials'})
        return render(request, self.template_name, {'form': form})

user_login = UserLoginView.as_view()

# class CustomLogoutView(View):
#     def post(self, request, *args, **kwargs):
#         logout(request)
#         return redirect('login')

# user_logout = CustomLogoutView.as_view()
