from django.urls import path
from . import views

urlpatterns = [
    # path('category', views.CategoryView),
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('cart', views.CartView),
    path('order', views.OrderView),
    path('order-item', views.OrderItemView),
]
