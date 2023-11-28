from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get(self, request):
        queryset = self.get_queryset()
        serializer = MenuItemSerializer(queryset, many=True)
        if request.user.groups.filter(name='Manager').exists():
            return Response(serializer.data)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request, pk):
        try:
            menu_item = MenuItem.objects.get(pk=pk)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenuItemSerializer(menu_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get(self):
        queryset = self.get_queryset()
        serializer = MenuItemSerializer(queryset)
        return Response(serializer.data)
    def post(self, request, pk):
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def put(self, request, pk):
        if request.user.groups.filter(name='Manager').exists():
            try:
                menu_item = MenuItem.objects.get(pk=pk)
            except MenuItem.DoesNotExist:
                return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = MenuItemSerializer(menu_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def CartView(request):
    if request.method == 'GET':
        items = Cart.objects.all()
        serialized_item = CartSerializer(items, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def OrderView(request):
    if request.method == 'GET':
        items = Order.objects.all()
        serialized_item = OrderSerializer(items, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    
def OrderItemView(request):
    if request.method == 'GET':
        items = OrderItem.objects.all()
        serialized_item = OrderItemSerializer(items, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
