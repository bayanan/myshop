import braintree
import weasyprint
from django.shortcuts import render, get_object_or_404, redirect
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Получение токена для создания транзакции
        nonce = request.POST.get('payment_method_nonce', None)
        # Создание и сохранение транзакции
        result = braintree.Transaction.sale({
            'amount': f'{order.get_total_cost():.2f}',
            'payment_method_nonce': nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        if result.is_success:
            # Отметка заказа как оплаченного
            order.paid = True
            # Сохранение ID транзакции в заказе
            order.braintree_id = result.transaction.id
            order.save()
            # Создание электронного сообщения
            subject = f'My Shop - Invoice no. {order.id}'
            message = 'Please, find attached the invoice for your recent purchase.'
            email = EmailMessage(subject,
                                 message,
                                 'admin@mail.ru',
                                 [order.email])
            # Формирование PDF
            html = render_to_string('orders/order/pdf.html', {'order': order})
            out = BytesIO()
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
            # Прикрепляем PDF к электронному сообщению
            email.attach(f'order_{order.id}.pdf',
                         out.getvalue(),
                         'application/pdf')
            # Отправка сообщения
            email.send()
            return redirect('payment:payment_done')
        else:
            return redirect('payment:payment_canceled')
    else:
        # Формирование одноразового токена для JavaScript SDK
        client_token = braintree.ClientToken.generate()
        return render(request,
                      'payment/process.html',
                      {'order': order,
                       'client_token': client_token})


def payment_done(request):
    return render(request, 'payment/done.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
