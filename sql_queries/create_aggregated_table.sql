CREATE TABLE IF NOT EXISTS comments_sentiments_aggregated(
    observation_time                TEXT        NOT NULL,
    device                          TEXT        NOT NULL,
    source                          TEXT        NOT NULL,
    updated_at                      TEXT        NOT NULL,
    positive_comment_number         INTEGER     NOT NULL,
    neutral_comment_number          INTEGER     NOT NULL,
    negative_comment_number         INTEGER     NOT NULL,
    total_comments                  INTEGER     NOT NULL,
    sentiment_polarity              REAL        NOT NULL,
    positive_comment_perc           REAL        NOT NULL,
    neutral_comment_perc            REAL        NOT NULL,
    negative_comment_perc           REAL        NOT NULL,
    PRIMARY KEY (observation_time, device, source)
);
