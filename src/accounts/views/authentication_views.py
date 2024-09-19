from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from ..forms import LoginForm
from django.core.exceptions import ValidationError
from django.contrib import messages

class UserLoginView(View):
    """
    View for handling user login. It renders the login form on GET requests
    and processes login credentials on POST requests.
    """
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get(self, request):
        """
        Handles GET requests by rendering the login form.
        """
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """
        Handles POST requests to authenticate the user. If the credentials are
        valid, the user is logged in and redirected based on their role:
        - Superusers are redirected to the admin page.
        - Admin users are redirected to the admin dashboard.
        - Doctors are redirected to their doctor dashboard.

        If authentication fails, an error message is displayed.
        """
        try:
            form = self.form_class(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                
                user = authenticate(request, username=username, password=password)

                if user:
                    login(request, user)

                    # Redirect based on user role
                    if user.is_superuser:
                        return redirect('/admin')
                    elif hasattr(user, 'is_admin') and user.is_admin():
                        return redirect('admin_dashboard')
                    elif hasattr(user, 'is_doctor') and user.is_doctor():
                        return redirect(f'/doctor-dashboard?user_id={user.id}')
                else:
                    # Invalid credentials
                    messages.error(request, 'Invalid username or password.')
                    return render(request, self.template_name, {'form': form})
            
            # Form validation failed
            return render(request, self.template_name, {'form': form})

        except ValidationError as e:
            # Handle form validation errors
            messages.error(request, f"Form error: {str(e)}")
            return render(request, self.template_name, {'form': form})

        except Exception as e:
            # Handle unexpected exceptions
            messages.error(request, 'An unexpected error occurred. Please try again later.')
            return render(request, self.template_name, {'form': form})

# Use this view in your URLs
user_login = UserLoginView.as_view()
