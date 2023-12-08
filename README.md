football analytics project 

## data sources

* api football for base
* supplementary data through web-scraping

postgresql for database
reason: future planning. read-write, better large dataset

### tables


1. competition

| column | type |
| --- | --- |
| country | VARCHAR(30) |
| competition | VARCHAR(50) |

2. teams
| column | type |
| --- | --- |
| country | VARCHAR(30) |
| competition | VARCHAR(50) |




## Docker

```
cd docker 
docker compose up -d
```
