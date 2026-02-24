from django.contrib import admin

from moc_app.models import Category, Product


# Register your models here.
class CategoryForm(admin.ModelAdmin):
    list_display = ['name','slug']
    prepopulated_fields = {'slug':('name',)}
admin.site.register(Category,CategoryForm)


class ProductForm(admin.ModelAdmin):
    list_display = ['name','price','available','stock','updated','created']
    list_editable = ['price','available','stock']
    prepopulated_fields = {'slug':('name',)}
    list_per_page = 20
admin.site.register(Product,ProductForm)

