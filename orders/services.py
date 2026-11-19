from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone
from django.db import models

from .models import Coupon


COUPON_SESSION_KEY = "voltix_coupon_id"


def get_valid_coupon(coupon_id):
    if not coupon_id:
        return None

    now = timezone.now()

    return Coupon.objects.filter(
        pk=coupon_id,
        is_active=True,
        valid_from__lte=now,
        valid_until__gte=now,
        used_count__lt=models.F("max_uses"),
    ).first()


def calculate_totals(cart, coupon=None):
    subtotal = cart.get_total_price()

    discount_percent = (
        coupon.discount_percent if coupon else 0
    )

    discount_amount = (
        subtotal * Decimal(discount_percent) / Decimal("100")
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    total = subtotal - discount_amount

    return {
        "subtotal": subtotal,
        "discount_percent": discount_percent,
        "discount_amount": discount_amount,
        "total": total,
    }
