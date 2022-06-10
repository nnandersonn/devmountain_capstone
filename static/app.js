
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

function openPet(evt, petName){
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent")
    for (i=0; i<tabcontent.length; i++){
        tabcontent[i].style.display = "none"
    }

    tablinks = document.getElementsByClassName("tablinks")
    for (i=0; i<tablinks.length; i++){
        tablinks[i].className = tablinks[i].className.replace(" active", "")
    }

    document.getElementById(petName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Reactive nav bar
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger.addEventListener("click", mobileMenu);

function mobileMenu() {
    hamburger.classList.toggle("active");
    navMenu.classList.toggle("active");
}

const navLink = document.querySelectorAll(".nav-link");

navLink.forEach(n => n.addEventListener("click", closeMenu));

function closeMenu() {
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
}