import gpxpy
import gpxpy.gpx
import plotly.express as px


def parse_file(file):
    
    gpx = gpxpy.parse(file)

    latitude = []
    longitude = []
    elevation = []
    seg_distance = []
    seg_speed = []
    time = []
    previous_point = None

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                latitude.append(point.latitude)
                longitude.append(point.longitude)
                elevation.append(point.elevation)
                time.append(point.time)

               

                speed = point.speed_between(previous_point)
                if speed is None:
                    speed = 0
                seg_speed.append(speed)

                distance = point.distance_3d(previous_point)
                if not distance:
                    distance = point.distance_2d(previous_point)
                if distance is None:
                    distance = 0
                seg_distance.append(distance)
                
                previous_point = point

    # map = px.line_mapbox(
    #     lon = longitude,
    #     lat = latitude,
    #     mapbox_style="carto-positron",
    #     # text = elevation
    #     zoom = 15
    # )

    # map.add_scattermapbox(
    #     lon = longitude,
    #     lat = latitude,
    #     hovertext = seg_speed,
    #     marker=dict(color=seg_speed, size=8)
    # )

    # map.show()
    # fig_html = map.to_html()

    

    return [latitude, longitude, elevation, time, seg_distance, seg_speed]