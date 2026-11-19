from django.core.cache import cache

HOME_CATEGORIES = 'home:categories:v1'
HOME_NEW = 'home:new-products:v1'
HOME_FEATURED = 'home:featured-products:v1'
HOME_CACHE_TIMEOUT = 180


def clear_storefront_cache():
    cache.delete_many([HOME_CATEGORIES, HOME_NEW, HOME_FEATURED])
