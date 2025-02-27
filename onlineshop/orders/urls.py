from django.urls import path
import orders.views as views
app_name="orders"
urlpatterns=[
    path("created/",views.order_create,name="order_create"),
    path('admin/order/<int:order_id>/',views.admin_order_detail,name='admin_order_detail')
]