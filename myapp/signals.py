from django.contrib.auth.signals import user_logged_in
from django.db.models import ImageField
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from .image_utils import optimize_image_field


@receiver(pre_save, dispatch_uid='myapp_optimize_uploaded_images')
def optimize_uploaded_images(sender, instance, **kwargs):
    if sender._meta.app_label != 'myapp':
        return
    for field in sender._meta.get_fields():
        if isinstance(field, ImageField):
            optimize_image_field(getattr(instance, field.name))


def detect_device(request):
    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    from .models import CustomUser
    if 'android' in ua:
        return CustomUser.DEVICE_ANDROID
    if 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
        return CustomUser.DEVICE_IOS
    if any(tag in ua for tag in ('windows', 'macintosh', 'linux', 'x11')) and 'mobile' not in ua:
        return CustomUser.DEVICE_DESKTOP
    return CustomUser.DEVICE_OTHER


def _device_label(request):
    from .models import CustomUser
    ua_lower = request.META.get('HTTP_USER_AGENT', '').lower()
    if 'edg/' in ua_lower:
        browser = 'Edge'
    elif 'chrome/' in ua_lower and 'chromium' not in ua_lower:
        browser = 'Chrome'
    elif 'firefox/' in ua_lower:
        browser = 'Firefox'
    elif 'safari/' in ua_lower and 'chrome/' not in ua_lower:
        browser = 'Safari'
    else:
        browser = 'Browser'
    device_label = dict(CustomUser.DEVICE_CHOICES).get(detect_device(request), 'Device')
    return f'{device_label} · {browser}'


@receiver(user_logged_in, dispatch_uid='myapp_bind_single_session')
def bind_single_session(sender, request, user, **kwargs):
    """Enforce 'One ID - One Device - One Login': every successful login (site
    login/signup, SSO, or Django admin) binds this session as the account's only
    valid one. Any other active session for this account is signed out — with an
    explanatory message — the next time it's used, via SingleSessionMiddleware."""
    if not request.session.session_key:
        request.session.save()
    user.active_session_key = request.session.session_key or ''
    user.active_device_label = _device_label(request)
    user.active_login_at = timezone.now()
    user.device_type = detect_device(request)
    user.save(update_fields=['active_session_key', 'active_device_label', 'active_login_at', 'device_type'])
