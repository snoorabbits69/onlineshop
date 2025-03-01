from django.shortcuts import render,redirect,get_object_or_404

from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem,Order
from .tasks import order_created
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML,CSS
from django.contrib.staticfiles import finders
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon=cart.coupon
                order.discount=cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            # clear the cart
            cart.clear()
            order_created.delay(order.id)
            #setting the order session
            request.session['order_id']=order.id
            return redirect('payment:process')
            # return render(
            #     request, 'orders/order/created.html', {'order': order}
            # )
    else:
        form = OrderCreateForm()
    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form},
    )

@staff_member_required
def admin_order_detail(request,order_id):
    order=get_object_or_404(Order,id=order_id)
    return render(
        request,'admin/orders/detail.html',
        {'order':order}
    )
@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']=f'filename=order_{order.id}.pdf'
    HTML(string=html).write_pdf(
        response,
        stylesheets=[CSS(finders.find('css/pdf.css'))]
    )
    return response


