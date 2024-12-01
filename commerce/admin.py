from django.contrib import admin

from commerce.models import Product, Category, SubCategory, Cart, ProductImage, Comment

# Register your models here.

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Cart)
admin.site.register(ProductImage)
admin.site.register(Comment)