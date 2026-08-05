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
 */
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
    return ContentService.createTextOutput("OK");
  }
