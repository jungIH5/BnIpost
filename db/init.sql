-- BnIpost Database Initialization

-- Users table (managed by Java/Spring JPA, defined here for reference)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nickname VARCHAR(100) NOT NULL,
    profile_image TEXT,
    provider VARCHAR(20) NOT NULL CHECK (provider IN ('NAVER', 'INSTAGRAM')),
    provider_id VARCHAR(255) NOT NULL,
    naver_access_token TEXT,
    naver_refresh_token TEXT,
    instagram_access_token TEXT,
    instagram_user_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (provider, provider_id)
);

-- Post history table (managed by Python/SQLAlchemy, defined here for reference)
CREATE TABLE IF NOT EXISTS post_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('naver', 'instagram')),
    input_type VARCHAR(20) NOT NULL CHECK (input_type IN ('keyword', 'image')),
    input_keyword TEXT,
    generated_title TEXT,
    generated_content TEXT,
    generated_hashtags TEXT,
    published_url TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'published', 'failed')),
    retry_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_post_history_user_id ON post_history(user_id);
CREATE INDEX IF NOT EXISTS idx_post_history_platform ON post_history(platform);
CREATE INDEX IF NOT EXISTS idx_post_history_created_at ON post_history(created_at DESC);
