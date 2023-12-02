from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, pagination
from rest_framework.response import Response
from django.contrib.auth.models import User, Group, GroupManager
from .serializers import UserSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import Category, MenuItem, Cart, Order, OrderItem
from .permissions import IsManagerUser

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get(self, request):
        queryset = self.get_queryset()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
    
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    # Add filters for sorting and search
    filter_fields = ('title', 'price', 'featured', 'category')
    search_fields = ('title', 'price', 'featured', 'category')
    ordering_fields = ('title', 'price', 'featured', 'category')
    
    # Add pagination
    pagination_class = CustomPagination
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = MenuItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        if request.user.groups.filter(name='Manager').exists():
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    # Add filters for sorting and search
    filter_fields = ('title', 'price', 'featured', 'category')
    search_fields = ('title', 'price', 'featured', 'category')
    ordering_fields = ('title', 'price', 'featured', 'category')
    
    # Add pagination
    pagination_class = CustomPagination
    
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

class ManagerUserView(generics.ListCreateAPIView):
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = UserSerializer
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # def post(self, request):
    #     # Assuming you are passing the username as 'username' in the request data
    #     username = request.data.get('username')

    #     try:
    #         user = User.objects.get(username=username)
    #     except User.DoesNotExist:
    #         return Response({"error": f"User with username '{username}' not found"}, status=status.HTTP_404_NOT_FOUND)

    #     # Get or create the manager group
    #     manager_group, created = Group.objects.get_or_create(name='Manager')

    #     # Assign the user to the manager group
    #     user.groups.add(manager_group)

    #     return Response({"message": f"User '{username}' has been assigned to the 'manager' group"}, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = get_object_or_404(User, username=request.data.get('username'))
        group = Group.objects.get(name='Manager')
        user.groups.add(group)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#Removes this particular user from the manager group and returns 200 – Success if everything is okay.If the user is not found, returns 404 – Not found
class SingleManagerUserView(generics.DestroyAPIView):
    permission_classes = [IsManagerUser]
    def delete(self, request, userId):
        try:
            group = Group.objects.get(name='Manager')
            user = User.objects.get(pk=userId)
            user.groups.remove(group)
            return Response(status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class DeliveryUserView(generics.ListCreateAPIView):
    permission_classes = [IsManagerUser]
    queryset = User.objects.filter(groups__name='Delivery Crew')
    def get(self, request):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)
    def post(self, request):
        try:
            user = User.objects.get(pk=request.data.get('userId'))
            group = Group.objects.get(name='Delivery Crew')
            user.groups.add(group)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

#Assigns the user in the payload to delivery crew group and returns 201-Created HTTP
class SingleDeliveryUserView(generics.DestroyAPIView):
    queryset = User.objects.filter(groups__name='Delivery Crew')
    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        group = Group.objects.get(name='Delivery Crew')
        user.groups.remove(group)
        return Response(status=status.HTTP_200_OK)

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    def get(self, request):
        queryset = self.get_queryset()
        serializer = CartSerializer(queryset, many=True)
        if request.user.groups.filter(name='Customer').exists():
            return Response(serializer.data)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        menu_item = get_object_or_404(MenuItem, pk=request.data.get('itemId'))
        user = request.user
        quantity = request.data.get('quantity')
        if quantity is not None:
            try:
                quantity = int(quantity)
            except ValueError:
                return Response({"error": "Quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Quantity must be provided"}, status=status.HTTP_400_BAD_REQUEST)
        unit_price = menu_item.price
        try:
            price = unit_price * quantity
        except TypeError as e:
            return Response({"error": f"Invalid quantity: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        cart_item = Cart(user=user, menuitem=menu_item, quantity=quantity, unit_price=unit_price, price=price)
        cart_item.save()
        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request, pk):
        cart_item = get_object_or_404(Cart, pk=pk)
        cart_item.delete()
        return Response(status=status.HTTP_200_OK)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
# Create order view class with get and post methods, 
# get() Returns all orders with order items created by this user, 
# post() Creates a new order item for the current user. 
# Gets current cart items from the cart endpoints and adds those items to the order items table. 
# Then deletes all items from the cart for this user.
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    # Add filters for sorting and search
    filter_fields = ('user', 'delivery_crew', 'status', 'total', 'date')
    search_fields = ('user', 'delivery_crew', 'status', 'total', 'date')
    ordering_fields = ('user', 'delivery_crew', 'status', 'total', 'date')
    
    # Add pagination
    pagination_class = CustomPagination
    
    def get(self, request):
        if request.user.groups.filter(name='Customer').exists():
            order = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data)
        elif request.user.groups.filter(name='Delivery crew').exists():
            order = Order.objects.filter(delivery_crew=request.user)
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data)
        elif request.user.groups.filter(name='Manager').exists():
            order = Order.objects.all()
            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data)
    def post(self, request):
        if request.user.groups.filter(name='Customer').exists():
            user = request.user
            delivery_crew = get_object_or_404(User, pk=request.data.get('delivery_crew'))
            status = request.data.get('status')
            total = request.data.get('total')
            date = request.data.get('date')
            order = Order(user=user, delivery_crew=delivery_crew, status=status, total=total, date=date)
            order.save()
            cart_items = Cart.objects.filter(user=user)
            for cart_item in cart_items:
                order_item = OrderItem(order=order, menuitem=cart_item.menuitem, quantity=cart_item.quantity, unit_price=cart_item.unit_price, price=cart_item.price)
                order_item.save()
            cart_items.delete()
            return Response("Create OK.")
    
#Returns all items for this order id. If the order ID doesn’t belong to the current user, it displays an appropriate HTTP error status code.
class SingleOrderView(generics.ListAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    def get(self, request, pk):
        if request.user.groups.filter(name='Customer').exists():
            order_id = get_object_or_404(Order, pk=pk)
            if order_id.user == request.user:
                queryset = self.get_queryset()
                serializer = OrderItemSerializer(queryset, many=True)
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        
    def put(self, request, pk):
        if request.user.groups.filter(name='Manager').exist():
            order = get_object_or_404(Order, pk=pk)
            delivery_crew = request.data.get('delivery_crew')
            status = request.data.get('status')
            order.delivery_crew = delivery_crew
            order.status = status
            order.save()
            return Response(status=status.HTTP_200_OK)
    
    def patch(self, request, pk):
        if request.user.groups.filter(is_delivery_crew=True).exist():
            order = get_object_or_404(Order, pk=pk)
            status = request.data.get('status')
            order.status = status
            order.save()
            return Response(status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        if request.user.groups.filter(name='Manager').exist():
            order = get_object_or_404(Order, pk=pk)
            order.delete()
            return Response(status=status.HTTP_200_OK)
