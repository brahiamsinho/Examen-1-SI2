# Importación lateral: registra todas las tablas en Base.metadata (Alembic autogenerate).
# Orden: dependencias FK (Usuario antes que módulos que la referencian).
from app.modules.usuarios import models as _usuarios_models  # noqa: F401
from app.modules.acceso import models as _acceso_models  # noqa: F401
from app.modules.talleres import models as _talleres_models  # noqa: F401
from app.modules.vehiculos import models as _vehiculos_models  # noqa: F401
from app.modules.bitacora import models as _bitacora_models  # noqa: F401
from app.modules.emergencias import models as _emergencias_models  # noqa: F401
from app.modules.comunicaciones import models as _comunicaciones_models  # noqa: F401
from app.modules.pagos import models as _pagos_models  # noqa: F401
