-- ─────────────────────────────────────────
-- QUERY 1 — Feature Adoption Rate by User Segment
-- ─────────────────────────────────────────

SELECT
    user_segment,
    feature_name,
    COUNT(DISTINCT user_id) AS users_who_used_feature,
    COUNT(DISTINCT user_id) * 100.0 /
        SUM(COUNT(DISTINCT user_id)) OVER (PARTITION BY user_segment) AS adoption_rate
FROM feature_usage
GROUP BY user_segment, feature_name
ORDER BY adoption_rate DESC;


-- ─────────────────────────────────────────
-- QUERY 2 — D7 and D30 Retention by Acquisition Channel
-- ─────────────────────────────────────────

SELECT
    acquisition_channel,
    COUNT(DISTINCT user_id) AS total_users,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 6 AND 8
        THEN user_id END) * 100.0 / COUNT(DISTINCT user_id) AS D7_Retention,
    COUNT(DISTINCT CASE WHEN days_since_signup BETWEEN 28 AND 32
        THEN user_id END) * 100.0 / COUNT(DISTINCT user_id) AS D30_Retention
FROM user_activity
GROUP BY acquisition_channel
ORDER BY D30_Retention DESC;


-- ─────────────────────────────────────────
-- QUERY 3 — Feature Engagement Depth
-- ─────────────────────────────────────────

SELECT
    feature_name,
    AVG(session_duration_seconds)       AS avg_time_on_feature,
    COUNT(*)                            AS total_interactions,
    COUNT(DISTINCT user_id)             AS unique_users,
    COUNT(*) / COUNT(DISTINCT user_id)  AS interactions_per_user
FROM feature_usage
GROUP BY feature_name
ORDER BY interactions_per_user DESC;


-- ─────────────────────────────────────────
-- QUERY 4 — Funnel Drop-off Identification (CTE)
-- ─────────────────────────────────────────

WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'app_open'               THEN 1 ELSE 0 END) AS reached_app,
        MAX(CASE WHEN event = 'registration_complete'  THEN 1 ELSE 0 END) AS reached_registration,
        MAX(CASE WHEN event = 'kyc_complete'           THEN 1 ELSE 0 END) AS reached_kyc,
        MAX(CASE WHEN event = 'first_deposit'          THEN 1 ELSE 0 END) AS reached_deposit,
        MAX(CASE WHEN event = 'first_trade'            THEN 1 ELSE 0 END) AS reached_trade
    FROM user_events
    GROUP BY user_id
)
SELECT
    SUM(reached_app)          AS step1_app,
    SUM(reached_registration) AS step2_registration,
    SUM(reached_kyc)          AS step3_kyc,
    SUM(reached_deposit)      AS step4_deposit,
    SUM(reached_trade)        AS step5_trade,

    ROUND(SUM(reached_registration) * 100.0 / NULLIF(SUM(reached_app), 0), 2)          AS app_to_reg_rate,
    ROUND(SUM(reached_kyc)          * 100.0 / NULLIF(SUM(reached_registration), 0), 2) AS reg_to_kyc_rate,
    ROUND(SUM(reached_deposit)      * 100.0 / NULLIF(SUM(reached_kyc), 0), 2)          AS kyc_to_deposit_rate,
    ROUND(SUM(reached_trade)        * 100.0 / NULLIF(SUM(reached_deposit), 0), 2)      AS deposit_to_trade_rate
FROM funnel;


-- ─────────────────────────────────────────
-- QUERY 5 — Monthly Active Users Trend
-- ─────────────────────────────────────────

SELECT
    DATE_TRUNC('month', activity_date) AS month,
    COUNT(DISTINCT user_id)            AS monthly_active_users
FROM user_activity
WHERE activity_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', activity_date)
ORDER BY month ASC;


-- ─────────────────────────────────────────
-- QUERY 6 — Users Stuck at Each Funnel Stage
-- ─────────────────────────────────────────

WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event = 'registration_complete' THEN 1 ELSE 0 END) AS registered,
        MAX(CASE WHEN event = 'kyc_complete'          THEN 1 ELSE 0 END) AS kyc_done,
        MAX(CASE WHEN event = 'first_deposit'         THEN 1 ELSE 0 END) AS deposited,
        MAX(CASE WHEN event = 'first_trade'           THEN 1 ELSE 0 END) AS traded
    FROM user_events
    GROUP BY user_id
)
SELECT
    COUNT(CASE WHEN registered = 1 AND kyc_done = 0  THEN 1 END) AS stuck_at_kyc,
    COUNT(CASE WHEN kyc_done   = 1 AND deposited = 0 THEN 1 END) AS stuck_at_deposit,
    COUNT(CASE WHEN deposited  = 1 AND traded = 0    THEN 1 END) AS stuck_at_first_trade
FROM funnel;
