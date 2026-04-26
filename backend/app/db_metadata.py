# Importación lateral: registra todas las tablas en Base.metadata (Alembic autogenerate).
# Orden: dependencias FK (Usuario antes que módulos que la referencian).
from app.modules.usuarios import models as _usuarios_models  # noqa: F401
from app.modules.permisos import models as _permisos_models  # noqa: F401
from app.modules.roles import models as _roles_models  # noqa: F401
from app.modules.auth import models as _auth_models  # noqa: F401
from app.modules.talleres import models as _talleres_models  # noqa: F401
from app.modules.vehiculos import models as _vehiculos_models  # noqa: F401
from app.modules.bitacora import models as _bitacora_models  # noqa: F401
from app.modules.emergencias import models as _emergencias_models  # noqa: F401
from app.modules.notificaciones import models as _notificaciones_models  # noqa: F401
from app.modules.mensajes_solicitud import models as _mensajes_solicitud_models  # noqa: F401
from app.modules.dispositivos_push import models as _dispositivos_push_models  # noqa: F401
from app.modules.pagos import models as _pagos_models  # noqa: F401
