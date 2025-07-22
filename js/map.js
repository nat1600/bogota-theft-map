import { googleMapsAPIKey } from './config.js';
//export const googleMapsAPIKey = "AIzaSyATpG42RkE_ouiT5AyhfkKl2OxAiepaTT0";



// Función Haversine para calcular distancia en metros
function getDistanceMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000; // Radio Tierra en metros
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;

  const a = 
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) *
    Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// Hacerla accesible para updateMapUI
window.getDistanceMeters = getDistanceMeters;

async function initMap() {
  try {
    const response = await fetch("reportes.json");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    const center = { lat: 4.711, lng: -74.0721 };

    function getColorBasedOnRobos(cantidad) {
      if (cantidad >= 10) return '#FF0000';
      if (cantidad >= 5) return '#FFA500';
      return '#FFFF00';
    }

    const robosPorArea = {};
    data.forEach(robo => {
      const areaKey = `${robo.lat.toFixed(2)},${robo.lng.toFixed(2)}`;
      if (!robosPorArea[areaKey]) {
        robosPorArea[areaKey] = 0;
      }
      robosPorArea[areaKey]++;
    });

    const styledMapType = new google.maps.StyledMapType(
      [
        {
          featureType: "all",
          elementType: "all",
          stylers: [
            { saturation: -20 },
            { lightness: 20 },
            { visibility: "on" },
          ],
        },
        {
          featureType: "poi",
          stylers: [{ visibility: "off" }],
        },
        {
          featureType: "transit",
          stylers: [{ visibility: "off" }],
        },
      ],
      { name: "Pretty Map" }
    );

    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 13,
      center: center,
      mapTypeControlOptions: {
        mapTypeIds: ["roadmap", "satellite", "hybrid", "terrain", "styled_map"],
      },
    });

    map.mapTypes.set("styled_map", styledMapType);
    map.setMapTypeId("styled_map");

    window.map = map;

    data.forEach((robo) => {
      const marker = new google.maps.Marker({
        position: { lat: robo.lat, lng: robo.lng },
        map: map,
        icon: {
          url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
          scaledSize: new google.maps.Size(30, 30),
        },
        title: `Robo en ${robo.barrio}`,
      });

      const areaKey = `${robo.lat.toFixed(2)},${robo.lng.toFixed(2)}`;
      const cantidadRobos = robosPorArea[areaKey];
      const colorZona = getColorBasedOnRobos(cantidadRobos);

      const dangerZoneCircle = new google.maps.Circle({
        strokeColor: colorZona,
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: colorZona,
        fillOpacity: 0.35,
        map: map,
        center: { lat: robo.lat, lng: robo.lng },
        radius: 300, // Radio visible, pero real clustering usa getDistanceMeters
      });

      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div class="custom-info-window">
            <div class="info-header">
              <div class="info-icon">
                <i class="fas fa-exclamation-triangle"></i>
              </div>
              <div class="info-title">Reporte de Seguridad</div>
            </div>
            <div class="info-details">
              <div class="info-detail">
                <i class="fas fa-map-marker-alt"></i>
                <span><strong>Barrio:</strong> ${robo.barrio}</span>
              </div>
              <div class="info-detail">
                <i class="fas fa-clock"></i>
                <span><strong>Hora:</strong> ${robo.hora}</span>
              </div>
              <div class="info-detail">
                <i class="fas fa-info-circle"></i>
                <span><strong>Detalle:</strong> ${robo.detalle}</span>
              </div>
            </div>
          </div>
        `,
      });

      marker.addListener("click", () => {
        infoWindow.open(map, marker);
      });
    });

    if (typeof window.updateMapUI === 'function') {
      window.updateMapUI(data);
    }

    console.log('Mapa cargado exitosamente con', data.length, 'reportes');

  } catch (error) {
    console.error('Error al cargar el mapa:', error);

    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 13,
      center: { lat: 4.711, lng: -74.0721 },
    });

    window.map = map;
  }
}

window.handleMapError = function() {
  console.error('Error al cargar Google Maps API');
  document.getElementById('map').innerHTML = `
    <div style="display: flex; align-items: center; justify-content: center; height: 100%; background: #f5f5f5; color: #666;">
      <div style="text-align: center;">
        <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 20px;"></i>
        <h3>Error al cargar el mapa</h3>
        <p>Verifica tu conexión a internet y la API key de Google Maps</p>
      </div>
    </div>
  `;
};

window.initMap = initMap;

const script = document.createElement("script");
script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsAPIKey}&callback=initMap&v=weekly`;
script.async = true;
script.defer = true;
script.onerror = window.handleMapError;
document.head.appendChild(script);
