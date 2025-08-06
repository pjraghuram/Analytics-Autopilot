CREATE TABLE IF NOT EXISTS file_uploads (
    id                      SERIAL PRIMARY KEY,
    original_filename       VARCHAR(255) NOT NULL,
    stored_filename        VARCHAR(255) NOT NULL,
    file_size              BIGINT NOT NULL,
    file_type              VARCHAR(50) NOT NULL,
    upload_datetime        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload_status          VARCHAR(20) DEFAULT 'uploaded',
    original_rows          INTEGER,
    original_columns       INTEGER,
    original_shape         VARCHAR(50),
    is_processed           BOOLEAN DEFAULT FALSE,
    processing_datetime    TIMESTAMP NULL,
    processing_status      VARCHAR(20) DEFAULT 'pending',
    processed_filename     VARCHAR(255) NULL,
    processed_rows         INTEGER NULL,
    processed_columns      INTEGER NULL,
    processed_shape        VARCHAR(50) NULL,
    rows_removed           INTEGER NULL,
    columns_removed        INTEGER NULL,
    s3_original_key        VARCHAR(500) NULL,
    s3_processed_key       VARCHAR(500) NULL,
    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_filename ON file_uploads(original_filename);
CREATE INDEX IF NOT EXISTS idx_file_uploads_upload_date ON file_uploads(upload_datetime);
CREATE INDEX IF NOT EXISTS idx_file_uploads_processed ON file_uploads(is_processed);