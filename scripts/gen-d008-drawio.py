"""Genera docs/diagrams/drawio/d008-componente-principal-sistema.drawio

Artefacto PUDS 4.4.1.1.1 — Diagrama de componente principal del sistema.
Layout alineado a plantilla académica (hub FastAPI + módulos + capas + BD).
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "diagrams" / "drawio" / "d008-componente-principal-sistema.drawio"


def esc(text: str) -> str:
    return html.escape(text).replace("\n", "&#xa;")


def comp(
    cid: str,
    val: str,
    x: int,
    y: int,
    w: int,
    h: int,
    fill: str = "#fff4cc",
    stroke: str = "#333333",
    bold: bool = False,
) -> str:
    sw = "2" if bold else "1"
    return f"""        <mxCell id="{cid}" value="{esc(val)}" style="shape=component;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};strokeWidth={sw};align=center;verticalAlign=middle;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>
        </mxCell>"""


def table_box(cid: str, val: str, x: int, y: int, parent: str = "dbpkg") -> str:
    return f"""        <mxCell id="{cid}" value="{esc(val)}" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;fontSize=10;align=center;" vertex="1" parent="{parent}">
          <mxGeometry x="{x}" y="{y}" width="88" height="28" as="geometry"/>
        </mxCell>"""


def edge(
    eid: str,
    src: str,
    tgt: str,
    label: str = "",
    dashed: bool = True,
    curved: bool = False,
) -> str:
    dash = "1" if dashed else "0"
    style = "curved=1;" if curved else "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    return f"""        <mxCell id="{eid}" value="{esc(label)}" style="{style}html=1;dashed={dash};endArrow=classic;endFill=1;strokeColor=#333333;fontSize=10;" edge="1" parent="1" source="{src}" target="{tgt}">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>"""


def main() -> None:
    cells: list[str] = [
        '        <mxCell id="0"/>',
        '        <mxCell id="1" parent="0"/>',
        """        <mxCell id="title" value="4.4.1.1.1  Diagrama de componente principal del sistema" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=15;fontStyle=1" vertex="1" parent="1">
          <mxGeometry x="320" y="8" width="760" height="28" as="geometry"/>
        </mxCell>""",
        """        <mxCell id="subtitle" value="Plataforma Inteligente de Atencion de Emergencias Vehiculares — Backend FastAPI" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontSize=11;fontColor=#555555;" vertex="1" parent="1">
          <mxGeometry x="280" y="34" width="840" height="22" as="geometry"/>
        </mxCell>""",
        comp("http", "WebSockets / Requests", 430, 58, 190, 50, "#ffe0e0"),
        comp("auth", "Autenticacion / Autorizacion\nJWT / Session", 660, 58, 230, 55, "#e8d4ff"),
        comp("api", "Backend API\n(FastAPI)", 510, 370, 250, 76, "#fff4cc", "#333333", True),
    ]

    mods = [
        ("m1", "Acceso, Roles\ny Permisos"),
        ("m2", "Usuarios"),
        ("m3", "Vehiculos"),
        ("m4", "Incidentes"),
        ("m5", "Gestion de Talleres\ny Tecnicos"),
        ("m6", "Inteligencia\ndel Incidente"),
        ("m7", "Priorizacion y\nAsignacion"),
        ("m8", "Atencion de\nSolicitudes"),
        ("m9", "Finanzas"),
        ("m10", "Notificaciones"),
        ("m11", "Historial y\nTrazabilidad"),
    ]
    for i, (mid, name) in enumerate(mods):
        cells.append(comp(mid, name, 30, 95 + i * 56, 220, 50))

    layers = [
        ("l1", "Routers"),
        ("l2", "URLs / Endpoints"),
        ("l3", "Schemas"),
        ("l4", "Services"),
        ("l5", "Permissions / Security"),
        ("l6", "Repositories"),
        ("l7", "Models"),
        ("l8", "Migrations"),
        ("l9", "Signals / Events"),
        ("l10", "Tasks / WebSockets"),
    ]
    layer_y0 = 95
    layer_h = 46
    layer_gap = 4
    for i, (lid, name) in enumerate(layers):
        y = layer_y0 + i * (layer_h + layer_gap)
        cells.append(comp(lid, name, 960, y, 180, layer_h, "#d6eaf8"))

    cells.extend(
        [
            comp(
                "store",
                "Almacenamiento de medios\n(Imagenes / Audios)",
                60,
                820,
                260,
                58,
                "#d5f5e3",
            ),
            comp(
                "ext",
                "Servicios externos\n(Mapas / IA / Push / Pagos)",
                360,
                820,
                280,
                58,
                "#d5f5e3",
            ),
            """        <mxCell id="dbpkg" value="Base de datos (PostgreSQL)" style="swimlane;whiteSpace=wrap;html=1;fillColor=#d5f5e3;strokeColor=#333333;fontStyle=1;fontSize=12;startSize=32;rounded=1;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="680" y="790" width="660" height="200" as="geometry"/>
        </mxCell>""",
        ]
    )

    tables = [
        ("t1", "usuarios", 16, 44),
        ("t2", "roles", 112, 44),
        ("t3", "permisos", 208, 44),
        ("t4", "clientes", 304, 44),
        ("t5", "vehiculos", 400, 44),
        ("t6", "talleres", 16, 84),
        ("t7", "incidentes", 112, 84),
        ("t8", "notificaciones", 208, 84),
        ("t9", "atenciones", 304, 84),
        ("t10", "pagos", 400, 84),
        ("t11", "tecnicos", 16, 124),
        ("t12", "evidencias", 112, 124),
        ("t13", "bitacora", 208, 124),
        ("t14", "historial", 304, 124),
        ("t15", "tenants", 400, 124),
    ]
    for tid, name, tx, ty in tables:
        cells.append(table_box(tid, name, tx, ty))

    cells.append(
        """        <mxCell id="flow_bracket" value="" style="endArrow=classic;startArrow=classic;html=1;dashed=1;strokeColor=#666666;strokeWidth=1;endFill=1;startFill=1;" edge="1" parent="1">
          <mxGeometry relative="1" as="geometry">
            <mxPoint x="1175" y="120" as="sourcePoint"/>
            <mxPoint x="1175" y="560" as="targetPoint"/>
          </mxGeometry>
        </mxCell>"""
    )

    eid = 100
    for mid, _ in mods:
        cells.append(edge(f"e{eid}", mid, "api", "", dashed=False, curved=True))
        eid += 1

    cells.append(edge(f"e{eid}", "http", "api", "", dashed=False, curved=True))
    eid += 1
    cells.append(edge(f"e{eid}", "auth", "api", "", dashed=False, curved=True))
    eid += 1

    for lid, _ in layers:
        cells.append(edge(f"e{eid}", "api", lid, "", dashed=False, curved=True))
        eid += 1

    for i in range(len(layers) - 1):
        cells.append(edge(f"e{eid}", layers[i][0], layers[i + 1][0], "", dashed=False))
        eid += 1

    cells.append(edge(f"e{eid}", "l1", "l4", "invoca"))
    eid += 1
    cells.append(edge(f"e{eid}", "l4", "l6", "usa"))
    eid += 1
    cells.append(edge(f"e{eid}", "l6", "l7", "persiste"))
    eid += 1
    cells.append(edge(f"e{eid}", "l7", "dbpkg", "ORM async"))
    eid += 1
    cells.append(edge(f"e{eid}", "api", "store", "", dashed=False, curved=True))
    eid += 1
    cells.append(edge(f"e{eid}", "api", "ext", "", dashed=False, curved=True))
    eid += 1
    cells.append(edge(f"e{eid}", "api", "dbpkg", "SQLAlchemy", dashed=False))
    eid += 1
    cells.append(edge(f"e{eid}", "store", "dbpkg", "metadatos"))
    eid += 1
    cells.append(edge(f"e{eid}", "ext", "dbpkg", "", dashed=True))
    eid += 1

    xml = f"""<mxfile host="app.diagrams.net" modified="2026-05-30T00:00:00.000Z" agent="Examen-SI2-agent" version="24.0.0" type="device">
  <diagram name="4.4.1.1.1 Componente principal" id="d008-componente-principal">
    <mxGraphModel dx="1500" dy="950" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1400" pageHeight="1020" math="0" shadow="0">
      <root>
{chr(10).join(cells)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")
    print(f"Written: {OUT}")


if __name__ == "__main__":
    main()
