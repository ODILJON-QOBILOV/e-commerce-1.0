from django.db import models
from users.models import User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SubCategory(BaseModel):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.IntegerField()
    category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name='user_products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return self.product.name

class Comment(BaseModel):
    text = models.CharField(max_length=200)
    product = models.ForeignKey(Product, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.text



class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} in {self.cart.user}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField()
    payment_method = models.CharField(max_length=100, choices=[
        ('card', 'Card'),
        ('cash', 'Cash')
    ])
    user_location = models.CharField(max_length=100)
    status = models.CharField(choices=[
        ('pending', 'Pending'),
        ('delivering', 'Delivering'),
        ('delivered', 'Delivered')
    ], default='pending', max_length=20)

    def save(self, *args, **kwargs):
        self.total_price = Cart.objects.filter(user=self.user).aggregate(
            total=models.Sum('total_price')
        )['total'] or 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Order"