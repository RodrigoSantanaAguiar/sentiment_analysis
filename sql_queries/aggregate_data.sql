INSERT OR REPLACE INTO comments_sentiments_aggregated(
    observation_time,
    device,
    source,
    updated_at,
    positive_comment_number,
    neutral_comment_number,
    negative_comment_number,
    total_comments,
    sentiment_polarity,
    positive_comment_perc,
    neutral_comment_perc,
    negative_comment_perc
)

WITH count_comments AS (
SELECT
    strftime('%Y-%m-%d %H:%M:00', timestamp) AS observation_time,
    device,
    source,
    strftime('%Y-%m-%d %H:%M:%S', datetime('now')) AS updated_at,
    AVG(sentiment_polarity) AS sentiment_polarity,
    COUNT(CASE WHEN sentiment_label = 'Positive' THEN 1 ELSE NULL END) AS positive_comment_number,
    COUNT(CASE WHEN sentiment_label = 'Neutral' THEN 1 ELSE NULL END) AS neutral_comment_number,
    COUNT(CASE WHEN sentiment_label = 'Negative' THEN 1 ELSE NULL END) AS negative_comment_number,
    COUNT(*) AS total_comments
FROM comments_sentiments_raw
GROUP BY observation_time, device, source
)

SELECT
    observation_time,
    device,
    source,
    updated_at,
    positive_comment_number,
    neutral_comment_number,
    negative_comment_number,
    total_comments,
    sentiment_polarity,
    ROUND(positive_comment_number * 1.0 / total_comments, 2) AS positive_comment_perc,
    ROUND(neutral_comment_number * 1.0 / total_comments, 2) AS neutral_comment_perc,
    ROUND(negative_comment_number * 1.0 / total_comments, 2) AS negative_comment_perc
FROM count_comments;
