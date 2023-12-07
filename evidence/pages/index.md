---
title: 🦆 DuckDB pypi stats | Evidence
---
<GithubStarCount user='duckdb' repo='duckdb'/>

## How many people downloaded DuckDB ?
<BigValue 
    title='Total download'
    data={count_over_month} 
    value='download_count' 
    fmt='#,##0.00,,"M"'	
/>
<BigValue 
    data={count_november} 
    value='download_sum_november_2023' 
    fmt='#,##0.00,,"M"'	
/>

### Daily Download

<LineChart data = {download_daily} y=daily_download x=timestamp_day  />

### Monthly download

<DataTable data="{download_month}" search="false">
    <Column id="month_start_date" title="Month Start Date"/>
    <Column id="monthly_downloads" title="Monthly Downloads" />
</DataTable>

## Which DuckDB version do people use ?
<LineChart 
    data={duckdb_version} 
    x=week_start_date 
    y=cum_download 
    series=simplified_version 
    yAxisTitle="cumulative downloads" 
    xAxisTitle="day of year"
/>

## Which Python version do people use ?
<LineChart 
    data={python_version} 
    x=week_start_date 
    y=cum_download 
    series=python_major_minor_version 
    yAxisTitle="cumulative downloads" 
    xAxisTitle="week of the year"
/>

```sql count_over_month
SELECT SUM(daily_download_count) AS download_count
FROM daily_stats
```

```sql count_november
SELECT 
    SUM(daily_download_count) AS download_sum_november_2023
FROM 
    daily_stats
WHERE
    timestamp_day BETWEEN '2023-11-01' AND '2023-11-30';
```


```sql download_month
SELECT 
    DATE_TRUNC('month', timestamp_day) AS month_start_date,
    SUM(daily_download_count) AS monthly_downloads
FROM 
    daily_stats
GROUP BY 
    month_start_date
ORDER BY 
    month_start_date DESC;
```

```sql download_daily
SELECT 
    SUM(daily_download_count) AS daily_download,
    timestamp_day
FROM 
    daily_stats
GROUP BY 
   timestamp_day 
ORDER BY 
    timestamp_day DESC;
```

```sql duckdb_version
WITH weekly_downloads AS (
    SELECT
        DATE_TRUNC('week', timestamp_day) AS week_start_date,
        CONCAT(SPLIT_PART(file_version, '.', 1), '.', SPLIT_PART(file_version, '.', 2)) AS simplified_version,
        SUM(daily_download_count) AS weekly_downloads
    FROM
       daily_stats 
    WHERE 
        (
            CAST(SPLIT_PART(file_version, '.', 1) AS INT) > 0 OR 
            (CAST(SPLIT_PART(file_version, '.', 1) AS INT) = 0 AND CAST(SPLIT_PART(file_version, '.', 2) AS INT) >= 6)
        )
        AND EXTRACT(year FROM timestamp_day) > 2022 
        OR (
            EXTRACT(year FROM timestamp_day) = 2022 AND EXTRACT(week FROM timestamp_day) >= 48
        )
    GROUP BY
        1, 2
),
distinct_weekly_downloads AS (
    SELECT DISTINCT
        week_start_date,
        simplified_version,
        weekly_downloads
    FROM
        weekly_downloads
),
cumulative_downloads AS (
    SELECT
        week_start_date,
        simplified_version,
        SUM(weekly_downloads) OVER (
            PARTITION BY simplified_version
            ORDER BY week_start_date
        ) AS cum_download
    FROM
        distinct_weekly_downloads
)
SELECT * FROM cumulative_downloads;
```

```sql python_version
WITH weekly_downloads AS (
    SELECT
        DATE_TRUNC('week', timestamp_day) AS week_start_date,
        CONCAT(SPLIT_PART(python_version, '.', 1), '.', SPLIT_PART(python_version, '.', 2)) AS python_major_minor_version,
        SUM(daily_download_count) AS weekly_downloads
    FROM
        daily_stats 
    WHERE 
        daily_download_count IS NOT NULL AND
        python_major_minor_version IN ('2.7', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11')
    GROUP BY
        1, 2
),
cumulative_downloads AS (
    SELECT
        week_start_date,
        python_major_minor_version,
        SUM(weekly_downloads) OVER (
            PARTITION BY python_major_minor_version
            ORDER BY week_start_date
        ) AS cum_download
    FROM
        weekly_downloads
)
SELECT * FROM cumulative_downloads;
```
