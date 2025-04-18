require('dotenv').config();

const googleMapsAPIKey = process.env.GOOGLE_MAPS_API_KEY;

async function initMap() {
  const response = await fetch("reportes.json");
  const data = await response.json();

  const center = { lat: 4.711, lng: -74.0721 }; // Bogotá
  const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 12,
      center: center,
  });

  data.forEach((robo) => {
      const marker = new google.maps.Marker({
          position: { lat: robo.lat, lng: robo.lng },
          map: map,
          title: `Robo en ${robo.barrio}`,
      });

      const infoWindowContent = `
          <div>
              <strong>Barrio:</strong> ${robo.barrio} <br>
              <strong>Hora:</strong> ${robo.hora} <br>
              <strong>Detalle:</strong> ${robo.detalle}
          </div>
      `;
      const infoWindow = new google.maps.InfoWindow({
          content: infoWindowContent,
      });

      marker.addListener("click", () => {
          infoWindow.open(map, marker);
      });
  });
}

function loadScript() {
  const script = document.createElement("script");
  script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsAPIKey}&callback=initMap`;
  document.head.appendChild(script);
}

window.onload = loadScript;