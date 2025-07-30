from django.db import models
from category.models import Category
from django.urls import reverse
# Create your models here.

class product(models.Model):
    product_name        = models.CharField(max_length=200, unique=True)
    slug                = models.SlugField(max_length=200, unique=True)                
    desciptions         = models.TextField(max_length=500, blank=True)
    price               = models.IntegerField()
    p_image             = models.ImageField(upload_to='photos/products')
    stock               = models.IntegerField() 
    is_available        = models.BooleanField()
    category            = models.ForeignKey(Category, on_delete=models.CASCADE)
    create_date         = models.DateTimeField(auto_now_add=True)
    modified_date       = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail' , args = [self.category.slug, self.slug ])

    def __str__(self):
        return self.product_name

