SELECT * 
FROM {{ source('cs2', 'events') }}