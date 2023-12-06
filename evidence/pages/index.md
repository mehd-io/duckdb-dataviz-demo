---
title: DuckDB 🦆 - Python 🐍 downloads
---
<GithubStarCount user='duckdb' repo='duckdb'/>

## How many people downloaded DuckDB ?
<BigValue 
    title='Total download past 2 years'
    data={count_over_month} 
    value='download_count' 
    fmt='#,##0.00,,"M"'	
/>
<BigValue 
    data={count_september} 
    value='download_sum_september_2023' 
    fmt='#,##0.00,,"M"'	
/>

<LineChart data = {download_week} y=weekly_downloads x=week_start_date  />

<DataTable data="{download_month}" search="false">
    <Column id="month_start_date" title="Month Start Date"/>
    <Column id="monthly_downloads" title="Monthly Downloads" />
</DataTable>


## Where do people download DuckDB?

<WorldMap 
    data={world} 
    title="World Map" 
    subtitle="Downloads by Country" 
    region=country_name 
    value=download_count
    colorScale=red
/>

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

```count_over_month
SELECT SUM(daily_download_count) AS download_count
FROM daily_stats
WHERE timestamp_day BETWEEN DATE_TRUNC('month', CURRENT_DATE) AND CURRENT_DATE;
```

```count_september
SELECT 
    SUM(daily_download_count) AS download_sum_september_2023
FROM 
    daily_stats
WHERE
    timestamp_day BETWEEN '2023-09-01' AND '2023-09-30';
```


```download_month
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

```sql download_week 
SELECT 
    DATE_TRUNC('week', timestamp_day) AS week_start_date,
    SUM(daily_download_count) AS weekly_downloads
FROM 
    daily_stats
GROUP BY 
    DATE_TRUNC('week', timestamp_day)
ORDER BY 
    week_start_date DESC;
```


```sql world
SELECT  *
FROM country_download
```


```sql duckdb_version
WITH weekly_downloads AS (
    SELECT
        MAKE_DATE(year, 1, 1) + INTERVAL '7' DAY * (week - 1) AS week_start_date,
        CONCAT(SPLIT_PART(duckdb_version, '.', 1), '.', SPLIT_PART(duckdb_version, '.', 2)) AS simplified_version,
        SUM(download_count) AS weekly_downloads
    FROM
       weekly_duckdb_version 
    WHERE 
        (
            CAST(SPLIT_PART(duckdb_version, '.', 1) AS INT) > 0 OR 
            (CAST(SPLIT_PART(duckdb_version, '.', 1) AS INT) = 0 AND CAST(SPLIT_PART(duckdb_version, '.', 2) AS INT) >= 6)
        )
        AND (year > 2022 OR (year = 2022 AND week >= 48)) 
    GROUP BY
        1, 2 -- Grouping by the position number in the SELECT clause (short-hand)
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
    -- Calculate the start date of each week and sum the download counts per Python version
    SELECT
        MAKE_DATE(year, 1, 1) + INTERVAL '7' DAY * (week - 1) AS week_start_date,
        python_major_minor_version,
        SUM(download_count) AS weekly_downloads
    FROM
        weekly_python_version
    WHERE 
        download_count IS NOT NULL AND
        python_major_minor_version IN ('2.7', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11')
    GROUP BY
        1, 2
),
cumulative_downloads AS (
    -- Calculate the cumulative download counts per Python version over time
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
