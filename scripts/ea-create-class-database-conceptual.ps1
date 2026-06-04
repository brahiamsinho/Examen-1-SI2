# ea-create-class-database-conceptual.ps1
# D-020 / 4.3.3.1.1 — Diagrama de clase conceptual BD (EA). Re-ejecutable.
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

function Find-ClassInPackage {
    param([object]$Package, [string]$Name)
    $Package.Elements.Refresh()
    for ($i = 0; $i -lt $Package.Elements.Count; $i++) {
        $e = $Package.Elements.GetAt($i)
        if ($e.Name -eq $Name -and $e.Type -eq "Class") { return $e }
    }
    return $null
}

function Set-ClassAttributes {
    param([object]$Element, [hashtable[]]$Attributes)
    $Element.Attributes.Refresh()
    $existing = @{}
    for ($i = 0; $i -lt $Element.Attributes.Count; $i++) {
        $a = $Element.Attributes.GetAt($i)
        $existing[$a.Name] = $a
    }
    foreach ($spec in $Attributes) {
        $attr = $null
        if ($existing.ContainsKey($spec.Name)) {
            $attr = $existing[$spec.Name]
        }
        else {
            $attr = $Element.Attributes.AddNew($spec.Name, $spec.Type)
        }
        $attr.Type = $spec.Type
        $attr.LowerBound = $spec.Order
        if (-not $attr.Update()) {
            throw "Atributo fallo en $($Element.Name): $($spec.Name)"
        }
    }
    $Element.Attributes.Refresh()
    $Element.Update() | Out-Null
}

function Add-Or-UpdateClass {
    param([object]$Package, [string]$Name, [hashtable[]]$Attributes)
    $el = Find-ClassInPackage -Package $Package -Name $Name
    if (-not $el) {
        $el = $Package.Elements.AddNew($Name, "Class")
        if (-not $el.Update()) { throw "No se pudo crear clase $Name" }
        $Package.Elements.Refresh()
        Write-Host "Clase creada: $Name (ID $($el.ElementID))"
    }
    else {
        Write-Host "Clase existente: $Name (ID $($el.ElementID))"
    }
    Set-ClassAttributes -Element $el -Attributes $Attributes
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

function Find-Association {
    param([object]$Source, [object]$Target, [string]$Name)
    $Source.Connectors.Refresh()
    for ($i = 0; $i -lt $Source.Connectors.Count; $i++) {
        $c = $Source.Connectors.GetAt($i)
        if ($c.Type -eq "Association" -and $c.SupplierID -eq $Target.ElementID -and $c.ClientID -eq $Source.ElementID) {
            if (-not $Name -or $c.Name -eq $Name) { return $c }
        }
    }
    return $null
}

function Add-Association {
    param(
        [object]$Source,
        [object]$Target,
        [string]$Name,
        [string]$SourceMult,
        [string]$TargetMult
    )
    $c = Find-Association -Source $Source -Target $Target -Name $Name
    if (-not $c) {
        $c = $Source.Connectors.AddNew($Name, "Association")
        $c.SupplierID = $Target.ElementID
        $c.ClientID = $Source.ElementID
    }
    else {
        $c.Name = $Name
    }
    $c.SupplierEnd.Role = $Name
    $c.SupplierEnd.Multiplicity = $TargetMult
    $c.ClientEnd.Multiplicity = $SourceMult
    if (-not $c.Update()) {
        throw "Asociacion fallo: $($Source.Name) -> $($Target.Name) ($Name)"
    }
    $Source.Connectors.Refresh()
}

# --- Main ---
$repo = Get-EaRepository
$model = $repo.Models.GetAt(0)

$pkgDiseno = Find-Or-CreatePackage -Parent $model -Name "Diseno de Datos Logico" -Description "PUDS 4.3.3"
$pkgDominio = Find-Or-CreatePackage -Parent $pkgDiseno -Name "Objetos de dominio" -Description "Entidades conceptuales BD"

$classes = @{
    Tenant = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "slug"; Type = "string"; Order = 1 },
        @{ Name = "nombre"; Type = "string"; Order = 2 },
        @{ Name = "estado"; Type = "string"; Order = 3 },
        @{ Name = "plan"; Type = "string"; Order = 4 }
    )
    Usuario = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "email"; Type = "string"; Order = 1 },
        @{ Name = "password_hash"; Type = "string"; Order = 2 },
        @{ Name = "estado"; Type = "string"; Order = 3 },
        @{ Name = "tenant_id"; Type = "int"; Order = 4 }
    )
    Rol = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "nombre"; Type = "string"; Order = 1 },
        @{ Name = "descripcion"; Type = "string"; Order = 2 }
    )
    UsuarioRol = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "usuario_id"; Type = "int"; Order = 1 },
        @{ Name = "rol_id"; Type = "int"; Order = 2 },
        @{ Name = "asignado_at"; Type = "datetime"; Order = 3 }
    )
    Cliente = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "usuario_id"; Type = "int"; Order = 1 },
        @{ Name = "tenant_id"; Type = "int"; Order = 2 },
        @{ Name = "ciudad"; Type = "string"; Order = 3 },
        @{ Name = "direccion"; Type = "string"; Order = 4 }
    )
    MarcaVehiculo = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "nombre"; Type = "string"; Order = 1 }
    )
    Vehiculo = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "placa"; Type = "string"; Order = 1 },
        @{ Name = "anio"; Type = "int"; Order = 2 },
        @{ Name = "color"; Type = "string"; Order = 3 },
        @{ Name = "tenant_id"; Type = "int"; Order = 4 }
    )
    Taller = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "nombre_comercial"; Type = "string"; Order = 1 },
        @{ Name = "direccion"; Type = "string"; Order = 2 },
        @{ Name = "latitud"; Type = "float"; Order = 3 },
        @{ Name = "longitud"; Type = "float"; Order = 4 },
        @{ Name = "tenant_id"; Type = "int"; Order = 5 },
        @{ Name = "estado"; Type = "string"; Order = 6 }
    )
    Tecnico = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "usuario_id"; Type = "int"; Order = 1 },
        @{ Name = "taller_id"; Type = "int"; Order = 2 },
        @{ Name = "estado"; Type = "string"; Order = 3 }
    )
    SolicitudEmergencia = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "descripcion_texto"; Type = "string"; Order = 1 },
        @{ Name = "estado"; Type = "string"; Order = 2 },
        @{ Name = "latitud"; Type = "float"; Order = 3 },
        @{ Name = "longitud"; Type = "float"; Order = 4 },
        @{ Name = "tenant_id"; Type = "int"; Order = 5 }
    )
    Pago = @(
        @{ Name = "id"; Type = "int"; Order = 0 },
        @{ Name = "monto"; Type = "float"; Order = 1 },
        @{ Name = "moneda"; Type = "string"; Order = 2 },
        @{ Name = "estado"; Type = "string"; Order = 3 },
        @{ Name = "metodo"; Type = "string"; Order = 4 },
        @{ Name = "referencia_externa"; Type = "string"; Order = 5 }
    )
}

$elements = @{}
foreach ($entry in $classes.GetEnumerator()) {
    $elements[$entry.Key] = Add-Or-UpdateClass -Package $pkgDominio -Name $entry.Key -Attributes $entry.Value
}

$associations = @(
    @{ Source = "Tenant"; Target = "Usuario"; Name = "agrupa"; SM = "1"; TM = "0..*" },
    @{ Source = "Tenant"; Target = "Cliente"; Name = "agrupa"; SM = "1"; TM = "0..*" },
    @{ Source = "Tenant"; Target = "Taller"; Name = "agrupa"; SM = "1"; TM = "0..*" },
    @{ Source = "Usuario"; Target = "Cliente"; Name = "es"; SM = "1"; TM = "0..1" },
    @{ Source = "Usuario"; Target = "Tecnico"; Name = "es"; SM = "1"; TM = "0..1" },
    @{ Source = "Usuario"; Target = "UsuarioRol"; Name = "tiene"; SM = "1"; TM = "0..*" },
    @{ Source = "Rol"; Target = "UsuarioRol"; Name = "define"; SM = "1"; TM = "0..*" },
    @{ Source = "MarcaVehiculo"; Target = "Vehiculo"; Name = "clasifica"; SM = "1"; TM = "0..*" },
    @{ Source = "Cliente"; Target = "Vehiculo"; Name = "posee"; SM = "1"; TM = "0..*" },
    @{ Source = "Cliente"; Target = "SolicitudEmergencia"; Name = "solicita"; SM = "1"; TM = "0..*" },
    @{ Source = "Vehiculo"; Target = "SolicitudEmergencia"; Name = "involucra"; SM = "1"; TM = "0..*" },
    @{ Source = "Taller"; Target = "Tecnico"; Name = "emplea"; SM = "1"; TM = "0..*" },
    @{ Source = "Taller"; Target = "SolicitudEmergencia"; Name = "atiende"; SM = "0..1"; TM = "0..*" },
    @{ Source = "Tecnico"; Target = "SolicitudEmergencia"; Name = "asigna"; SM = "0..1"; TM = "0..*" },
    @{ Source = "SolicitudEmergencia"; Target = "Pago"; Name = "genera"; SM = "1"; TM = "0..*" }
)

foreach ($a in $associations) {
    Add-Association -Source $elements[$a.Source] -Target $elements[$a.Target] `
        -Name $a.Name -SourceMult $a.SM -TargetMult $a.TM
}

$diagram = Find-Or-CreateDiagram -Package $pkgDominio -Name "DISEÑO CONCEPTUAL DE LA BASE DE DATOS"
$diagram.Notes = "Canónico académico 4.3.3.1.1 — atributos alineados backend"
$diagram.Update() | Out-Null

$layout = @(
    @{ Name = "Rol"; X = 60; Y = 70; W = 160; H = 100 },
    @{ Name = "UsuarioRol"; X = 260; Y = 70; W = 175; H = 110 },
    @{ Name = "Tenant"; X = 480; Y = 60; W = 180; H = 120 },
    @{ Name = "Taller"; X = 880; Y = 65; W = 200; H = 150 },
    @{ Name = "Usuario"; X = 260; Y = 250; W = 180; H = 130 },
    @{ Name = "Cliente"; X = 480; Y = 250; W = 180; H = 140 },
    @{ Name = "SolicitudEmergencia"; X = 870; Y = 240; W = 210; H = 150 },
    @{ Name = "MarcaVehiculo"; X = 60; Y = 520; W = 160; H = 80 },
    @{ Name = "Vehiculo"; X = 260; Y = 510; W = 180; H = 140 },
    @{ Name = "Tecnico"; X = 480; Y = 520; W = 180; H = 120 },
    @{ Name = "Pago"; X = 880; Y = 510; W = 200; H = 140 }
)

foreach ($pos in $layout) {
    Place-OnDiagram -Diagram $diagram -Element $elements[$pos.Name] `
        -X $pos.X -Y $pos.Y -W $pos.W -H $pos.H
}

$repo.ReloadDiagram($diagram.DiagramID)
Write-Host ""
Write-Host "OK — D-020 actualizado en EA."
Write-Host "  Paquete: Objetos de dominio (ID $($pkgDominio.PackageID))"
Write-Host "  Diagrama: DISEÑO CONCEPTUAL DE LA BASE DE DATOS (ID $($diagram.DiagramID))"
Write-Host "  View -> Zoom -> Fit in Window; Ctrl+S para guardar .eapx"
