from django.db.models import Sum
from drf_spectacular.utils import extend_schema, OpenApiExample, inline_serializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, serializers
from rest_framework.permissions import IsAuthenticated


from commerce.models import Product, Cart, Order, Comment
from commerce.serializers import CreateProductsSerializers, GetProductsSerializers, AddCartItemSerializer, \
    GetCartSerializer, ProductSerializer, OrdersSerializer, OrderUserInfoSerializer, CommentSerializer, \
    PostCommentsSerializer, UpdateProductSerializer


class CreateProductAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    @extend_schema(
        responses=CreateProductsSerializers(many=True),
    )
    def post(self, request):
        serializer = CreateProductsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetProductsAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    @extend_schema(
        responses=GetProductsSerializers(many=True)
    )
    def get(self, request):
        products = Product.objects.all()
        serializer = GetProductsSerializers(products, many=True)
        return Response(serializer.data)


class AddCartItemAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    @extend_schema(
        request=AddCartItemSerializer,
        tags=["Cart"]
    )

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            cart = serializer.save()
            return Response(
                {"detail": "Added to cart successfully.", "cart": AddCartItemSerializer(cart).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetCartAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    @extend_schema(
        tags=["cart"]
    )
    def get(self, request):
        user = request.user
        data = Cart.objects.filter(user=user)
        if not data.exists():
            return Response({"detail": "No items in the cart."}, status=status.HTTP_404_NOT_FOUND)
        serializer = GetCartSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
        tags=["Product Detail, Get, Update, Destroy"]
    )
class GetUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrdersAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    @extend_schema(
        request=OrdersSerializer,
        tags=["Orders"]
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrdersSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
        request=OrderUserInfoSerializer,
        tags=["Orders"]
    )
# class CreateOrderAPIView(APIView):
#     permission_classes = (IsAuthenticated, )
#     def post(self, request):
#         cart_items = Cart.objects.filter(user=request.user).first()
#         if not cart_items:
#             return Response({'message': 'you dont have any items in cart'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = CreateProductsSerializers(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         order = Order.objects.create(
#             user=request.user,
#             products=cart_items.product.name,
#             price=cart_items.price,
#             payment_method=serializer.data.get('payment_method'),
#             user_location=serializer.data.get('user_location'),
#             quantity=cart_items.quantity,
#             status='pending'
#        )
#         order.save()
#         return Response({'message': 'Order created successfully.', 'order': order}, status=status.HTTP_201_CREATED)

class CreateOrderAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        # Step 1: Retrieve all cart items for the user
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({'message': 'You don\'t have any items in your cart'}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Calculate total price from all cart items
        total_price = sum(item.price for item in cart_items)

        # Step 3: Get payment method and user location from the request data
        serializer = OrderUserInfoSerializer(data=request.data)
        if serializer.is_valid():
            # Save any relevant information (like payment method or user location)
            payment_method = serializer.validated_data.get('payment_method')
            user_location = serializer.validated_data.get('user_location')

            # Step 4: Create the order
            order = Order.objects.create(
                user=request.user,
                total_price=cart_items,  # The total price from the cart items
                payment_method=payment_method,
                user_location=user_location,
                status='pending',  # Default status
            )

            # Optional: Link cart items to the order
            # You can store the cart items in the order if you want to track them
            order.cart_items.set(cart_items)

            # Step 5: Clear the cart after placing the order
            cart_items.delete()

            return Response({
                'message': 'Order created successfully.',
                'order': {
                    'user': order.user.username,
                    'total_price': order.total_price,
                    'payment_method': order.payment_method,
                    'user_location': order.user_location,
                    'status': order.status
                }
            }, status=status.HTTP_201_CREATED)

        return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class ProductsCommentAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    @extend_schema(
        tags=["Comments"],
        request=PostCommentsSerializer
    )
    def post(self, request):
        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(product=product)

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=ProductSerializer,
)
class ProductsUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductsDeleteAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RetrieveProductAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = Product.objects.all()
    serializer_class = ProductSerializer




