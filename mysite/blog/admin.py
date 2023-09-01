from django.contrib import admin
from .models import Post

# Register your models here.
# this adds the blog model to the administration site
# admin.site.register(Post)
# the model registered is using a custom class
# the list_display allows to set the fields of your model that you want to display 
# in the administration object list page
# the @admin.register() decorator performs the same function as the admin.site.register() function
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']