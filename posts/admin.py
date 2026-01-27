from django.contrib import admin
from .models import Post, Category

admin.site.register(Post)
admin.site.register(Category)

# Register your models here.
@admin.action(description="Mark selected posts as Published")
def make_published(modeladmin, _request, queryset):
    queryset.update(status='PB')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
  actions = [make_published]
  list_display = ('title', 'author', 'category', 'status', 'created_at')
  list_filter = ('status', 'category', 'author')
  search_fields = ('title', 'content')
  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
  list_display = ('name',)