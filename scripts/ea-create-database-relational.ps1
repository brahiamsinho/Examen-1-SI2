# ea-create-database-relational.ps1
# D-021 / PUDS 4.3.3 — Diagrama RELACIONAL de la base de datos (EA). Re-ejecutable.
# Tablas y FK alineadas a backend/migrations/*.sql + modelos ORM.
# Requisito: Enterprise Architect abierto con .eapx del examen.

$ErrorActionPreference = "Stop"

function Get-EaRepository {
    try {
        $app = [Runtime.InteropServices.Marshal]::GetActiveObject("EA.App")
        Write-Host "Conectado a EA en ejecucion."
    }
    catch {
        Write-Host "Iniciando Enterprise Architect..."
        $app = New-Object -ComObject EA.App
        $app.Visible = $true
    }
    $repo = $app.Repository
    if (-not $repo.ConnectionString) {
        throw "Abre tu proyecto .eapx en EA y vuelve a ejecutar este script."
    }
    return $repo
}

function Set-DiagramBounds {
    param([object]$DiagramObject, [int]$X, [int]$Y, [int]$W, [int]$H)
    $DiagramObject.left = $X
    $DiagramObject.right = $X + $W
    $DiagramObject.top = -($Y + $H)
    $DiagramObject.bottom = -$Y
    $DiagramObject.Update() | Out-Null
}

function Find-PackageByName {
    param([object]$Parent, [string]$Name)
    $Parent.Packages.Refresh()
    for ($i = 0; $i -lt $Parent.Packages.Count; $i++) {
        $p = $Parent.Packages.GetAt($i)
        if ($p.Name -eq $Name) { return $p }
    }
    return $null
}

function Find-Or-CreatePackage {
    param([object]$Parent, [string]$Name, [string]$Description = "")
    $found = Find-PackageByName -Parent $Parent -Name $Name
    if ($found) {
        Write-Host "Paquete existente: $Name (ID $($found.PackageID))"
        return $found
    }
    $pkg = $Parent.Packages.AddNew($Name, "Package")
    $pkg.Notes = $Description
    if (-not $pkg.Update()) { throw "No se pudo crear paquete $Name" }
    $Parent.Packages.Refresh()
    Write-Host "Paquete creado: $Name (ID $($pkg.PackageID))"
    return $pkg
}

function Find-TableInPackage {
    param([object]$Package, [string]$Name)
    $Package.Elements.Refresh()
    for ($i = 0; $i -lt $Package.Elements.Count; $i++) {
        $e = $Package.Elements.GetAt($i)
        if ($e.Name -eq $Name -and $e.Type -eq "Class") { return $e }
    }
    return $null
}

function Set-TableColumns {
    param([object]$Element, [object[]]$Columns)
    $Element.Attributes.Refresh()
    $existing = @{}
    for ($i = 0; $i -lt $Element.Attributes.Count; $i++) {
        $a = $Element.Attributes.GetAt($i)
        $existing[$a.Name] = $a
    }
    $order = 0
    foreach ($col in $Columns) {
        $parts = $col -split ":", 3
        $colName = $parts[0]
        $colType = $parts[1]
        $colFlags = if ($parts.Count -ge 3) { $parts[2] } else { "" }

        $attr = $null
        if ($existing.ContainsKey($colName)) {
            $attr = $existing[$colName]
        }
        else {
            $attr = $Element.Attributes.AddNew($colName, $colType)
        }
        $attr.Type = $colType
        $attr.LowerBound = $order
        if ($colFlags -match "PK") { $attr.Stereotype = "PK" }
        if ($colFlags -match "FK") { $attr.Stereotype = "FK" }
        if (-not $attr.Update()) {
            throw "Columna fallo en $($Element.Name): $colName"
        }
        $order++
    }
    $Element.Attributes.Refresh()
    $Element.Update() | Out-Null
}

function Add-Or-UpdateTable {
    param([object]$Package, [string]$Name, [object[]]$Columns)
    $el = Find-TableInPackage -Package $Package -Name $Name
    if (-not $el) {
        $el = $Package.Elements.AddNew($Name, "Class")
        if (-not $el.Update()) { throw "No se pudo crear tabla $Name" }
        $Package.Elements.Refresh()
        Write-Host "Tabla creada: $Name (ID $($el.ElementID))"
    }
    else {
        Write-Host "Tabla existente: $Name (ID $($el.ElementID))"
    }
    $el.Stereotype = "table"
    $el.Update() | Out-Null
    Set-TableColumns -Element $el -Columns $Columns
    return $el
}

function Find-Or-CreateDiagram {
    param([object]$Package, [string]$Name, [string]$Type = "Class")
    $Package.Diagrams.Refresh()
    for ($i = 0; $i -lt $Package.Diagrams.Count; $i++) {
        $d = $Package.Diagrams.GetAt($i)
        if ($d.Name -eq $Name) {
            Write-Host "Diagrama existente: $Name (ID $($d.DiagramID))"
            return $d
        }
    }
    $diag = $Package.Diagrams.AddNew($Name, $Type)
    if (-not $diag.Update()) { throw "No se pudo crear diagrama $Name" }
    $Package.Diagrams.Refresh()
    Write-Host "Diagrama creado: $Name (ID $($diag.DiagramID))"
    return $diag
}

function Place-OnDiagram {
    param([object]$Diagram, [object]$Element, [int]$X, [int]$Y, [int]$W, [int]$H)
    $found = $false
    $Diagram.DiagramObjects.Refresh()
    for ($i = 0; $i -lt $Diagram.DiagramObjects.Count; $i++) {
        $do = $Diagram.DiagramObjects.GetAt($i)
        if ($do.ElementID -eq $Element.ElementID) {
            Set-DiagramBounds -DiagramObject $do -X $X -Y $Y -W $W -H $H
            $found = $true
            break
        }
    }
    if (-not $found) {
        $do = $Diagram.DiagramObjects.AddNew("", "")
        $do.ElementID = $Element.ElementID
        Set-DiagramBounds -DiagramObject $do -X $X -Y $Y -W $W -H $H
    }
    $Diagram.DiagramObjects.Refresh()
}

function Find-FkConnector {
    param([object]$ChildTable, [object]$ParentTable, [string]$FkName)
    $ChildTable.Connectors.Refresh()
    for ($i = 0; $i -lt $ChildTable.Connectors.Count; $i++) {
        $c = $ChildTable.Connectors.GetAt($i)
        if ($c.Type -eq "Association" -and $c.SupplierID -eq $ParentTable.ElementID -and $c.ClientID -eq $ChildTable.ElementID) {
            if (-not $FkName -or $c.Name -eq $FkName) { return $c }
        }
    }
    return $null
}

function Add-Fk {
    param(
        [object]$ChildTable,
        [object]$ParentTable,
        [string]$FkColumn,
        [string]$ChildMult = "0..*",
        [string]$ParentMult = "1"
    )
    $c = Find-FkConnector -ChildTable $ChildTable -ParentTable $ParentTable -FkName $FkColumn
    if (-not $c) {
        $c = $ChildTable.Connectors.AddNew($FkColumn, "Association")
        $c.SupplierID = $ParentTable.ElementID
        $c.ClientID = $ChildTable.ElementID
    }
    else {
        $c.Name = $FkColumn
    }
    $c.Stereotype = "FK"
    $c.ClientEnd.Multiplicity = $ChildMult
    $c.SupplierEnd.Multiplicity = $ParentMult
    if (-not $c.Update()) {
        throw "FK fallo: $($ChildTable.Name).$FkColumn -> $($ParentTable.Name)"
    }
    $ChildTable.Connectors.Refresh()
}

function Get-TableHeight {
    param([int]$ColumnCount)
    return [Math]::Max(80, 44 + ($ColumnCount * 18))
}

# --- Main ---
$repo = Get-EaRepository
$model = $repo.Models.GetAt(0)

$pkgDiseno = Find-Or-CreatePackage -Parent $model -Name "Diseno de Datos Logico" -Description "PUDS 4.3.3"
$pkgRel = Find-Or-CreatePackage -Parent $pkgDiseno -Name "Modelo relacional" -Description "Tablas PostgreSQL + FK (diagrama relacional)"

# Columnas: "nombre:tipo:PK|FK" (flags opcionales)
$tableDefs = [ordered]@{
    tenants = @(
        "id:int:PK", "slug:varchar(80)", "nombre:varchar(150)", "estado:estado_tenant", "plan:plan_tenant"
    )
    roles = @("id:int:PK", "nombre:varchar(50)", "descripcion:varchar(255)")
    permisos = @("id:int:PK", "codigo:varchar(80)", "nombre:varchar(80)", "modulo:varchar(80)")
    usuarios = @(
        "id:int:PK", "email:varchar(120)", "password_hash:varchar(255)", "estado:estado_usuario",
        "tenant_id:int:FK", "nombres:varchar(100)", "apellidos:varchar(100)", "telefono:varchar(30)"
    )
    rol_permiso = @("id:int:PK", "rol_id:int:FK", "permiso_id:int:FK")
    usuario_rol = @("id:int:PK", "usuario_id:int:FK", "rol_id:int:FK", "asignado_at:timestamp")
    sesiones = @("id:int:PK", "usuario_id:int:FK", "token_jti:varchar(255)", "estado:estado_sesion", "expira_at:timestamp")
    usuario_tokens_seguridad = @("id:int:PK", "usuario_id:int:FK", "tipo:varchar(32)", "token_hash:varchar(64)", "expires_at:timestamp")
    clientes = @("id:int:PK", "usuario_id:int:FK", "tenant_id:int:FK", "ciudad:varchar(100)", "direccion:text")
    talleres = @(
        "id:int:PK", "tenant_id:int:FK", "usuario_responsable_id:int:FK", "nombre_comercial:varchar(150)",
        "direccion:text", "latitud:numeric", "longitud:numeric", "estado:estado_taller"
    )
    especialidades_tecnico = @("id:int:PK", "nombre:varchar(100)", "descripcion:varchar(255)")
    tecnicos = @(
        "id:int:PK", "usuario_id:int:FK", "taller_id:int:FK", "especialidad_id:int:FK",
        "estado:estado_tecnico", "documento_identidad:varchar(50)"
    )
    marcas_vehiculo = @("id:int:PK", "nombre:varchar(80)")
    modelos_vehiculo = @("id:int:PK", "marca_id:int:FK", "nombre:varchar(80)")
    tipos_vehiculo = @("id:int:PK", "nombre:varchar(50)")
    vehiculos = @(
        "id:int:PK", "tenant_id:int:FK", "cliente_id:int:FK", "placa:varchar(20)",
        "marca_id:int:FK", "modelo_id:int:FK", "tipo_vehiculo_id:int:FK", "anio:int", "color:varchar(50)"
    )
    solicitudes_emergencia = @(
        "id:int:PK", "tenant_id:int:FK", "cliente_id:int:FK", "vehiculo_id:int:FK",
        "taller_id:int:FK", "tecnico_id:int:FK", "estado:estado_solicitud", "descripcion_texto:text"
    )
    solicitud_ubicaciones = @(
        "id:int:PK", "solicitud_id:int:FK", "latitud:numeric", "longitud:numeric", "es_actual:boolean"
    )
    solicitud_evidencias = @("id:int:PK", "solicitud_id:int:FK", "tipo:tipo_evidencia", "archivo_url:text")
    solicitud_historial_estado = @(
        "id:int:PK", "solicitud_id:int:FK", "estado_anterior:estado_solicitud", "estado_nuevo:estado_solicitud", "usuario_id:int:FK"
    )
    notificaciones = @(
        "id:int:PK", "usuario_id:int:FK", "solicitud_id:int:FK", "tipo:tipo_notificacion", "titulo:varchar(150)", "leida:boolean"
    )
    solicitud_mensajes = @(
        "id:int:PK", "solicitud_id:int:FK", "emisor_usuario_id:int:FK", "receptor_usuario_id:int:FK", "mensaje:text"
    )
    usuario_fcm_tokens = @("id:int:PK", "usuario_id:int:FK", "token:text", "platform:varchar(20)")
    pagos = @(
        "id:int:PK", "solicitud_id:int:FK", "cliente_id:int:FK", "monto:numeric", "moneda:char(3)",
        "metodo:metodo_pago", "estado:estado_pago", "referencia_externa:varchar(255)"
    )
    comisiones_taller = @(
        "id:int:PK", "solicitud_id:int:FK", "taller_id:int:FK", "pago_id:int:FK",
        "monto_comision:numeric", "monto_taller_neto:numeric", "estado:estado_comision"
    )
    taller_disponibilidad = @(
        "id:int:PK", "taller_id:int:FK", "acepta_nuevas_solicitudes:boolean", "capacidad_maxima_diaria:int"
    )
    solicitud_taller_bandeja = @("id:int:PK", "solicitud_id:int:FK", "taller_id:int:FK", "estado:estado_bandeja")
    solicitud_asignaciones_tecnico = @(
        "id:int:PK", "solicitud_id:int:FK", "taller_id:int:FK", "tecnico_id:int:FK", "estado:estado_asignacion"
    )
    bitacora = @(
        "id:int:PK", "usuario_id:int:FK", "modulo:varchar(100)", "entidad:varchar(100)",
        "entidad_id:int", "accion:accion_bitacora", "ip_address:varchar(45)"
    )
}

$tables = @{}
foreach ($entry in $tableDefs.GetEnumerator()) {
    $tables[$entry.Key] = Add-Or-UpdateTable -Package $pkgRel -Name $entry.Key -Columns $entry.Value
}

# Foreign keys (child -> parent, label = column name)
$foreignKeys = @(
    @{ Child = "usuarios"; Parent = "tenants"; Fk = "tenant_id" },
    @{ Child = "clientes"; Parent = "tenants"; Fk = "tenant_id" },
    @{ Child = "clientes"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "talleres"; Parent = "tenants"; Fk = "tenant_id" },
    @{ Child = "talleres"; Parent = "usuarios"; Fk = "usuario_responsable_id" },
    @{ Child = "rol_permiso"; Parent = "roles"; Fk = "rol_id" },
    @{ Child = "rol_permiso"; Parent = "permisos"; Fk = "permiso_id" },
    @{ Child = "usuario_rol"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "usuario_rol"; Parent = "roles"; Fk = "rol_id" },
    @{ Child = "sesiones"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "usuario_tokens_seguridad"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "usuario_fcm_tokens"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "bitacora"; Parent = "usuarios"; Fk = "usuario_id"; ChildMult = "0..*"; ParentMult = "0..1" },
    @{ Child = "tecnicos"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "tecnicos"; Parent = "talleres"; Fk = "taller_id" },
    @{ Child = "tecnicos"; Parent = "especialidades_tecnico"; Fk = "especialidad_id"; ParentMult = "0..1" },
    @{ Child = "modelos_vehiculo"; Parent = "marcas_vehiculo"; Fk = "marca_id" },
    @{ Child = "vehiculos"; Parent = "tenants"; Fk = "tenant_id" },
    @{ Child = "vehiculos"; Parent = "clientes"; Fk = "cliente_id" },
    @{ Child = "vehiculos"; Parent = "marcas_vehiculo"; Fk = "marca_id" },
    @{ Child = "vehiculos"; Parent = "modelos_vehiculo"; Fk = "modelo_id" },
    @{ Child = "vehiculos"; Parent = "tipos_vehiculo"; Fk = "tipo_vehiculo_id" },
    @{ Child = "solicitudes_emergencia"; Parent = "tenants"; Fk = "tenant_id" },
    @{ Child = "solicitudes_emergencia"; Parent = "clientes"; Fk = "cliente_id" },
    @{ Child = "solicitudes_emergencia"; Parent = "vehiculos"; Fk = "vehiculo_id" },
    @{ Child = "solicitudes_emergencia"; Parent = "talleres"; Fk = "taller_id"; ParentMult = "0..1" },
    @{ Child = "solicitudes_emergencia"; Parent = "tecnicos"; Fk = "tecnico_id"; ParentMult = "0..1" },
    @{ Child = "solicitud_ubicaciones"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_evidencias"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_historial_estado"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_historial_estado"; Parent = "usuarios"; Fk = "usuario_id"; ParentMult = "0..1" },
    @{ Child = "notificaciones"; Parent = "usuarios"; Fk = "usuario_id" },
    @{ Child = "notificaciones"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id"; ParentMult = "0..1" },
    @{ Child = "solicitud_mensajes"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_mensajes"; Parent = "usuarios"; Fk = "emisor_usuario_id" },
    @{ Child = "solicitud_mensajes"; Parent = "usuarios"; Fk = "receptor_usuario_id" },
    @{ Child = "pagos"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "pagos"; Parent = "clientes"; Fk = "cliente_id" },
    @{ Child = "comisiones_taller"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "comisiones_taller"; Parent = "talleres"; Fk = "taller_id" },
    @{ Child = "comisiones_taller"; Parent = "pagos"; Fk = "pago_id"; ParentMult = "0..1" },
    @{ Child = "taller_disponibilidad"; Parent = "talleres"; Fk = "taller_id" },
    @{ Child = "solicitud_taller_bandeja"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_taller_bandeja"; Parent = "talleres"; Fk = "taller_id" },
    @{ Child = "solicitud_asignaciones_tecnico"; Parent = "solicitudes_emergencia"; Fk = "solicitud_id" },
    @{ Child = "solicitud_asignaciones_tecnico"; Parent = "talleres"; Fk = "taller_id" },
    @{ Child = "solicitud_asignaciones_tecnico"; Parent = "tecnicos"; Fk = "tecnico_id" }
)

foreach ($fk in $foreignKeys) {
    $childMult = if ($fk.ChildMult) { $fk.ChildMult } else { "0..*" }
    $parentMult = if ($fk.ParentMult) { $fk.ParentMult } else { "1" }
    Add-Fk -ChildTable $tables[$fk.Child] -ParentTable $tables[$fk.Parent] `
        -FkColumn $fk.Fk -ChildMult $childMult -ParentMult $parentMult
}

$diagram = Find-Or-CreateDiagram -Package $pkgRel -Name "DIAGRAMA RELACIONAL DE LA BASE DE DATOS"
$diagram.Notes = "PUDS 4.3.3 — modelo relacional PostgreSQL. Stereotype table + FK. Fuente: backend/migrations/"
$diagram.Update() | Out-Null

# Layout por zonas (x, y, w fijo 200)
$layout = @(
    @{ Name = "tenants"; X = 520; Y = 40 },
    @{ Name = "roles"; X = 40; Y = 40 },
    @{ Name = "permisos"; X = 40; Y = 180 },
    @{ Name = "rol_permiso"; X = 260; Y = 110 },
    @{ Name = "usuario_rol"; X = 260; Y = 250 },
    @{ Name = "usuarios"; X = 520; Y = 220 },
    @{ Name = "sesiones"; X = 760; Y = 220 },
    @{ Name = "usuario_tokens_seguridad"; X = 760; Y = 360 },
    @{ Name = "usuario_fcm_tokens"; X = 760; Y = 500 },
    @{ Name = "clientes"; X = 520; Y = 400 },
    @{ Name = "talleres"; X = 1020; Y = 40 },
    @{ Name = "especialidades_tecnico"; X = 1020; Y = 220 },
    @{ Name = "tecnicos"; X = 1020; Y = 360 },
    @{ Name = "taller_disponibilidad"; X = 1280; Y = 360 },
    @{ Name = "marcas_vehiculo"; X = 40; Y = 520 },
    @{ Name = "modelos_vehiculo"; X = 260; Y = 520 },
    @{ Name = "tipos_vehiculo"; X = 40; Y = 660 },
    @{ Name = "vehiculos"; X = 260; Y = 660 },
    @{ Name = "solicitudes_emergencia"; X = 520; Y = 580 },
    @{ Name = "solicitud_ubicaciones"; X = 760; Y = 640 },
    @{ Name = "solicitud_evidencias"; X = 760; Y = 780 },
    @{ Name = "solicitud_historial_estado"; X = 760; Y = 920 },
    @{ Name = "solicitud_mensajes"; X = 1020; Y = 640 },
    @{ Name = "notificaciones"; X = 1020; Y = 780 },
    @{ Name = "solicitud_taller_bandeja"; X = 1280; Y = 520 },
    @{ Name = "solicitud_asignaciones_tecnico"; X = 1280; Y = 660 },
    @{ Name = "pagos"; X = 520; Y = 820 },
    @{ Name = "comisiones_taller"; X = 520; Y = 980 },
    @{ Name = "bitacora"; X = 260; Y = 860 }
)

foreach ($pos in $layout) {
    $colCount = $tableDefs[$pos.Name].Count
    $h = Get-TableHeight -ColumnCount $colCount
    Place-OnDiagram -Diagram $diagram -Element $tables[$pos.Name] -X $pos.X -Y $pos.Y -W 200 -H $h
}

$repo.ReloadDiagram($diagram.DiagramID)
Write-Host ""
Write-Host "OK — Diagrama relacional D-021 en EA."
Write-Host "  Paquete: Modelo relacional (ID $($pkgRel.PackageID))"
Write-Host "  Diagrama: DIAGRAMA RELACIONAL DE LA BASE DE DATOS (ID $($diagram.DiagramID))"
Write-Host "  Tablas: $($tables.Count) | FK: $($foreignKeys.Count)"
Write-Host "  View -> Zoom -> Fit in Window; Line Style -> Direct; Ctrl+S"
