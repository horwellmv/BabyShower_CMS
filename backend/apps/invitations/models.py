import re
from django.db import models

class Guest(models.Model):
    class RSVPStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        CONFIRMED = 'CONFIRMED', 'Confirmado'
        DECLINED = 'DECLINED', 'No Asistirá'

    phone_number = models.CharField(max_length=20, unique=True, verbose_name="Número de Teléfono")
    full_name = models.CharField(max_length=150, verbose_name="Nombre Completo")
    rsvp_status = models.CharField(
        max_length=15,
        choices=RSVPStatus.choices,
        default=RSVPStatus.PENDING,
        verbose_name="Estado RSVP"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Clean phone number: keep only digits
        self.phone_number = re.sub(r'\D', '', self.phone_number)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

    class Meta:
        verbose_name = "Invitado"
        verbose_name_plural = "Invitados"


class Gift(models.Model):
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    suggested_link = models.URLField(blank=True, verbose_name="Enlace de Compra")
    image = models.ImageField(upload_to='gifts/', verbose_name="Imagen")
    is_unlimited = models.BooleanField(default=False, verbose_name="Stock Ilimitado/Múltiple")
    order = models.IntegerField(default=0, verbose_name="Orden de visualización")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Regalo"
        verbose_name_plural = "Regalos"
        ordering = ['order', 'title']


class GiftReservation(models.Model):
    gift = models.ForeignKey(Gift, on_delete=models.CASCADE, related_name='reservations', verbose_name="Regalo")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='gift_reservations', verbose_name="Invitado")
    reserved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('gift', 'guest')
        verbose_name = "Reserva de Regalo"
        verbose_name_plural = "Reservas de Regalos"

    def __str__(self):
        return f"{self.gift.title} reservado por {self.guest.full_name}"


class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/', verbose_name="Imagen")
    caption = models.CharField(max_length=150, blank=True, verbose_name="Pie de foto")
    order = models.IntegerField(default=0, verbose_name="Orden de visualización")

    def __str__(self):
        return self.caption or f"Imagen #{self.id}"

    class Meta:
        verbose_name = "Imagen de Galería"
        verbose_name_plural = "Imágenes de Galería"
        ordering = ['order', 'id']
