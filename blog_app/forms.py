from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
  """
    Custom registration form to include the email field.
    """
  class Meta: 
    model = User
    fields = ('username', 'email')

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    #Make the email field required during registration
    self.fields['email'].required = True