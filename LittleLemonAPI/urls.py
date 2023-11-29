from django.urls import path
from . import views

urlpatterns = [
    # path('category', views.CategoryView),
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagerUserView.as_view()),
    path('groups/manager/users/{userId}', views.SingleManagerUserView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryUserView.as_view()),
    path('groups/delivery-crew/users/{userId}', views.SingleDeliveryUserView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/{orderId}', views.SingleOrderView.as_view()),
]
