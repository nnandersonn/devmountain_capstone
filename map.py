import plotly.express as px


def create_map(longitude, latitude, speed):
    map = px.line_mapbox(
        lon = longitude,
        lat = latitude,
        mapbox_style="carto-positron",
        # text = elevation
        zoom = 15
    )

    map.add_scattermapbox(
        lon = longitude,
        lat = latitude,
        hovertext = speed,
        marker=dict(color=speed, size=8)
    )


    map.update_layout(showlegend=False)
    map['layout'].update(margin=dict(l=0, r=0, b=0, t=0))

    m_h = map.to_html()
    return m_h