from django.contrib import admin
from .models import Category, SparePart, Sale

# Register your models here.
admin.site.register(Category)
admin.site.register(SparePart)
admin.site.register(Sale)
