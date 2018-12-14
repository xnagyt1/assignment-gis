from flask import Flask, render_template, jsonify
import sys
import random
import json
import requests
from geojson import Point, Feature
import psycopg2

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = 'pk.eyJ1IjoieG5hZ3l0MSIsImEiOiJjanAwMHp4OHQyenVoM3FxaW1qNWR0MGE4In0.xU5ZQnYsmsoKulliOf0RLw'

@app.route("/")
def hello():
	return render_template('index.html')
'''
@app.route("/")
def hello():
	return render_template('heatmap.html')
'''
@app.route('/mapbox_js')
def mapbox_js():
	return render_template('mapbox_js.html')

@app.route('/test/')
def testsAll():
    data = {}
    data['type'] = 'FeatureCollection'
    datas = []
    attacks = getAllAttacksEnglandToo();
    for i in range(len(attacks)):
        data1 = {}
        data1['type'] = 'Feature'        
        properties = {}
        properties["city"] = attacks[i][0]
        attack = json.loads(attacks[i][1])
        attack['coordinates'].append(1)
        data1['properties'] = properties
        data1['geometry'] = attack
        datas.append(data1)
        
    data['features'] = datas
    geo_json = json.dumps(data)
    return geo_json

@app.route('/testShop/')
def testsShopsAll():
    data = {}
    data['type'] = 'FeatureCollection'
    datas = []
    shops = getAllshops();
    for i in range(len(shops)):
        data1 = {}
        data1['type'] = 'Feature'        
        properties = {}
        properties["name"] = shops[i][0]
        properties["type"] = shops[i][1]
        shop = json.loads(shops[i][2])
        data1['properties'] = properties
        data1['geometry'] = shop
        datas.append(data1)
        
    data['features'] = datas
    geo_json = json.dumps(data)
    return geo_json

@app.route('/testWater/<params>')
def testsWaterAll(params):
    start_p_long = float(params.split(",")[1].split("=")[1])
    start_p_lat = float(params.split(",")[0].split("=")[1])
    data = {}
    data['type'] = 'FeatureCollection'
    datas = []
    waters = getWaterAll(start_p_lat,start_p_long)
    for i in range(len(waters)):
        data1 = {}
        data1['type'] = 'Feature'        
        properties = {}
        properties['color'] = 'green'
        water = json.loads(waters[i][0])
        data1['properties'] = properties
        data1['geometry'] = water
        datas.append(data1)
        
    data['features'] = datas
    geo_json = json.dumps(data)
    return geo_json

@app.route('/testRegion/')
def testsRegionAll():
    data = {}
    data['type'] = 'FeatureCollection'
    datas = []
    region = getRegionAll()
    for i in range(len(region)):
        data1 = {}
        data1['type'] = 'Feature'        
        properties = {}
        properties["nkill"] = region[i][0]
        if region[i][5]<5:
            properties['color'] = 'green'
        elif region[i][5]<10:
            properties["color"] = 'yellow'
        elif region[i][5]<15:
            properties["color"] = 'orange'
        else:
            properties["color"] = 'red'
        water = json.loads(region[i][4])
        data1['properties'] = properties
        data1['geometry'] = water
        datas.append(data1)
        
    data['features'] = datas
    geo_json = json.dumps(data)
    return geo_json

@app.route('/attacks/')
def attacksAll():
    attacks = getAllAttacks()
    coords = [[json.loads(point[1])["coordinates"][0],json.loads(point[1])["coordinates"][1],point[0]] for point in attacks]
    return jsonify({"data": coords}) 
    
def getAllAttacks():
    conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
    cursor = conn.cursor()
    cursor.execute("""SELECT city,ST_AsGeoJSON(geom) FROM attacks where country_text = 'Ireland'""")
    attacks = cursor.fetchall()
    conn.close()
    cursor.close()
    return attacks

def getAllAttacksEnglandToo():
    conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
    cursor = conn.cursor()
    cursor.execute("""SELECT city,ST_AsGeoJSON(geom) FROM attacks where country_text = 'Ireland' or country_text = 'United Kingdom'""")
    attacks = cursor.fetchall()
    conn.close()
    cursor.close()
    return attacks
	
@app.route('/shops/<params>')
def shopsAll(params):
	start_p_long = float(params.split(",")[1].split("=")[1])
	start_p_lat = float(params.split(",")[0].split("=")[1])
	shops = getAllshops(start_p_long,start_p_lat)
	coords = [[json.loads(point[2])["coordinates"][0],json.loads(point[2])["coordinates"][1],point[0]] for point in shops]
	return jsonify({"data": coords}) 
    
def getAllshops(lat,lon):
    conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT name,shop,ST_AsGeoJSON(ST_Transform (way, 4326)) as way,
					ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me 
                    FROM planet_osm_point where shop = 'supermarket' and name is not null
					ORDER BY dist_me ASC
                    LIMIT 10;""",(lat,lon))
    shops = cursor.fetchall()
    conn.close()
    cursor.close()
    return shops
	
@app.route('/water/')
def waterAll():
	water = getWaterAll()
	coords = [json.loads(point[0]) for point in water]
	return jsonify({"data": coords})
	
def getWaterAll(lat,lon):
	conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
	cursor = conn.cursor()
	cursor.execute("""SELECT DISTINCT ST_AsGeoJSON(ST_Transform (way, 4326)) as way, 
					ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me
					FROM planet_osm_polygon where water is not null and name is not null and 
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) < 2000
					union
					SELECT DISTINCT ST_AsGeoJSON(ST_Transform (way, 4326)) as way,
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography ) as dist_me
					FROM planet_osm_polygon where waterway is not null and name is not null and 
				    ST_Distance(ST_Transform (way, 4326)::Geography , ST_SetSRID(ST_MakePoint(%s,%s), 4326)::Geography )<2000
					ORDER BY dist_me ASC LIMIT 200;""",(lon,lat,lon,lat,lon,lat,lon,lat))
	waters = cursor.fetchall()
	conn.close()
	cursor.close()
	return waters
	
@app.route('/region/')
def regionAll():
	region = getRegionAll()
	coords = [json.loads(point[0]) for point in region]
	return jsonify({"data": coords})
	
def getRegionAll():
	conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
	cursor = conn.cursor()
	#cursor.execute("""select DISTINCT ST_AsGeoJSON(ST_Transform (way, 4326)),name, admin_level from planet_osm_polygon where 
	#					admin_level::int >= 7 and ST_Intersects(ST_SetSRID(ST_MakePoint(-6.245485,53.361675),4326), ST_Transform (way, 4326));
	#				""")
	cursor.execute(""" select attacks.nkill, ST_AsGeoJSON(attacks.geom), attacks.geom, planet_osm_polygon.way, ST_AsGeoJSON(ST_Transform (planet_osm_polygon.way, 4326)), t3.sum
                	   from (select t1.name, t2.name, ST_AsGeoJSON(ST_Transform (t2.way, 4326)),t2.way
                				 from (select name, way from planet_osm_polygon where admin_level::int = 4) as t1,
                					  (select name, way from planet_osm_polygon where admin_level::int = 6) as t2
                				 where ST_Intersects( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))
                				 and not ST_Contains( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))															 
                	  		) as planet_osm_polygon,
                		   	(SELECT city, ST_AsGeoJSON(geom),geom,nkill FROM attacks where country_text = 'Ireland' and nkill::int > 0) as attacks,
                			(select planet_osm_polygon.way, ST_AsGeoJSON(ST_Transform (planet_osm_polygon.way, 4326)), sum(attacks.nkill)
                				   from (select t1.name, t2.name, ST_AsGeoJSON(ST_Transform (t2.way, 4326)),t2.way
                							 from (select name, way from planet_osm_polygon where admin_level::int = 4) as t1,
                								  (select name, way from planet_osm_polygon where admin_level::int = 6) as t2
                							 where ST_Intersects( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))
                							 and not ST_Contains( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))															 
                						) as planet_osm_polygon,
                						(SELECT city, ST_AsGeoJSON(geom),geom,nkill FROM attacks where country_text = 'Ireland' and nkill::int > 0) as attacks
                				   where ST_Intersects(ST_SetSRID(attacks.geom,4326), ST_Transform (planet_osm_polygon.way, 4326))
                				   group by (planet_osm_polygon.way)) as t3		 
                	   where ST_Intersects(ST_SetSRID(attacks.geom,4326), ST_Transform (planet_osm_polygon.way, 4326)) and planet_osm_polygon.way = t3.way""")
	regions = cursor.fetchall()
	conn.close()
	cursor.close()
	return regions

	
@app.route('/map/')
def mapAll():
	region = getRegionAll()
	coords = [json.loads(point[0]) for point in region]
	return jsonify({"data": coords})
	
def getMapAll():
	conn = psycopg2.connect("dbname='pdt_project' user='postgres' host='localhost' password='pg'")
	cursor = conn.cursor()
	cursor.execute("""select t1.name, t2.name, ST_AsGeoJSON(ST_Transform (t2.way, 4326)),t2.way
    				 from (select name, way from planet_osm_polygon where admin_level::int = 4) as t1,
    					  (select name, way from planet_osm_polygon where admin_level::int = 6) as t2
    				 where ST_Intersects( ST_Transform (t1.way, 4326), ST_Transform (t2.way, 4326))""")
	regions = cursor.fetchall()
	conn.close()
	cursor.close()
	return regions


	
if __name__ == '__main__':
    app.run(debug=True)
	