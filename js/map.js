import { googleMapsAPIKey } from './config.js';

async function initMap() {
  const response = await fetch("reportes.json");
  const data = await response.json();

  const center = { lat: 4.711, lng: -74.0721 };

  // Define colores según la densidad de robos
  function getColorBasedOnRobos(cantidad) {
    if (cantidad >= 10) return '#FF0000';  // Rojo (alta peligrosidad)
    if (cantidad >= 5) return '#FFA500';  // Naranja (moderada peligrosidad)
    return '#FFFF00';  // Amarillo (baja peligrosidad)
  }

  // Contar los robos por área (simplificado, podríamos hacer esto por barrio o coordenadas)
  const robosPorArea = {};
  data.forEach(robo => {
    const areaKey = `${robo.lat.toFixed(2)},${robo.lng.toFixed(2)}`;
    if (!robosPorArea[areaKey]) {
      robosPorArea[areaKey] = 0;
    }
    robosPorArea[areaKey]++;
  });

  // Estilos de mapa
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

  // Crear marcadores y círculos de peligro
  data.forEach((robo) => {
    const marker = new google.maps.Marker({
      position: { lat: robo.lat, lng: robo.lng },
      map: map,
      icon: {
        url: "https://co.pinterest.com/pin/2111131070417027/",
        scaledSize: new google.maps.Size(30, 30),
      },
      title: `Robo en ${robo.barrio}`,
    });

    // Agregar círculos según la cantidad de robos
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
      radius: 300, // Radio de la zona (ajustar según preferencia)
    });

    const infoWindow = new google.maps.InfoWindow({
      content: `
        <div style="font-family: 'Arial'; line-height: 1.4;">
          <strong style="color:#333">📍 Barrio:</strong> ${robo.barrio}<br>
          <strong style="color:#333">⏰ Hora:</strong> ${robo.hora}<br>
          <strong style="color:#333">🔍 Detalle:</strong> ${robo.detalle}
        </div>
      `,
    });

    marker.addListener("click", () => {
      infoWindow.open(map, marker);
    });
  });
}

window.initMap = initMap;

// Cargar el script de Google Maps dinámicamente
const script = document.createElement("script");
script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsAPIKey}&callback=initMap`;
script.async = true;
script.defer = true;
document.head.appendChild(script);
