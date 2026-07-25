"""
Script de exportación de datos — BabyShower CMS
=================================================
Exporta los datos de la base SQLite a un fixture JSON
que puede ser importado en PostgreSQL en producción.

Uso:
    cd backend
    python manage.py dumpdata invitations auth.user --indent 2 --output ../data_fixture.json

Para importar en producción (Railway console):
    python manage.py loaddata data_fixture.json

Nota: Este script NO migra archivos media (imágenes).
Las imágenes deben subirse manualmente a Supabase Storage.
"""
import os
import sys
import subprocess


def main():
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    output_file = os.path.join(backend_dir, '..', 'data_fixture.json')
    
    print("=" * 50)
    print("[*] Exportando datos de SQLite...")
    print("=" * 50)
    
    # Export invitations app data + auth users (for superuser)
    cmd = [
        sys.executable, 'manage.py', 'dumpdata',
        'invitations',       # All invitations models (Guest, Gift, GiftReservation, GalleryImage)
        'auth.user',         # Admin superuser
        '--indent', '2',
        '--output', output_file,
        '--exclude', 'contenttypes',
        '--exclude', 'auth.permission',
        '--exclude', 'sessions',
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        file_size = os.path.getsize(output_file)
        print(f"[OK] Datos exportados exitosamente a: {output_file}")
        print(f"   Tamaño del archivo: {file_size / 1024:.1f} KB")
        print()
        print("[i] Para importar en produccion (Railway console):")
        print("   python manage.py loaddata data_fixture.json")
        print()
        print("[!] Recuerda: Las imagenes deben subirse manualmente")
        print("   a Supabase Storage manteniendo la misma estructura")
        print("   de carpetas (gifts/, gallery/).")
    else:
        print(f"[ERROR] Error al exportar datos:")
        print(result.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
