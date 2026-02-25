from django.contrib import admin
from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name','email')
    search_fields = ('username', 'last_name','email')
    ordering = ('email',)
    
    def save_model(self, request, obj, form, change):        
        obj.save()