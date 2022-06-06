
function initMap(){
    map = new google.maps.Map(document.getElementById('map'), {center: {lat: lat[0], lng: lng[0]}, zoom: 15})
    
    var path = []

    for (var i=0; i<lat.length; i++){
        path.push(new google.maps.LatLng(lat[i], lng[i]))
    }

    const activityPath = new google.maps.Polyline({
        path: path,
        strokeColor: "#FF0000",
        strokeOpacity: 1,
        strokeWeight: 2,
        map:map,
    })

}