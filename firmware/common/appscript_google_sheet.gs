/*
 * Google Apps Script — backend de la hoja de cálculo del banco de medición.
 *
 * Se despliega como Web App (Deploy > New deployment > Web app) y su URL
 * /exec se coloca en firmware/common/config_local.py (SCRIPT_URL), que NO se
 * versiona. El ESP32 (esp32_ina228) y sheet.py publican datos por GET; la
 * lectura devuelve la pestaña como CSV.
 *
 *   Escritura:  ?hoja=<nombre>&<col>=<valor>&...      -> agrega una fila
 *   Lectura:    ?hoja=<nombre>&accion=leer            -> devuelve CSV
 *
 * PODA: la pestaña 'inbox' (buffer transitorio de ventanas del ESP32) se recorta
 * sola a las ultimas INBOX_MAX filas. Sin esto crecia sin limite y getDataRange()
 * se pasaba del timeout (y Sheets no podia ni abrir la hoja). Solo se poda 'inbox';
 * 'verificacion' y demas pestañas de resultados NO se tocan.
 */
var INBOX_MAX  = 300;  // filas de datos objetivo en 'inbox' tras podar
var INBOX_TRIG = 400;  // recien poda cuando pasa de esto (histeresis): asi ~99%
                       // de las escrituras NO borran filas -> casi no hay
                       // lectura-durante-poda (la carrera que dejaba p_avg vacio)

function doGet(e) {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var hoja = e.parameter.hoja || "inbox";
    var sh = ss.getSheetByName(hoja) || ss.insertSheet(hoja);

    // LECTURA: ?hoja=X&accion=leer  -> devuelve la pestaña como CSV
    if (e.parameter.accion === "leer") {
      var vals = sh.getDataRange().getValues();
      return ContentService.createTextOutput(
        vals.map(function(r){ return r.join(","); }).join("\n")
      ).setMimeType(ContentService.MimeType.CSV);
    }

    // ESCRITURA: junta los params (menos hoja/accion) + fecha
    var params = { fecha: new Date() };
    Object.keys(e.parameter).forEach(function(k){
      if (k !== "hoja" && k !== "accion") params[k] = e.parameter[k];
    });

    // encabezado actual; agrega columnas para params nuevos
    var header = sh.getLastColumn() > 0
        ? sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0] : [];
    Object.keys(params).forEach(function(k){
      if (header.indexOf(k) === -1) {
        header.push(k);
        sh.getRange(1, header.length).setValue(k);
      }
    });

    // fila en el orden del encabezado: numeros como Number (decimales OK),
    // fecha como Date (legible, sin convertir a timestamp)
    function num(v){ return (v !== "" && !isNaN(v)) ? Number(v) : v; }
    sh.appendRow(header.map(function(k){
      if (k === "fecha") return params.fecha;
      return params.hasOwnProperty(k) ? num(params[k]) : "";
    }));

    // PODA solo del inbox, con HISTERESIS: recien cuando pasa de INBOX_TRIG
    // filas, borra de golpe hasta dejar INBOX_MAX. Asi la mayoria de las
    // escrituras no tocan filas (menos lectura-durante-poda).
    if (hoja === "inbox" && sh.getLastRow() - 1 > INBOX_TRIG) {
      var sobran = sh.getLastRow() - 1 - INBOX_MAX;    // -1 por el encabezado
      if (sobran > 0) sh.deleteRows(2, sobran);         // borra desde la fila 2
    }
    return ContentService.createTextOutput("OK");
  }

/* Vaciar el inbox a mano (correr desde el editor si alguna vez se llena de nuevo,
 * o para limpiar una hoja vieja sin abrir la grilla). Conserva el encabezado. */
function limpiarInbox() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName("inbox");
  if (!sh) return;
  var ncol = Math.max(sh.getLastColumn(), 1);
  var enc = sh.getRange(1, 1, 1, ncol).getValues();
  sh.clearContents();
  sh.getRange(1, 1, 1, ncol).setValues(enc);
  SpreadsheetApp.flush();
}
