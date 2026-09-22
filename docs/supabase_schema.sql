-- ==========================================================================
-- IMAGEGO SUPABASE SETUP SCRIPT
-- Run this in your Supabase Project -> SQL Editor
-- ==========================================================================

-- 1. Create Artworks Metadata Table
CREATE TABLE IF NOT EXISTS public.artworks (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    url TEXT NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    aspect_ratio TEXT DEFAULT '16:9',
    width INTEGER DEFAULT 1344,
    height INTEGER DEFAULT 768,
    style TEXT DEFAULT 'cinematic',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Enable Row Level Security (RLS) & Public Read/Write Policy
ALTER TABLE public.artworks ENABLE ROW LEVEL SECURITY;

-- Allow public access for reading artworks
CREATE POLICY "Public Read Artworks"
    ON public.artworks
    FOR SELECT
    USING (true);

-- Allow public access for inserting artworks
CREATE POLICY "Public Insert Artworks"
    ON public.artworks
    FOR INSERT
    WITH CHECK (true);

-- Allow public access for deleting artworks
CREATE POLICY "Public Delete Artworks"
    ON public.artworks
    FOR DELETE
    USING (true);

-- 3. Create Storage Bucket for Artwork Images (if not already created)
INSERT INTO storage.buckets (id, name, public)
VALUES ('artwork-images', 'artwork-images', true)
ON CONFLICT (id) DO NOTHING;

-- 4. Storage Bucket Policies (Public read and insert)
CREATE POLICY "Public Read Storage Objects"
    ON storage.objects
    FOR SELECT
    USING (bucket_id = 'artwork-images');

CREATE POLICY "Public Upload Storage Objects"
    ON storage.objects
    FOR INSERT
    WITH CHECK (bucket_id = 'artwork-images');

CREATE POLICY "Public Delete Storage Objects"
    ON storage.objects
    FOR DELETE
    USING (bucket_id = 'artwork-images');
