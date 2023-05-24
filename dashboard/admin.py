from django.contrib import admin
from .models import notes, homework,todo
# Register your models here.
admin.site.register(notes)
admin.site.register(homework)
admin.site.register(todo)
