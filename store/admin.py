from django.contrib import admin
from .models import product,Variation

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'create_date', 'is_available', 'modified_date',)
    prepopulated_fields = {'slug' : ('product_name',)}

class VariationAdmin(admin.ModelAdmin):
    list_display = ('products', 'variation_category', 'variation_value', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('products', 'variation_category', 'variation_value')

# Register your models here.
admin.site.register(product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
