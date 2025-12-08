from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm

# ---- Registration View ----
def register(request):
  if request.method == 'POST':
    form = UserRegistrationForm(request.POST)
    
    if form.is_valid():
      form.save()
      username = form.cleaned_data.get('username')
      #Add a success message to display on the next page
      messages.success(request, f'Account created for {username}!')
      return redirect('login') # Redirect to the login page
  else:
    form = UserRegistrationForm()
  
  return render(request, 'blog/register.html', {'form': form})

# --- Profile Management View (Basic Implementation)
@login_required
def profile(request):
  #This example view just displays the profile template.
  # For updating, you would add a form and POST logic here
  return render(request, 'blog/profile.html')