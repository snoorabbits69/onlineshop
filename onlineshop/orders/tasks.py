from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def order_created(order_id):
    order=Order.objects.get(id=order_id)
    subject=f'Order no.{order.id}'
    message=(
        f'Dear {order.firstname},\n\n'
        f'You have sucessfully placed an order'
        f'Your order id is {order.id}'
    )
    mail_sent=send_mail(
        subject,message,'snoorabbits69@gmail.com',[order.email]
    )
    return mail_sent