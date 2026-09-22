import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Manages cloud storage and persistent PostgreSQL operations via Supabase.
    Automatically activates when SUPABASE_URL and SUPABASE_KEY are provided.
    """

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    @property
    def is_configured(self) -> bool:
        """Returns True if Supabase credentials are validly populated in environment."""
        url = (self.settings.supabase_url or "").strip()
        key = (self.settings.supabase_key or "").strip()
        return bool(url and key and url.startswith("http"))

    @property
    def client(self):
        """Lazy-loaded Supabase client."""
        if not self.is_configured:
            return None

        if self._client is None:
            try:
                from supabase import create_client, Client
                self._client: Client = create_client(
                    self.settings.supabase_url.strip(),
                    self.settings.supabase_key.strip(),
                )
                logger.info("Supabase client initialized successfully: %s", self.settings.supabase_url)
            except Exception as exc:
                logger.error("Failed to initialize Supabase client: %s", str(exc))
                return None

        return self._client

    async def upload_image_bytes(
        self,
        filename: str,
        image_bytes: bytes,
        content_type: str = "image/png",
    ) -> Optional[str]:
        """
        Uploads verified image bytes to Supabase Storage Bucket and returns its public CDN URL.
        """
        client = self.client
        if not client:
            return None

        bucket_name = self.settings.supabase_bucket
        try:
            # Upload file to Supabase Storage
            res = client.storage.from_(bucket_name).upload(
                path=filename,
                file=image_bytes,
                file_options={"content-type": content_type, "upsert": "true"},
            )

            # Retrieve public URL
            public_url = client.storage.from_(bucket_name).get_public_url(filename)
            logger.info("Uploaded %s to Supabase Storage bucket '%s'. Public URL: %s", filename, bucket_name, public_url)
            return public_url
        except Exception as exc:
            logger.warning("Supabase Storage upload error for %s: %s", filename, str(exc))
            # Attempt to construct public URL even if bucket exists
            try:
                base_url = self.settings.supabase_url.rstrip("/")
                return f"{base_url}/storage/v1/object/public/{bucket_name}/{filename}"
            except Exception:
                return None

    async def insert_artwork_record(self, artifact_dict: dict) -> bool:
        """
        Inserts generated artwork metadata into the Supabase PostgreSQL table.
        """
        client = self.client
        if not client:
            return False

        table_name = self.settings.supabase_table
        try:
            record = {
                "id": artifact_dict.get("id"),
                "filename": artifact_dict.get("filename"),
                "url": artifact_dict.get("url"),
                "prompt": artifact_dict.get("prompt"),
                "negative_prompt": artifact_dict.get("negative_prompt"),
                "aspect_ratio": artifact_dict.get("aspect_ratio"),
                "width": artifact_dict.get("width"),
                "height": artifact_dict.get("height"),
                "style": artifact_dict.get("style"),
                "retry_count": artifact_dict.get("retry_count", 0),
                "created_at": artifact_dict.get("created_at"),
            }
            client.table(table_name).insert(record).execute()
            logger.info("Inserted record %s into Supabase table '%s'", artifact_dict.get("id"), table_name)
            return True
        except Exception as exc:
            logger.warning("Supabase table insert error for %s: %s", artifact_dict.get("id"), str(exc))
            return False

    def fetch_history(self, limit: int = 50) -> list[dict]:
        """
        Fetches generation history from Supabase PostgreSQL table sorted by newest first.
        """
        client = self.client
        if not client:
            return []

        table_name = self.settings.supabase_table
        try:
            response = (
                client.table(table_name)
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data or []
        except Exception as exc:
            logger.warning("Supabase fetch history error: %s", str(exc))
            return []

    def delete_record_and_file(self, identifier: str) -> bool:
        """
        Deletes the artwork from both the Supabase table and Storage bucket.
        """
        client = self.client
        if not client:
            return False

        clean_id = identifier.replace(".png", "").replace(".json", "")
        filename = f"{clean_id}.png"
        table_name = self.settings.supabase_table
        bucket_name = self.settings.supabase_bucket

        deleted = False
        try:
            # Delete from DB
            client.table(table_name).delete().eq("id", clean_id).execute()
            deleted = True
        except Exception as exc:
            logger.warning("Supabase DB delete error for %s: %s", clean_id, str(exc))

        try:
            # Delete from Storage
            client.storage.from_(bucket_name).remove([filename])
        except Exception as exc:
            logger.warning("Supabase storage delete error for %s: %s", filename, str(exc))

        return deleted


# Singleton instance
supabase_service = SupabaseService()
