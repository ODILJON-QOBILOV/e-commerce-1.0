from django.urls import path

from commerce.views import CreateProductAPIView, GetProductsAPIView, AddCartItemAPIView, GetCartAPIView, OrdersAPIView, \
    CreateOrderAPIView, ProductsCommentAPIView, ProductsUpdateAPIView, ProductsDeleteAPIView, RetrieveProductAPIView

urlpatterns = [
    path('create/', CreateProductAPIView.as_view()),
    path('get/', GetProductsAPIView.as_view()),
    path('cart/add/', AddCartItemAPIView.as_view()),
    path('cart/get/', GetCartAPIView.as_view()),
    path('order/', OrdersAPIView.as_view()),
    path('order/create/', CreateOrderAPIView.as_view()),
    path('comments/', ProductsCommentAPIView.as_view()),
    path('update/<int:pk>/', ProductsUpdateAPIView.as_view()),
    path('delete/<int:pk>/', ProductsDeleteAPIView.as_view()),
    path('get/<int:pk>/', RetrieveProductAPIView.as_view()),
]