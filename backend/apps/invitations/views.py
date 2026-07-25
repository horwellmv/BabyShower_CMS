import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from apps.invitations.models import Guest, Gift, GiftReservation, GalleryImage

def login_view(request):
    if request.session.get('guest_id'):
        return redirect('home')

    error_message = None
    if request.method == 'POST':
        phone_input = request.POST.get('phone', '')
        # Clean phone number input to keep digits only
        cleaned_phone = re.sub(r'\D', '', phone_input)
        
        try:
            guest = Guest.objects.get(phone_number=cleaned_phone)
            request.session['guest_id'] = guest.id
            return redirect('home')
        except Guest.DoesNotExist:
            error_message = "Lo sentimos, el número ingresado no coincide con ningún invitado en nuestra lista. Por favor, verifica tu número."

    return render(request, 'login.html', {'error_message': error_message})


@require_POST
def logout_view(request):
    if 'guest_id' in request.session:
        del request.session['guest_id']
    return redirect('login')


def home_view(request):
    guest = request.guest
    return render(request, 'home.html', {
        'guest': guest,
        'rsvp_choices': Guest.RSVPStatus.choices
    })


def gallery_view(request):
    images = GalleryImage.objects.all().order_by('order', 'id')
    return render(request, 'gallery.html', {'images': images})


def gifts_view(request):
    guest = request.guest
    all_gifts = Gift.objects.all().order_by('order', 'title')
    
    gifts_data = []
    for gift in all_gifts:
        reservations = gift.reservations.all()
        
        is_reserved_by_me = any(r.guest == guest for r in reservations)
        is_reserved_by_someone_else = any(r.guest != guest for r in reservations)
        
        if not gift.is_unlimited and is_reserved_by_someone_else:
            status = 'locked'
            reserved_by_display = "Reservado"
        elif is_reserved_by_me:
            status = 'reserved_by_me'
            reserved_by_display = None
        else:
            status = 'available'
            reserved_by_display = None

        gifts_data.append({
            'gift': gift,
            'status': status,
            'reserved_by_display': reserved_by_display,
        })
        
    return render(request, 'gifts.html', {'gifts_data': gifts_data})


def my_reservations_view(request):
    guest = request.guest
    my_res = GiftReservation.objects.filter(guest=guest).select_related('gift')
    return render(request, 'my_reservations.html', {'reservations': my_res})


@require_POST
def rsvp_api(request):
    status = request.POST.get('status')
    if status not in [Guest.RSVPStatus.CONFIRMED, Guest.RSVPStatus.DECLINED]:
        return JsonResponse({'success': False, 'error': 'Estado RSVP inválido'}, status=400)
    
    guest = request.guest
    guest.rsvp_status = status
    guest.save()
    
    return JsonResponse({
        'success': True,
        'rsvp_status': guest.rsvp_status,
        'full_name': guest.full_name
    })


@require_POST
def reserve_api(request, gift_id):
    guest = request.guest
    
    with transaction.atomic():
        gift = get_object_or_404(Gift.objects.select_for_update(), id=gift_id)
        
        already_reserved = GiftReservation.objects.filter(gift=gift, guest=guest).exists()
        if already_reserved:
            return JsonResponse({'success': True, 'message': 'Ya has reservado este regalo'})
            
        if not gift.is_unlimited:
            has_reservation = GiftReservation.objects.filter(gift=gift).exists()
            if has_reservation:
                return JsonResponse({'success': False, 'error': 'Lo sentimos, este regalo ya ha sido reservado por otro invitado.'}, status=400)
                
        GiftReservation.objects.create(gift=gift, guest=guest)
    
    return JsonResponse({'success': True, 'message': '¡Regalo reservado con éxito!'})

