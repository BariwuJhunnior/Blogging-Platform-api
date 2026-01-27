from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Follow
from django.utils.html import format_html


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
  #Thumbnail is the custom method we create below
  list_display = ('user', 'thumbnail', 'bio')
  readonly_fields = ('thumbnail',)

  @admin.action(description="Picture")
  def thumbnail(self, obj):
    if obj.profile_picture:
      return format_html('<img src="{}" style="width: 50px; border-radius: 50%; object-fit: cover;" />', obj.profile_picture.url)
    
    return 'No Image'
  

admin.site.register(Follow)
admin.site.register(Profile)

class ProfileInline(admin.StackedInline):
  model = Profile
  can_delete = False
  verbose_name_plural = 'Profile Info'
  readonly_fields = ('thumbnail',)

  def thumbnail(self, obj):
    if obj.profile_picture:
      return format_html('<img src="{}" width="100" />', obj.profile_picture.url)
    return "No Image"
  
#Unregister the original User admin
admin.site.unregister(User)

#2. Register User with our new Inline
@admin.register(User)
class UserAdmin(BaseUserAdmin):
  inlines = (ProfileInline,)