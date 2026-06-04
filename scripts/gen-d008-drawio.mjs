import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, "..", "docs", "diagrams", "drawio", "d008-componente-principal-sistema.drawio");

const esc = (t) =>
  t
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/\n/g, "&#xa;");

const comp = (cid, val, x, y, w, h, fill = "#fff4cc", stroke = "#333333", bold = false) =>
  `        <mxCell id="${cid}" value="${esc(val)}" style="shape=component;whiteSpace=wrap;html=1;fillColor=${fill};strokeColor=${stroke};strokeWidth=${bold ? 2 : 1};align=center;verticalAlign=middle;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="${x}" y="${y}" width="${w}" height="${h}" as="geometry"/>
        </mxCell>`;

const table = (cid, val, x, y) =>
  `        <mxCell id="${cid}" value="${esc(val)}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;fontSize=10;align=center;" vertex="1" parent="dbpkg">
          <mxGeometry x="${x}" y="${y}" width="88" height="28" as="geometry"/>
        </mxCell>`;

const edge = (eid, src, tgt, label = "", dashed = true, curved = false) => {
  const dash = dashed ? "1" : "0";
  const style = curved
    ? "curved=1;"
    : "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;";
  return `        <mxCell id="${eid}" value="${esc(label)}" style="${style}html=1;dashed=${dash};endArrow=classic;endFill=1;strokeColor=#333333;fontSize=10;" edge="1" parent="1" source="${src}" target="${tgt}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>`;
};

const cells = [];
cells.push('        <mxCell id="0"/>', '        <mxCell id="1" parent="0"/>');
cells.push(`        <mxCell id="title" value="4.4.1.1.1  Diagrama de componente principal del sistema" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=15;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="320" y="8" width="760" height="28" as="geometry"/>
        </mxCell>`);
cells.push(`        <mxCell id="subtitle" value="Plataforma Inteligente de Atencion de Emergencias Vehiculares — Backend FastAPI" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;fontColor=#555555;" vertex="1" parent="1">
          <mxGeometry x="280" y="34" width="840" height="22" as="geometry"/>
        </mxCell>`);
cells.push(comp("http", "WebSockets / Requests", 430, 58, 190, 50, "#ffe0e0"));
cells.push(comp("auth", "Autenticacion / Autorizacion\nJWT / Session", 660, 58, 230, 55, "#e8d4ff"));
cells.push(comp("api", "Backend API\n(FastAPI)", 510, 370, 250, 76, "#fff4cc", "#333333", true));

const mods = [
  ["m1", "Acceso, Roles\ny Permisos"],
  ["m2", "Usuarios"],
  ["m3", "Vehiculos"],
  ["m4", "Incidentes"],
  ["m5", "Gestion de Talleres\ny Tecnicos"],
  ["m6", "Inteligencia\ndel Incidente"],
  ["m7", "Priorizacion y\nAsignacion"],
  ["m8", "Atencion de\nSolicitudes"],
  ["m9", "Finanzas"],
  ["m10", "Notificaciones"],
  ["m11", "Historial y\nTrazabilidad"],
];
mods.forEach(([id, name], i) => cells.push(comp(id, name, 30, 95 + i * 56, 220, 50)));

const layers = [
  ["l1", "Routers"],
  ["l2", "URLs / Endpoints"],
  ["l3", "Schemas"],
  ["l4", "Services"],
  ["l5", "Permissions / Security"],
  ["l6", "Repositories"],
  ["l7", "Models"],
  ["l8", "Migrations"],
  ["l9", "Signals / Events"],
  ["l10", "Tasks / WebSockets"],
];
layers.forEach(([id, name], i) => cells.push(comp(id, name, 960, 95 + i * 50, 180, 46, "#d6eaf8")));

cells.push(comp("store", "Almacenamiento de medios\n(Imagenes / Audios)", 60, 820, 260, 58, "#d5f5e3"));
cells.push(comp("ext", "Servicios externos\n(Mapas / IA / Push / Pagos)", 360, 820, 280, 58, "#d5f5e3"));
cells.push(`        <mxCell id="dbpkg" value="Base de datos (PostgreSQL)" style="swimlane;whiteSpace=wrap;html=1;fillColor=#d5f5e3;strokeColor=#333333;fontStyle=1;fontSize=12;startSize=32;rounded=1;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="680" y="790" width="660" height="200" as="geometry"/>
        </mxCell>`);

[
  ["t1", "usuarios", 16, 44],
  ["t2", "roles", 112, 44],
  ["t3", "permisos", 208, 44],
  ["t4", "clientes", 304, 44],
  ["t5", "vehiculos", 400, 44],
  ["t6", "talleres", 16, 84],
  ["t7", "incidentes", 112, 84],
  ["t8", "notificaciones", 208, 84],
  ["t9", "atenciones", 304, 84],
  ["t10", "pagos", 400, 84],
  ["t11", "tecnicos", 16, 124],
  ["t12", "evidencias", 112, 124],
  ["t13", "bitacora", 208, 124],
  ["t14", "historial", 304, 124],
  ["t15", "tenants", 400, 124],
].forEach((t) => cells.push(table(...t)));

cells.push(`        <mxCell id="flow_bracket" value="" style="endArrow=classic;startArrow=classic;html=1;dashed=1;strokeColor=#666666;strokeWidth=1;endFill=1;startFill=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1175" y="120" as="sourcePoint"/>
            <mxPoint x="1175" y="560" as="targetPoint"/>
          </mxGeometry>
        </mxCell>`);

let eid = 100;
mods.forEach(([id]) => cells.push(edge(`e${eid++}`, id, "api", "", false, true)));
cells.push(edge(`e${eid++}`, "http", "api", "", false, true));
cells.push(edge(`e${eid++}`, "auth", "api", "", false, true));
layers.forEach(([id]) => cells.push(edge(`e${eid++}`, "api", id, "", false, true)));
for (let i = 0; i < layers.length - 1; i++) {
  cells.push(edge(`e${eid++}`, layers[i][0], layers[i + 1][0], "", false, false));
}
cells.push(edge(`e${eid++}`, "l1", "l4", "invoca"));
cells.push(edge(`e${eid++}`, "l4", "l6", "usa"));
cells.push(edge(`e${eid++}`, "l6", "l7", "persiste"));
cells.push(edge(`e${eid++}`, "l7", "dbpkg", "ORM async"));
cells.push(edge(`e${eid++}`, "api", "store", "", false, true));
cells.push(edge(`e${eid++}`, "api", "ext", "", false, true));
cells.push(edge(`e${eid++}`, "api", "dbpkg", "SQLAlchemy", false));
cells.push(edge(`e${eid++}`, "store", "dbpkg", "metadatos"));
cells.push(edge(`e${eid++}`, "ext", "dbpkg", ""));

const xml = `<mxfile host="app.diagrams.net" modified="2026-05-30T00:00:00.000Z" agent="Examen-SI2-agent" version="24.0.0" type="device">
  <diagram name="4.4.1.1.1 Componente principal" id="d008-componente-principal">
    <mxGraphModel dx="1500" dy="950" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1020" math="0" shadow="0">
      <root>
${cells.join("\n")}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
`;

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, xml);
console.log(`Written: ${OUT}`);
