# Overview

This application shows terror attacks in Ireland and/or in United Kingdom. Most important features are:
- Heatmap of terror attacks form 1970
- Exact locations of every attack (markers)
- Can show the top n buildings of same type in defined distance
- Can show the all lakes, rivers, sees in defined dictance
- Shows the regions on the border of Ireland and Northern Ireland and color it by sum of deads in terror attacks

This is it in action:

![Screenshot](heatmap.png)

![Screenshot](markers.png)

![Screenshot](regions.png)

The application has 2 separate parts, the client which is a [frontend web application](#frontend) using mapbox GL API and mapbox-gl.js and the [backend application](#backend) written in [Python](https://www.python.org/) using Flask server, backed by PostGIS. The frontend application communicates with backend using a [REST API](#api).

# Frontend

The frontend application is a static HTML page (`index.html`), which shows a mapbox-gl.js widget. It is displaying terror attack in Ireland. The map stzle is simle "light". 

All relevant frontend code is in `index.html`.
The frontend code is very simple, its only responsibilities are:
- displaying the whole map
- displaying the sidebar
- displaying the informations on map (heatmap, markers, polygons)
- handle users action (clicks)
- adding layers and sources into map

# Backend

The backend application was written in Python. This part of applicaion is responsible for comunicating with database and send data to frontend layer. For getting datas we used queryies and forcommunication we used flask.

## Data

Terror attack data is from Kaggle. I downloaded the full dataset and uplouaded it into database with my own py script. For this reason i used my own python script (load_terror.py).

Data about ireland were from Open Street Maps. I downloaded whole ireland (40 gb) and importet it using teh "osm2psql" tool.

## Queries

**Find terror attack in Ireland**

`SELECT city,ST_AsGeoJSON(geom) FROM attacks where country_text = 'Ireland'`

**Get nearest shops to selected location**

`SELECT DISTINCT name,shop,ST_AsGeoJSON(ST_Transform (way, 4326)) as way,
					ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me 
          FROM planet_osm_point where shop = 'supermarket' and name is not null
					ORDER BY dist_me ASC LIMIT 10;`
          
**Get the nearest waters**

'SELECT DISTINCT ST_AsGeoJSON(ST_Transform (way, 4326)) as way, 
					ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me
					FROM planet_osm_polygon where water is not null and name is not null and 
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) < 2000
					union
					SELECT DISTINCT ST_AsGeoJSON(ST_Transform (way, 4326)) as way,
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me
					FROM planet_osm_polygon where waterway is not null and name is not null and 
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography )<2000
					ORDER BY dist_me ASC LIMIT 200;'
          
**Get the regions near to the border, and compute the number of victioms**

'select attacks.nkill, ST_AsGeoJSON(attacks.geom), attacks.geom, planet_osm_polygon.way,
        ST_AsGeoJSON(ST_Transform (planet_osm_polygon.way, 4326)), t3.sum
            from (select t1.name, t2.name, ST_AsGeoJSON(ST_Transform (t2.way, 4326)),t2.way
            from (select name, way from planet_osm_polygon where admin_level::int = 4) as t1,
              (select name, way from planet_osm_polygon where admin_level::int = 6) as t2
            where ST_Intersects( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))
            and not ST_Contains( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))) as planet_osm_polygon,
            (SELECT city, ST_AsGeoJSON(geom),geom,nkill FROM attacks where country_text = 'Ireland' and nkill::int > 0) as attacks,
            (select planet_osm_polygon.way, ST_AsGeoJSON(ST_Transform (planet_osm_polygon.way, 4326)), sum(attacks.nkill)
                				   from (select t1.name, t2.name, ST_AsGeoJSON(ST_Transform (t2.way, 4326)),t2.way
                           from (select name, way from planet_osm_polygon where admin_level::int = 4) as t1,
                              (select name, way from planet_osm_polygon where admin_level::int = 6) as t2
                           where ST_Intersects( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))
                							 and not ST_Contains( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))) as planet_osm_polygon,
                           (SELECT city, ST_AsGeoJSON(geom),geom,nkill FROM attacks where country_text = 'Ireland' and nkill::int > 0)                              as attacks
                				   where ST_Intersects(ST_SetSRID(attacks.geom,4326), ST_Transform (planet_osm_polygon.way, 4326))
                				   group by (planet_osm_polygon.way)) as t3		 
             where ST_Intersects(ST_SetSRID(attacks.geom,4326), ST_Transform (planet_osm_polygon.way, 4326)) 
             and planet_osm_polygon.way = t3.way'

### Response

The responses for queries are differents but every contains a geoinformation (points or polygons)
These infromation is transformed into a valid geojson format. For this reason i was using json library in python:

"data = {}
    data['type'] = 'FeatureCollection'
    datas = []
    shops = getAllshops();
    for i in range(len(shops)):
        data1 = {}
        data1['type'] = 'Feature'        
        properties = {}
        properties['name'] = shops[i][0]
        properties['type'] = shops[i][1]
        shop = json.loads(shops[i][2])
        data1['properties'] = properties
        data1['geometry'] = shop
        datas.append(data1)
        
    data['features'] = datas
    geo_json = json.dumps(data)"
