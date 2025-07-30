from django.contrib import admin
from .models import product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'create_date', 'is_available', 'modified_date',)
    prepopulated_fields = {'slug' : ('product_name',)}


# Register your models here.
admin.site.register(product, ProductAdmin)
