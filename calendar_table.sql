SELECT
    t.*

FROM   
    adhoc_db.calendar_table t

WHERE 1=1
    AND t.ym=202603 #only show March of 2026

ORDER BY
    t.dt asc #show values in date order, ascending

;