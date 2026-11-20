from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.db import transaction

from .cache_utils import clear_storefront_cache
from .models import Category, Product, ProductImage


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
@receiver(post_save, sender=ProductImage)
@receiver(post_delete, sender=ProductImage)
def invalidate_storefront(sender, using, **kwargs):

    transaction.on_commit(clear_storefront_cache, using=using)
