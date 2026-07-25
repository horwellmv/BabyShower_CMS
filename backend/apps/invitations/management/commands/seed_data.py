import os
import io
import re
from PIL import Image, ImageDraw
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from apps.invitations.models import Guest, Gift, GiftReservation, GalleryImage

class Command(BaseCommand):
    help = "Loads seed data for the Baby Shower application"

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing data...")
        GiftReservation.objects.all().delete()
        Guest.objects.all().delete()
        Gift.objects.all().delete()
        GalleryImage.objects.all().delete()

        # 1. Create Guests
        self.stdout.write("Creating guests...")
        guests_data = [
            {"full_name": "Invitado Demo", "phone_number": "1111111111"},
            {"full_name": "María R.", "phone_number": "2222222222"},
            {"full_name": "Carlos M.", "phone_number": "3333333333"},
            {"full_name": "Familia S.", "phone_number": "4444444444"},
            {"full_name": "Sofía L.", "phone_number": "5555555555"},
        ]
        
        created_guests = {}
        for gd in guests_data:
            g = Guest.objects.create(
                full_name=gd["full_name"],
                phone_number=gd["phone_number"],
                rsvp_status=Guest.RSVPStatus.PENDING
            )
            created_guests[gd["full_name"]] = g

        # Helper to generate watercolor-like placeholders
        def generate_watercolor_img(filename, label, color_hex):
            # Parse color
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
            
            # Create canvas
            img = Image.new("RGB", (500, 500), color=(253, 248, 245))
            draw = ImageDraw.Draw(img)
            
            # Draw overlay circles to simulate soft watercolor wash
            draw.ellipse([50, 80, 450, 420], fill=(r, g, b))
            draw.ellipse([100, 100, 400, 400], fill=(255, 255, 255))
            draw.ellipse([130, 130, 370, 370], fill=(r, g, b))
            
            # Save
            f = io.BytesIO()
            img.save(f, format="PNG")
            return ContentFile(f.getvalue(), name=filename)

        # Helper to try loading existing generated assets or fall back
        def get_image_file(target_filename, label, color_hex, source_path=None):
            if source_path and os.path.exists(source_path):
                try:
                    with open(source_path, 'rb') as f:
                        return ContentFile(f.read(), name=target_filename)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to read {source_path}: {e}"))
            return generate_watercolor_img(target_filename, label, color_hex)

        # Paths to assets images
        assets_images_dir = os.path.join(settings.BASE_DIR.parent, "frontend", "assets", "images")
        stroller_path = os.path.join(assets_images_dir, "stroller.png")
        diapers_path = os.path.join(assets_images_dir, "diapers.png")

        # 2. Create Gifts
        self.stdout.write("Creating gifts...")
        gifts_data = [
            {
                "title": "Bodysuits de Algodón Orgánico",
                "description": "Juego de pañaleros suaves de algodón orgánico para la comodidad de Adhara.",
                "is_unlimited": True,
                "color": "#ebbbba",
                "order": 1
            },
            {
                "title": "Conejito de Peluche",
                "description": "Un conejito de peluche ultrasuave de orejas caídas.",
                "is_unlimited": False,
                "color": "#eee0d5",
                "order": 2
            },
            {
                "title": "Organizador de Pañales",
                "description": "Organizador de lona para pañales y toallitas.",
                "is_unlimited": False,
                "color": "#dbe5df",
                "order": 3
            },
            {
                "title": "Moisés Tejido",
                "description": "Moisés tejido a mano de fibras naturales.",
                "is_unlimited": False,
                "color": "#eee0d5",
                "order": 4
            },
            {
                "title": "Set de Toallas de Baño",
                "description": "Toallas de baño suaves con capucha.",
                "is_unlimited": True,
                "color": "#bfc9c3",
                "order": 5
            },
            {
                "title": "Monitor de Bebé",
                "description": "Monitor inteligente de audio y video nocturno.",
                "is_unlimited": False,
                "color": "#ebbbba",
                "order": 6
            },
            {
                "title": "Cochecito de Paseo Premium",
                "description": "Cochecito de paseo con suspensión y diseño ergonómico.",
                "is_unlimited": False,
                "color": "#eee0d5",
                "source": stroller_path,
                "order": 7
            },
            {
                "title": "Pañales Premium Ecológicos",
                "description": "Paquetes de pañales ecológicos biodegradables, ideales para abastecer stock inicial.",
                "is_unlimited": True,
                "color": "#dbe5df",
                "source": diapers_path,
                "order": 8
            }
        ]

        created_gifts = {}
        for idx, gd in enumerate(gifts_data):
            img_file = get_image_file(
                f"gift_{idx}.png",
                gd["title"],
                gd["color"],
                gd.get("source")
            )
            g = Gift.objects.create(
                title=gd["title"],
                description=gd["description"],
                is_unlimited=gd["is_unlimited"],
                order=gd["order"],
                image=img_file
            )
            created_gifts[gd["title"]] = g

        # 3. Pre-create some reservations as per prototype requirements
        self.stdout.write("Creating pre-reservations...")
        # Organizador de Pañales -> Reserved by María R.
        GiftReservation.objects.create(
            gift=created_gifts["Organizador de Pañales"],
            guest=created_guests["María R."]
        )
        # Monitor de Bebé -> Reserved by Familia S.
        GiftReservation.objects.create(
            gift=created_gifts["Monitor de Bebé"],
            guest=created_guests["Familia S."]
        )

        # 4. Create Gallery Images
        self.stdout.write("Creating gallery images...")
        gallery_data = [
            {"caption": "El primer ultrasonido de la pequeña Adhara", "color": "#ebbbba", "order": 1},
            {"caption": "Los felices futuros padres, Ali y Sofía", "color": "#dbe5df", "order": 2},
            {"caption": "Decoración de la habitación", "color": "#eee0d5", "order": 3},
            {"caption": "Eligiendo la ropita del bebé", "color": "#bfc9c3", "order": 4},
            {"caption": "¡Los primeros juguetitos de madera listos!", "color": "#ebbbba", "order": 5},
            {"caption": "Preparativos con amor", "color": "#dbe5df", "order": 6},
        ]
        
        for idx, gd in enumerate(gallery_data):
            img_file = generate_watercolor_img(
                f"gallery_{idx}.png",
                gd["caption"],
                gd["color"]
            )
            GalleryImage.objects.create(
                caption=gd["caption"],
                order=gd["order"],
                image=img_file
            )

        self.stdout.write(self.style.SUCCESS("Seed data loaded successfully!"))
