# ea-create-componente-principal.ps1
# D-008 — Diagrama componente principal (EA). Re-ejecutable.
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

function Add-Component {
    param([object]$Package, [string]$Name, [string]$Description = "")
    $el = $Package.Elements.AddNew($Name, "Component")
    if ($Description) { $el.Notes = $Description }
    if (-not $el.Update()) { throw "No se pudo crear componente: $Name" }
    $Package.Elements.Refresh()
    return $el
}

function Find-Or-AddComponent {
    param([object]$Package, [string]$Name, [string]$Description = "")
    $Package.Elements.Refresh()
    for ($i = 0; $i -lt $Package.Elements.Count; $i++) {
        $e = $Package.Elements.GetAt($i)
        if ($e.Name -eq $Name -and $e.Type -eq "Component") { return $e }
    }
    return Add-Component -Package $Package -Name $Name -Description $Description
}

function Add-Note {
    param([object]$Package, [string]$Name, [string]$Text)
    $el = $Package.Elements.AddNew($Name, "Note")
    $el.Notes = $Text
    if (-not $el.Update()) { throw "No se pudo crear nota: $Name" }
    $Package.Elements.Refresh()
    return $el
}

function Find-Or-AddNote {
    param([object]$Package, [string]$Name, [string]$Text)
    $Package.Elements.Refresh()
    for ($i = 0; $i -lt $Package.Elements.Count; $i++) {
        $e = $Package.Elements.GetAt($i)
        if ($e.Name -eq $Name -and $e.Type -eq "Note") {
            $e.Notes = $Text
            $e.Update() | Out-Null
            return $e
        }
    }
    return Add-Note -Package $Package -Name $Name -Text $Text
}

function Place-OnDiagram {
    param([object]$Diagram, [object]$Element, [int]$X, [int]$Y, [int]$W, [int]$H)
    $do = $Diagram.DiagramObjects.AddNew("", "")
    $do.ElementID = $Element.ElementID
    Set-DiagramBounds -DiagramObject $do -X $X -Y $Y -W $W -H $H
    $Diagram.DiagramObjects.Refresh()
}

function Clear-ElementConnectors {
    param([object]$Element)
    $Element.Connectors.Refresh()
    for ($i = $Element.Connectors.Count - 1; $i -ge 0; $i--) {
        $Element.Connectors.DeleteAt($i, $true)
    }
    $Element.Connectors.Refresh()
}

function Add-Dependency {
    param([object]$Client, [object]$Supplier, [string]$Name = "")
    $c = $Client.Connectors.AddNew($Name, "Dependency")
    $c.SupplierID = $Supplier.ElementID
    $c.ClientID = $Client.ElementID
    if (-not $c.Update()) {
        throw "Dependency fallo: $($Client.Name) -> $($Supplier.Name)"
    }
    $Client.Connectors.Refresh()
}

function Find-Or-CreatePackage {
    param([object]$Parent, [string]$Name, [string]$Description)
    $Parent.Packages.Refresh()
    for ($i = 0; $i -lt $Parent.Packages.Count; $i++) {
        $p = $Parent.Packages.GetAt($i)
        if ($p.Name -eq $Name) {
            Write-Host "Paquete existente: $Name (ID $($p.PackageID))"
            return $p
        }
    }
    $pkg = $Parent.Packages.AddNew($Name, "Package")
    $pkg.Notes = $Description
    if (-not $pkg.Update()) { throw "No se pudo crear paquete $Name" }
    $Parent.Packages.Refresh()
    Write-Host "Paquete creado: $Name (ID $($pkg.PackageID))"
    return $pkg
}

function Find-Or-CreateDiagram {
    param([object]$Package, [string]$Name, [string]$Description)
    $Package.Diagrams.Refresh()
    for ($i = 0; $i -lt $Package.Diagrams.Count; $i++) {
        $d = $Package.Diagrams.GetAt($i)
        if ($d.Name -eq $Name) {
            Write-Host "Diagrama existente: $Name (ID $($d.DiagramID))"
            return $d
        }
    }
    $diag = $Package.Diagrams.AddNew($Name, "Component")
    $diag.Notes = $Description
    if (-not $diag.Update()) { throw "No se pudo crear diagrama $Name" }
    $Package.Diagrams.Refresh()
    Write-Host "Diagrama creado: $Name (ID $($diag.DiagramID))"
    return $diag
}

# ── Main ─────────────────────────────────────────────────────────────
$repo = Get-EaRepository
$root = $repo.Models.GetAt(0)

$pkg = Find-Or-CreatePackage -Parent $root -Name "Componentes sistema" `
    -Description "D-008 Diagrama componente principal FastAPI"

$diag = Find-Or-CreateDiagram -Package $pkg `
    -Name "Diagrama componente principal del sistema" `
    -Description "PUDS componente principal. Hub FastAPI + modulos + capas + PostgreSQL."

# Limpiar canvas (borrar de atras hacia adelante)
$diag.DiagramObjects.Refresh()
for ($i = $diag.DiagramObjects.Count - 1; $i -ge 0; $i--) {
    $diag.DiagramObjects.DeleteAt($i, $false)
}
$diag.DiagramObjects.Refresh()
$diag.Update()

Write-Host "Creando / reutilizando componentes..."

# Nombres con salto de linea para que EA muestre el texto (cajas mas anchas)
$http = Find-Or-AddComponent $pkg 'HTTP / REST Requests' 'REST JSON web y movil'
$auth = Find-Or-AddComponent $pkg "Autenticacion / Autorizacion`nJWT + X-Tenant-Slug" 'Bearer JWT, tenant'
$api  = Find-Or-AddComponent $pkg 'Backend API (FastAPI)' 'app/main.py routers /api'

$mods = @(
    @('Acceso, Roles y Permisos', 'auth, roles, tenants'),
    @('Usuarios', 'usuarios'),
    @("Clientes y`nVehiculos", 'clientes_y_vehiculos'),
    @("Incidentes`nEmergencias", 'incidentes/emergencias'),
    @("Gestion Talleres`ny Tecnicos", 'talleres_y_tecnicos'),
    @("Inteligencia`ndel Incidente", 'modules/ai'),
    @("Priorizacion y`nAsignacion", 'ai rank'),
    @("Atencion de`nSolicitudes", 'taller_emergencias'),
    @("Finanzas y`nPagos SaaS", 'pagos, billing'),
    @("Notificaciones y`nComunicaciones", 'comunicaciones'),
    @("Historial y`nTrazabilidad", 'bitacora')
)
$modEls = @()
foreach ($m in $mods) { $modEls += Find-Or-AddComponent $pkg $m[0] $m[1] }

$layers = @(
    @('Routers', 'router.py'),
    @('URLs / Endpoints', 'main.py'),
    @("Schemas`nPydantic", 'schemas.py'),
    @('Services', 'service.py'),
    @("Permissions`nSecurity", 'dependencies'),
    @('Repositories', 'repository.py'),
    @("Models`nSQLAlchemy", 'models.py'),
    @("Migrations`nSQL", 'migrations'),
    @("Middleware`nTenant + CORS", 'tenant_middleware'),
    @("Static / Media`nevidencias", 'uploads mount')
)
$layerEls = @()
foreach ($l in $layers) { $layerEls += Find-Or-AddComponent $pkg $l[0] $l[1] }

$store = Find-Or-AddComponent $pkg "Almacenamiento medios`nImagenes / Audios" 'backend/uploads'
$ext   = Find-Or-AddComponent $pkg "Servicios externos`nMapas / IA / Push / Pagos" 'Stripe FCM IA SMTP'
$db    = Find-Or-AddComponent $pkg 'Base de datos (PostgreSQL)' 'PostgreSQL 15'
$dbText = "tenants, usuarios, roles, permisos,`nclientes, vehiculos, talleres, tecnicos,`nsolicitudes_emergencia, notificaciones,`nmensajes_solicitud, pagos, comisiones,`nbitacora, dispositivos_push, evidencias"
$dbNote = Find-Or-AddNote $pkg 'Nota_Tablas_PG' $dbText

$allEls = @($http, $auth, $api) + $modEls + $layerEls + @($store, $ext, $db)
foreach ($el in $allEls) { Clear-ElementConnectors $el }

Write-Host "Colocando en diagrama (cajas ampliadas)..."

# Layout: izquierda | centro | derecha | abajo
Place-OnDiagram $diag $http 520 20  170 50
Place-OnDiagram $diag $auth 720 20  200 55
Place-OnDiagram $diag $api  520 340 220 70

$modW = 200
$modH = 52
$y = 95
foreach ($el in $modEls) {
    Place-OnDiagram $diag $el 40 $y $modW $modH
    $y += 58
}

$layW = 165
$layH = 48
$y = 105
foreach ($el in $layerEls) {
    Place-OnDiagram $diag $el 900 $y $layW $layH
    $y += 52
}

Place-OnDiagram $diag $store 80  780 230 58
Place-OnDiagram $diag $ext   380 780 250 58
Place-OnDiagram $diag $db    720 770 260 58
Place-OnDiagram $diag $dbNote 720 840 260 95

Write-Host "Creando dependencias (sin duplicados)..."

Add-Dependency $http $api 'HTTPS'
Add-Dependency $auth $api 'JWT'

foreach ($el in $modEls) {
    Add-Dependency $el $api ''
}

# API solo hacia capa Routers; cadena interna a la derecha (como plantilla)
Add-Dependency $api $layerEls[0] ''
Add-Dependency $layerEls[0] $layerEls[3] 'invoca'
Add-Dependency $layerEls[3] $layerEls[5] 'usa'
Add-Dependency $layerEls[5] $layerEls[6] 'persiste'
Add-Dependency $layerEls[6] $db 'ORM async'

# Capas auxiliares desde API (sin cadena vertical confusa)
Add-Dependency $api $layerEls[1] ''
Add-Dependency $api $layerEls[2] ''
Add-Dependency $api $layerEls[4] ''
Add-Dependency $api $layerEls[7] ''
Add-Dependency $api $layerEls[8] ''
Add-Dependency $api $layerEls[9] 'uploads'

Add-Dependency $api $store 'uploads'
Add-Dependency $api $ext 'API externa'
Add-Dependency $api $db 'SQLAlchemy'
Add-Dependency $store $db 'metadatos'

$repo.SaveDiagram($diag.DiagramID)
$repo.ReloadDiagram($diag.DiagramID)
$repo.OpenDiagram($diag.DiagramID)

Write-Host ""
Write-Host "OK - Diagrama corregido en EA (diagramID $($diag.DiagramID))"
Write-Host "  1. View -> Zoom -> Fit in Window"
Write-Host "  2. Si falta texto: selecciona caja -> Font size 9-10"
Write-Host "  3. Line Style -> Direct en flechas dobladas"
Write-Host "  4. Ctrl+S y export PNG"
