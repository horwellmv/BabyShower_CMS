"""
Supabase Storage Backend for Django
====================================
Custom storage backend that uploads media files to Supabase Storage
and returns public URLs for serving them.

Uses Supabase's REST API directly (no SDK needed).
"""

import os
import requests
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):
    """
    Django storage backend for Supabase Storage.
    
    Required settings:
        SUPABASE_URL: Your Supabase project URL (e.g., https://xxx.supabase.co)
        SUPABASE_KEY: Your Supabase service role key
        SUPABASE_BUCKET: Storage bucket name (default: 'media')
    """

    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL.rstrip('/') if settings.SUPABASE_URL else ''
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket = settings.SUPABASE_BUCKET
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables "
                "to use SupabaseStorage backend."
            )

    @property
    def base_api_url(self):
        """Base URL for Supabase Storage API."""
        return f"{self.supabase_url}/storage/v1"

    @property
    def headers(self):
        """Default headers for Supabase API requests."""
        return {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
        }

    def _save(self, name, content):
        """Upload a file to Supabase Storage."""
        import mimetypes
        import logging
        logger = logging.getLogger(__name__)

        # Read file content
        content.seek(0)
        file_data = content.read()

        # Determine content type reliably
        content_type = getattr(content, 'content_type', None)
        if not content_type or content_type == 'application/octet-stream':
            guessed_type, _ = mimetypes.guess_type(name)
            content_type = guessed_type or 'image/webp'

        # Upload via Supabase Storage API
        url = f"{self.base_api_url}/object/{self.bucket}/{name}"
        headers = {
            **self.headers,
            "Content-Type": content_type,
            "x-upsert": "true",  # Overwrite if exists
        }

        response = requests.post(url, headers=headers, data=file_data)

        if response.status_code not in (200, 201):
            error_msg = (
                f"[SupabaseStorage Error] Failed to upload '{name}' to bucket '{self.bucket}'. "
                f"URL: {url} | Status: {response.status_code} | "
                f"Content-Type: {content_type} | Response: {response.text}"
            )
            print(error_msg)
            logger.error(error_msg)
            raise IOError(error_msg)

        return name

    def url(self, name):
        """Return the public URL for a file."""
        if not name:
            return ""
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{name}"

    def exists(self, name):
        """Check if a file exists in Supabase Storage."""
        url = f"{self.base_api_url}/object/info/{self.bucket}/{name}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200

    def delete(self, name):
        """Delete a file from Supabase Storage."""
        url = f"{self.base_api_url}/object/{self.bucket}"
        payload = {"prefixes": [name]}
        response = requests.delete(url, headers=self.headers, json=payload)
        
        if response.status_code not in (200, 204):
            raise IOError(
                f"Failed to delete file from Supabase Storage: "
                f"{response.status_code} - {response.text}"
            )

    def _open(self, name, mode='rb'):
        """Download and return a file from Supabase Storage."""
        url = self.url(name)
        response = requests.get(url)
        
        if response.status_code != 200:
            raise IOError(
                f"Failed to download file from Supabase Storage: "
                f"{response.status_code}"
            )
        
        return ContentFile(response.content, name=name)

    def size(self, name):
        """Return the size of a file in Supabase Storage."""
        url = f"{self.base_api_url}/object/info/{self.bucket}/{name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            metadata = response.json()
            return metadata.get("metadata", {}).get("size", 0)
        return 0

    def listdir(self, path=""):
        """List contents of a directory in Supabase Storage."""
        url = f"{self.base_api_url}/object/list/{self.bucket}"
        payload = {"prefix": path, "limit": 1000}
        response = requests.post(url, headers=self.headers, json=payload)

        dirs = []
        files = []

        if response.status_code == 200:
            for item in response.json():
                name = item.get("name", "")
                if item.get("id") is None:
                    dirs.append(name)
                else:
                    files.append(name)

        return dirs, files
