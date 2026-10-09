document.addEventListener("DOMContentLoaded", () => {
  const loaderOverlay = document.getElementById("loader-overlay");

  // Inicializar mapa de Leaflet
  const map = L.map("map", {
    zoomControl: false,
  }).setView([-9.19, -75.015], 6);

  // Mover control de zoom a la esquina inferior izquierda
  L.control.zoom({ position: "bottomleft" }).addTo(map);

  // Capa base de Esri
  L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    { attribution: "Tiles &copy; Esri" }
  ).addTo(map);

  // Escala de colores para mapa térmico
  function getColor(val) {
    if (val === null || val === undefined || isNaN(val)) {
      return "transparent";
    }
    return val > 25
      ? "#d73027"
      : val > 20
        ? "#f46d43"
        : val > 15
          ? "#fdae61"
          : val > 10
            ? "#fee08b"
            : val > 5
              ? "#d9ef8b"
              : "#91bfdb";
  }

  // Consumir API REST del servidor Flask
  fetch("https://app-geo-json-luis.onrender.com/api/raster-data")
    .then((res) => {
      if (!res.ok) throw new Error("Error en la respuesta del servidor");
      return res.json();
    })
    .then((raster) => {
      const bounds = L.latLngBounds(raster.bounds);

      // Renderizar matriz raster en Canvas
      const canvas = document.createElement("canvas");
      canvas.width = raster.width;
      canvas.height = raster.height;
      const ctx = canvas.getContext("2d");

      for (let y = 0; y < raster.height; y++) {
        for (let x = 0; x < raster.width; x++) {
          const val = raster.data[y][x];
          const color = getColor(val);
          if (color !== "transparent") {
            ctx.fillStyle = color;
            ctx.fillRect(x, y, 1, 1);
          }
        }
      }

      const imageUrl = canvas.toDataURL();
      const overlay = L.imageOverlay(imageUrl, bounds, {
        opacity: 0.7,
      }).addTo(map);
      
      map.fitBounds(bounds);

      // Ocultar Spinner de Carga
      loaderOverlay.style.opacity = "0";
      setTimeout(() => {
        loaderOverlay.style.visibility = "hidden";
      }, 400);

      // Evento de interacción al hacer clic en el mapa
      map.on("click", function (e) {
        if (!bounds.contains(e.latlng)) {
          map.closePopup();
          return;
        }

        const containerPoint = map.latLngToContainerPoint(e.latlng);
        const overlayElement = overlay.getElement();
        if (!overlayElement) return;

        const overlayRect = overlayElement.getBoundingClientRect();
        const mapRect = map.getContainer().getBoundingClientRect();

        const relX =
          (containerPoint.x - (overlayRect.left - mapRect.left)) /
          overlayRect.width;
        const relY =
          (containerPoint.y - (overlayRect.top - mapRect.top)) /
          overlayRect.height;

        if (relX < 0 || relX >= 1 || relY < 0 || relY >= 1) {
          map.closePopup();
          return;
        }

        const x = Math.floor(relX * raster.width);
        const y = Math.floor(relY * raster.height);

        const safeX = Math.max(0, Math.min(raster.width - 1, x));
        const safeY = Math.max(0, Math.min(raster.height - 1, y));

        const temp = raster.data[safeY][safeX];

        if (temp !== null && temp !== undefined && !isNaN(temp)) {
          L.popup()
            .setLatLng(e.latlng)
            .setContent(`<b>Temperatura Mínima:</b> ${temp} °C`)
            .openOn(map);
        } else {
          map.closePopup();
        }
      });
    })
    .catch((err) => {
      console.error("Error al cargar datos geoespaciales:", err);
      const loadingText = document.querySelector(".loading-text");
      if (loadingText) {
        loadingText.innerText =
          "Error al conectar con la API. Reintentando...";
      }
    });

  // Leyenda
  const legend = L.control({ position: "bottomright" });
  legend.onAdd = function () {
    const div = L.DomUtil.create("div", "legend");
    const grades = [0, 5, 10, 15, 20, 25];
    div.innerHTML = "<strong>Temperatura (°C)</strong><br>";
    for (let i = 0; i < grades.length; i++) {
      div.innerHTML +=
        '<i style="background:' +
        getColor(grades[i] + 1) +
        '"></i> ' +
        grades[i] +
        (grades[i + 1] ? "&ndash;" + grades[i + 1] + "<br>" : "+");
    }
    return div;
  };
  legend.addTo(map);
});