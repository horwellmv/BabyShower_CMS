from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Guest, Gift, GiftReservation, GalleryImage

@admin.action(description="Marcar invitados como Confirmados")
def make_confirmed(modeladmin, request, queryset):
    queryset.update(rsvp_status=Guest.RSVPStatus.CONFIRMED)

@admin.action(description="Marcar invitados como Pendientes")
def make_pending(modeladmin, request, queryset):
    queryset.update(rsvp_status=Guest.RSVPStatus.PENDING)

@admin.action(description="Marcar invitados como No Asistirán")
def make_declined(modeladmin, request, queryset):
    queryset.update(rsvp_status=Guest.RSVPStatus.DECLINED)

@admin.action(description="Liberar todas las reservas del regalo")
def release_gifts(modeladmin, request, queryset):
    for gift in queryset:
        gift.reservations.all().delete()

class GiftReservationInline(admin.TabularInline):
    model = GiftReservation
    extra = 0
    verbose_name = "Reserva"
    verbose_name_plural = "Reservas de este regalo"

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'rsvp_status', 'updated_at')
    list_filter = ('rsvp_status',)
    search_fields = ('full_name', 'phone_number')
    actions = [make_confirmed, make_declined, make_pending]
    inlines = [GiftReservationInline]


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'is_unlimited', 'reservations_count', 'order')
    list_filter = ('is_unlimited',)
    search_fields = ('title', 'description')
    ordering = ('order', 'title')
    actions = [release_gifts]
    inlines = [GiftReservationInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 45px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Vista Previa"

    def reservations_count(self, obj):
        count = obj.reservations.count()
        if count == 0:
            return mark_safe('<span style="color: green; font-weight: bold;">Disponible</span>')
        if obj.is_unlimited:
            return format_html('<span style="color: blue;">{} reservado(s) (Ilimitado)</span>', count)
        return mark_safe('<span style="color: red; font-weight: bold;">Reservado (Único)</span>')
    reservations_count.short_description = "Estado de Reserva"


@admin.register(GiftReservation)
class GiftReservationAdmin(admin.ModelAdmin):
    list_display = ('gift', 'guest', 'reserved_at')
    list_filter = ('reserved_at',)
    search_fields = ('gift__title', 'guest__full_name')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'caption', 'order')
    ordering = ('order', 'id')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height: 60px; border-radius: 4px; object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Vista Previa"
