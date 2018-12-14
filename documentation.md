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

The application has 2 separate parts, the client which is a [frontend web application](#frontend) using mapbox API and mapbox.js and the [backend application](#backend) written in [Rails](http://rubyonrails.org/), backed by PostGIS. The frontend application communicates with backend using a [REST API](#api).

# Frontend

The frontend application is a static HTML page (`index.html`), which shows a mapbox.js widget. It is displaying hotels, which are mostly in cities, thus the map style is based on the Emerald style. I modified the style to better highlight main sightseeing points, restaurants and bus stops, since they are all important when selecting a hotel. I also highlighted rails tracks to assist in finding a quiet location.

All relevant frontend code is in `application.js` which is referenced from `index.html`. The frontend code is very simple, its only responsibilities are:
- detecting user's location, using the standard [web location API](https://developer.mozilla.org/en-US/docs/Web/API/Geolocation/Using_geolocation)
- displaying the sidebar panel with hotel list and filtering controls, driving the user interaction and calling the appropriate backend APIs
- displaying geo features by overlaying the map with a geojson layer, the geojson is provided directly by backend APIs

# Backend

The backend application is written in Python. This part of applicaion is responsible for comunicating with database and send data to frontend layer. For getting datas we used queryies and forcommunication we used flask.

## Data

Terror attack data is from Kaggle. I downloaded the full dataset and uplouaded it into database with my own py script. For this reason i used my own python script (load_terror.py).

Data about ireland were from Open Street Maps. I downloaded whole ireland (40 gb) and importet it using teh "osm2psql" tool.

## Api

**Find hotels in proximity to coordinates**

`GET /search?lat=25346&long=46346123`

**Find hotels by name, sorted by proximity and quality**

`GET /search?name=hviezda&lat=25346&long=46346123`

### Response

API calls return json responses with 2 top-level keys, `hotels` and `geojson`. `hotels` contains an array of hotel data for the sidebar, one entry per matched hotel. Hotel attributes are (mostly self-evident):
```
{
  "name": "Modra hviezda",
  "style": "modern", # cuisine style
  "stars": 3,
  "address": "Panska 31"
  "image_url": "/assets/hotels/652.png"
}
```
`geojson` contains a geojson with locations of all matched hotels and style definitions.
