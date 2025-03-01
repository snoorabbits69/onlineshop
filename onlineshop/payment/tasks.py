from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order

@shared_task
def payment_completed(order_id):
    try:
        # Get the order by ID
        order = Order.objects.get(id=order_id)

        # Email subject and message
        subject = f'My Shop - Invoice No {order.id}'
        message = 'Please find attached the invoice for your recent purchase.'

        # Create email
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="snoorabbits69@gmail.com",
            to=[order.email]
        )

        # Render the HTML for the PDF
        html = render_to_string('orders/order/pdf.html', {'order': order})

        # Generate PDF
        out = BytesIO()
        stylesheets = [weasyprint.CSS(finders.find('css/pdf.css'))]
        weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

        # Attach PDF to email
        out.seek(0)
        email.attach(f'Invoice_{order.id}.pdf', out.read(), 'application/pdf')

        # Send email
        email.send(fail_silently=False)

        return f"Email sent successfully to {order.email}"

    except Order.DoesNotExist:
        return f"Order with ID {order_id} does not exist."

    except Exception as e:
        return f"An error occurred: {str(e)}"
