CREATE TABLE IF NOT EXISTS comments_sentiments_raw(
    id                  INTEGER         PRIMARY KEY AUTOINCREMENT,
    user_id             TEXT            NOT NULL,
    comment             TEXT            NOT NULL,
    sentiment_label     TEXT            NOT NULL,
    sentiment_polarity  REAL            NOT NULL,
    timestamp           TEXT            NOT NULL,
    source              TEXT            NOT NULL,
    device              TEXT            NOT NULL
)
