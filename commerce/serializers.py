from rest_framework import serializers

from commerce.models import Product, Cart, Order, Comment


class CreateProductsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'count', 'category')


class GetProductsSerializers(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username')
    category_name = serializers.CharField(source='category.name')
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'count', 'category_name', 'user_username')



class AddCartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = ('product_id','product_name','quantity', 'price', 'user')
        read_only_fields = ['price']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, attrs):
        product = attrs['product']
        attrs['price'] = product.price * attrs['quantity']
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        product = validated_data['product']
        quantity = validated_data['quantity']
        price = validated_data['price']

        cart, created = Cart.objects.update_or_create(
            user=user, product=product,
            defaults={'quantity': quantity, 'price': price}
        )
        return cart

class GetCartSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = Cart
        fields = ('added_at','product', 'quantity', 'price', 'user')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'count', 'category')


class OrdersSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = Cart
        fields = ('added_at','product', 'quantity', 'price', 'user')


class OrderUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('payment_method', 'user_location')

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    product = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Comment
        fields = ('text', 'user', 'product')

class PostCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField()

class UpdateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'count', 'category')