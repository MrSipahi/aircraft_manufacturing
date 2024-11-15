from django import template
from django.core.cache import cache
from functools import lru_cache

register = template.Library()

@register.filter
def has_perm(user, permission):
    """
    Kullanıcının yetkisi olup olmadığını kontrol eder - HTML template için kullanılır - Cache mekanizması ile hızlandırılmıştır
    """
    cache_key = f'user_perm_{user.id}_{permission}'
    
    result = cache.get(cache_key)
    if result is None:
        result = user.has_team_permission(permission)
        cache.set(cache_key, result, timeout=300) 
    
    return result