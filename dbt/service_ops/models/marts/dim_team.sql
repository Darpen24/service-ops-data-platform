select team_id, team_name, region from {{ ref('stg_teams') }}
