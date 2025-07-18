let video, canvas, context, detector, imageData;

// INICIALITZACIONS

let aruco_marker2alumne = null;
let aruco_marker2control = null;

let controls_presents = [];

function onClickAruco2() {
  aruco_marker2alumne = JSON.parse(document.getElementById("aruco_marker2alumne").textContent);
  aruco_marker2control = JSON.parse(document.getElementById("aruco_marker2control").textContent);

  video = document.getElementById("aruco-video");
  canvas = document.getElementById("aruco-canvas");
  context = canvas.getContext("2d", { willReadFrequently: true });

  detector = new AR.Detector();

  // Primer intentem accedir a la càmera trasera
  navigator.mediaDevices.getUserMedia({ video: { facingMode: { exact: "environment" } } })
    .then(startStream)
    .catch(err => {
      console.warn("Càmera trasera no disponible, fem servir la per defecte:", err.message);

      // Si falla, fem servir qualsevol càmera
      return navigator.mediaDevices.getUserMedia({ video: true })
        .then(startStream)
        .catch(err2 => {
          console.error("No s'ha pogut accedir a cap càmera:", err2);
          show_no_camara();
        });
    });

  function show_no_camara() {
    const noCamaraDiv = document.getElementById("no-camara");
    if (noCamaraDiv) {
      noCamaraDiv.style.display = "block";
    } else {
      console.error("Div with ID 'no-camara' not found.");
    }
  }

  function startStream(stream) {
    video.srcObject = stream;

    video.onloadedmetadata = function () {
      const videoWidth = video.videoWidth;
      const videoHeight = video.videoHeight;
      const aspectRatio = videoWidth / videoHeight;

      const container = document.getElementById("info-control");
      const containerWidth = container.clientWidth;
      const scaledHeight = Math.round(containerWidth / aspectRatio);

      video.setAttribute("width", containerWidth);
      video.setAttribute("height", scaledHeight);

      canvas.width = containerWidth;
      canvas.height = scaledHeight;
      canvas.style.display = "block";

      neteja_prediccions();

      requestAnimationFrame(tick);
    };

    video.play();
  }
}



// TICK X FRAME

function tick() {
  requestAnimationFrame(tick);

  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    imageData = context.getImageData(0, 0, canvas.width, canvas.height);

    const markers = detector.detect(imageData);

    markers.forEach(marker => {

      pinta_nom_alumne_o_vermell(marker);
      marca_present(marker);

    });

    pinta_quants_hem_trobat();
  }
}

// MARCAR PRESENTS

function marca_present(marker) {
  if (marker === null || marker.id === undefined) {
    return
  }
  const markerId = marker.id.toString();
  const controlId = aruco_marker2control[markerId];
  if (!controlId) {
    return;
  }
  let control_ja_present = controls_presents.includes(controlId);
  if (control_ja_present) {
    return;
  }
  controls_presents.push(controlId);

  marcarPresentById(controlId);
}

function neteja_prediccions() {
  // Remove all divs with id starting with 'prediccio'
  document.querySelectorAll("div[id^='prediccio']").forEach(function (div) {
    div.remove();
  });
}

function neteja_controls_a_capturar(radios) {
  if (!radios || radios.length === 0) return;

  let first_radio = radios[0];
  let group = first_radio.closest('.btn-group');

  // Remove 'active' class from all '.btn' inside this group
  group.querySelectorAll('.btn').forEach(label => label.classList.remove('active'));

  // Uncheck all '.rad' inside this group
  group.querySelectorAll('.rad').forEach(radio => radio.checked = false);
}

function marcarPresentById(controlIdBase) {

  // Seleccionem tots els inputs que comencen pel mateix idBase
  const radios = document.querySelectorAll(`input[id^="${controlIdBase}"]`);

  neteja_controls_a_capturar(radios);

  radios.forEach(radio => {
    const label = radio.closest('label');

    if (radio.classList.contains('radPresent')) {
      radio.checked = true;
      label.classList.add('active');
    } else {
      radio.checked = false;
      label.classList.remove('active');
    }

  });
}

// PINTAR EL NOM DE L'ALUMNE O UN PUNT VERMELL

function pinta_nom_alumne_o_vermell(marker) {

  if (marker === null || marker.id === undefined) {
    return
  }

  const markerId = marker.id.toString();
  let { cx, cy } = calcula_centre_marcador(marker);

  let marcador_regonegut_com_alumne = aruco_marker2alumne.hasOwnProperty(markerId);
  if (marcador_regonegut_com_alumne) {
    // Dibuixa el nom de l'alumne en verd
    context.fillStyle = "lime";
    context.font = "16px monospace";
    context.fillText(aruco_marker2alumne[markerId], cx - 30, cy - 10);
  } else {
    // Dibuixa un punt vermell al centre
    context.beginPath();
    context.arc(cx, cy, 5, 0, 2 * Math.PI);
    context.fillStyle = "red";
    context.fill();
  }

}

function calcula_centre_marcador(marker) {
  const corners = marker.corners;
  let cx = 0, cy = 0;
  for (let i = 0; i < corners.length; i++) {
    cx += corners[i].x;
    cy += corners[i].y;
  }
  cx /= corners.length;
  cy /= corners.length;
  return { cx, cy };
}

// PINTAR QUANTS HEM TROBAT
function pinta_quants_hem_trobat() {
  // Pinta a la cantonada superior dreta del canvas
  // quants elements té controls_presents
  const quants = controls_presents.length;
  context.fillStyle = "black";
  context.font = "24px monospace";
  context.fillText(`Capturats: ${quants}`, canvas.width - 200, 30);

}

// CLICAR EL BOTÓ ARUCO2

document.addEventListener("DOMContentLoaded", function () {

  const aruco2Button2 = document.getElementById("usaaruco2");
  if (aruco2Button2) {
    aruco2Button2.addEventListener("click", onClickAruco2);
  } else {
    console.error("Button with ID 'usaaruco2' not found.");
  }

  const aruco2Button = document.getElementById("usaaruco");
  if (aruco2Button) {
    aruco2Button.addEventListener("click", onClickAruco2);
  } else {
    console.error("Button with ID 'usaaruco' not found.");
  }


});

