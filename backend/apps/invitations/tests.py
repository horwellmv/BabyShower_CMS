import tempfile
import shutil
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.invitations.models import Guest, Gift, GiftReservation

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BabyShowerTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        
        # Create test guests
        self.guest_a = Guest.objects.create(full_name="Invitado A", phone_number="1234567890")
        self.guest_b = Guest.objects.create(full_name="Invitado B", phone_number="0987654321")
        
        # Create a small dummy image for testing
        dummy_image = SimpleUploadedFile(
            name='test_image.png',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b',
            content_type='image/png'
        )
        
        # Create finite and infinite gifts
        self.finite_gift = Gift.objects.create(
            title="Cochecito Finito",
            description="Finite stock gift",
            image=dummy_image,
            is_unlimited=False
        )
        self.infinite_gift = Gift.objects.create(
            title="Pañales Infinitos",
            description="Infinite stock gift",
            image=dummy_image,
            is_unlimited=True
        )

    def test_middleware_redirects_unauthenticated(self):
        # Accessing home without session redirects to login
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))

    def test_login_success(self):
        # Login with valid phone number (phone input with formatting is cleaned automatically)
        response = self.client.post(reverse('login'), {'phone': '123-456-7890'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('guest_id'), self.guest_a.id)

    def test_login_failure(self):
        # Login with invalid phone
        response = self.client.post(reverse('login'), {'phone': '9999999999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lo sentimos, el número ingresado no coincide")

    def test_rsvp_api(self):
        # Set session
        session = self.client.session
        session['guest_id'] = self.guest_a.id
        session.save()
        
        # Update RSVP status to CONFIRMED
        response = self.client.post(reverse('api_rsvp'), {'status': 'CONFIRMED'})
        self.assertEqual(response.status_code, 200)
        self.guest_a.refresh_from_db()
        self.assertEqual(self.guest_a.rsvp_status, Guest.RSVPStatus.CONFIRMED)

    def test_finite_gift_reservation_limits(self):
        # Authenticate as guest_a
        session = self.client.session
        session['guest_id'] = self.guest_a.id
        session.save()
        
        # Reserve finite gift
        response = self.client.post(reverse('api_reserve', args=[self.finite_gift.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(GiftReservation.objects.filter(gift=self.finite_gift, guest=self.guest_a).exists())

        # Log in as guest_b and attempt to reserve same finite gift
        self.client.logout()
        session = self.client.session
        session['guest_id'] = self.guest_b.id
        session.save()
        
        response = self.client.post(reverse('api_reserve', args=[self.finite_gift.id]))
        self.assertEqual(response.status_code, 400) # Should fail
        self.assertIn('ya ha sido reservado', response.json()['error'])

    def test_infinite_gift_multiple_reservations(self):
        # Authenticate as guest_a and reserve infinite gift
        session = self.client.session
        session['guest_id'] = self.guest_a.id
        session.save()
        response = self.client.post(reverse('api_reserve', args=[self.infinite_gift.id]))
        self.assertEqual(response.status_code, 200)

        # Log in as guest_b and reserve same infinite gift (should succeed!)
        self.client.logout()
        session = self.client.session
        session['guest_id'] = self.guest_b.id
        session.save()
        response = self.client.post(reverse('api_reserve', args=[self.infinite_gift.id]))
        self.assertEqual(response.status_code, 200)
        
        # Verify both reservations exist
        self.assertEqual(GiftReservation.objects.filter(gift=self.infinite_gift).count(), 2)
