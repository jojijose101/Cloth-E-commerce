from django.db import models
from django.urls import reverse


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=250,unique=True)
    slug = models.SlugField(max_length=250,unique=True)
    desc = models.TextField(blank=True)
    img = models.ImageField(upload_to='category')
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def get_url(self):
        return reverse('moc_app:product_of_cat',args=[self.slug])

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    desc = models.TextField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    img = models.ImageField(upload_to='product')
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.IntegerField()
    # Clothing-specific metadata (kept simple to avoid complex variant tables)
    # Store comma-separated values like: "S,M,L,XL" and "Black,Blue,Red"
    sizes = models.CharField(max_length=120, blank=True, help_text='Comma-separated sizes e.g. S,M,L,XL')
    colors = models.CharField(max_length=120, blank=True, help_text='Comma-separated colors e.g. Black,Blue,Red')
    brand = models.CharField(max_length=120, blank=True)
    material = models.CharField(max_length=120, blank=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    def get_url(self):
        return reverse('moc_app:product',args=[self.category.slug,self.slug])


    class Meta:
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name