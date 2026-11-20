import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order


logger = logging.getLogger(__name__)


def send_order_confirmation(order_id):

    try:
        order = (
            Order.objects
            .prefetch_related("items")
            .get(pk=order_id)
        )

        context = {
            "order": order,
        }

        subject = (
            f"VOLTIX — Підтвердження замовлення №{order.pk}"
        )

        text_content = render_to_string(
            "orders/emails/order_created.txt",
            context
        )

        html_content = render_to_string(
            "orders/emails/order_created.html",
            context
        )

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )

        message.attach_alternative(
            html_content,
            "text/html"
        )

        message.send(fail_silently=False)

        logger.info(
            "Email підтвердження замовлення №%s відправлено.",
            order_id
        )

    except Exception:
        logger.exception(
            "Не вдалося надіслати email замовлення №%s.",
            order_id
        )


# EMAIL ПРИ ЗМІНІ СТАТУСУ
def send_order_status_email(order_id, expected_status):

    try:
        order = Order.objects.get(pk=order_id)

        if order.status != expected_status:
            logger.info(
                "Пропущено застарілий email для замовлення №%s.",
                order_id
            )
            return

        context = {
            "order": order,
        }

        subject = (
            f"VOLTIX — Замовлення №{order.pk}: "
            f"{order.get_status_display()}"
        )

        text_content = render_to_string(
            "orders/emails/order_status.txt",
            context
        )

        html_content = render_to_string(
            "orders/emails/order_status.html",
            context
        )

        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
        )

        message.attach_alternative(
            html_content,
            "text/html"
        )

        message.send(fail_silently=False)

        logger.info(
            "Email про статус замовлення №%s сформовано.",
            order.pk
        )

    except Exception:
        logger.exception(
            "Помилка email статусу замовлення №%s.",
            order_id
        )

