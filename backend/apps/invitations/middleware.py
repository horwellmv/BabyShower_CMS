from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.conf import settings
from apps.invitations.models import Guest

class GuestSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        
        # Check static/media first
        is_static_or_media = (
            (settings.STATIC_URL and path.startswith(settings.STATIC_URL)) or
            (settings.MEDIA_URL and path.startswith(settings.MEDIA_URL)) or
            '__debug__' in path
        )

        if is_static_or_media:
            return self.get_response(request)

        # Define exempt prefixes or names
        try:
            login_url = reverse('login')
        except NoReverseMatch:
            login_url = '/login/'

        is_exempt = (
            path == login_url or
            path.startswith('/admin/')
        )

        if not is_exempt:
            guest_id = request.session.get('guest_id')
            if not guest_id:
                return redirect(login_url)
            
            try:
                request.guest = Guest.objects.get(id=guest_id)
            except Guest.DoesNotExist:
                if 'guest_id' in request.session:
                    del request.session['guest_id']
                return redirect(login_url)
        else:
            guest_id = request.session.get('guest_id')
            if guest_id:
                try:
                    request.guest = Guest.objects.get(id=guest_id)
                except Guest.DoesNotExist:
                    request.guest = None
            else:
                request.guest = None

        return self.get_response(request)
