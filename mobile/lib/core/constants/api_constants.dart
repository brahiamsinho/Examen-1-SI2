// lib/core/constants/api_constants.dart
// =========================================================
// Rutas de la API — la base y timeouts vienen de mobile/.env (ver AppEnv).
// Prefijo de app móvil / web responsable: `/app/...` (antes `/portal/...`).
// =========================================================

import '../config/app_env.dart';

class ApiConstants {
  static String get baseUrl => AppEnv.apiBaseUrl;

  // Endpoints — auth
  static String get login => '${AppEnv.apiBaseUrl}/auth/login';
  static String get logout => '${AppEnv.apiBaseUrl}/auth/logout';
  static String get me => '${AppEnv.apiBaseUrl}/auth/me';
  static String get authSolicitarRecuperacionContrasena =>
      '${AppEnv.apiBaseUrl}/auth/solicitar-recuperacion-contrasena';

  /// App taller (responsable): taller y datos del responsable.
  static String get appTallerMiTaller => '${AppEnv.apiBaseUrl}/app/taller/mi-taller';
  static String get appTallerDashboard => '${AppEnv.apiBaseUrl}/app/taller/dashboard';
  static String get appTallerTecnicos => '${AppEnv.apiBaseUrl}/app/taller/tecnicos';
  static String appTallerTecnico(int id) => '${AppEnv.apiBaseUrl}/app/taller/tecnicos/$id';

  static String get appTallerEmergenciasBandejaDisponibles =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/bandeja/disponibles';

  static String appTallerEmergenciasBandejaDetalle(int bandejaId) =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/bandeja/$bandejaId';

  static String appTallerEmergenciasBandejaAceptar(int bandejaId) =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/bandeja/$bandejaId/aceptar';

  static String appTallerEmergenciasBandejaRechazar(int bandejaId) =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/bandeja/$bandejaId/rechazar';

  static String appTallerEmergenciasAsignarTecnico(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/solicitudes/$solicitudId/asignar-tecnico';

  static String appTallerEmergenciasAsignaciones(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/solicitudes/$solicitudId/asignaciones';

  static String get appTallerEmergenciasDisponibilidad =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/disponibilidad';

  static String get appTallerEmergenciasComisiones =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/comisiones';

  static String get appTallerEmergenciasComisionesResumen =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/comisiones/resumen';

  static String get appTallerEmergenciasHistorial =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/historial-atenciones';

  static String get appTallerEmergenciasReportesDashboard =>
      '${AppEnv.apiBaseUrl}/app/taller/emergencias/reportes/dashboard';

  static String get appTallerSuscripcion => '${AppEnv.apiBaseUrl}/app/taller/suscripcion';

  static String get appTallerBitacora => '${AppEnv.apiBaseUrl}/app/taller/bitacora';

  static String get appTallerBackups => '${AppEnv.apiBaseUrl}/app/taller/backups/';

  static String appTallerBackupDownload(int id) => '${AppEnv.apiBaseUrl}/app/taller/backups/$id/download';

  static String get appTallerReportesPlantillas => '${AppEnv.apiBaseUrl}/app/taller/reportes/plantillas';

  static String appTallerReportePlantillaRun(int id) =>
      '${AppEnv.apiBaseUrl}/app/taller/reportes/plantillas/$id/run';

  static String appTallerReportePlantilla(int id) =>
      '${AppEnv.apiBaseUrl}/app/taller/reportes/plantillas/$id';

  static String get appTallerReportesExecute => '${AppEnv.apiBaseUrl}/app/taller/reportes/execute';

  static String get appTallerReportesNlQuery => '${AppEnv.apiBaseUrl}/app/taller/reportes/nl-query';

  static String get appTallerReportesVoice => '${AppEnv.apiBaseUrl}/app/taller/reportes/voice';

  static String appTallerReporteExport(String fmt) =>
      '${AppEnv.apiBaseUrl}/app/taller/reportes/export/$fmt';

  /// App técnico — emergencias.
  static String get appTecnicoEmergenciasServiciosAsignados =>
      '${AppEnv.apiBaseUrl}/app/tecnico/emergencias/servicios-asignados';

  static String appTecnicoEmergenciaUbicacion(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/tecnico/emergencias/solicitudes/$solicitudId/ubicacion';

  static String appTecnicoEmergenciaUbicacionTecnico(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/tecnico/emergencias/solicitudes/$solicitudId/ubicacion-tecnico';

  static String appTecnicoEmergenciaEstado(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/tecnico/emergencias/solicitudes/$solicitudId/estado';

  static String appTecnicoEmergenciaMensajes(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/tecnico/emergencias/$solicitudId/mensajes';

  // App móvil cliente
  static String get appClienteRegistro => '${AppEnv.apiBaseUrl}/app/cliente/registro';
  static String get appClienteMiPerfil => '${AppEnv.apiBaseUrl}/app/cliente/mi-perfil';
  static String get appClienteMisVehiculos => '${AppEnv.apiBaseUrl}/app/cliente/mis-vehiculos';

  static String appClienteMisVehiculo(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/mis-vehiculos/$id';

  /// Solicitudes de emergencia (cliente autenticado).
  static String get appClienteEmergencias => '${AppEnv.apiBaseUrl}/app/cliente/emergencias';

  static String appClienteEmergencia(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id';

  /// Seguimiento, taller, técnico y ETA.
  static String appClienteEmergenciaSeguimiento(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/seguimiento';

  static String appClienteEmergenciaUbicacionTecnico(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/ubicacion-tecnico';

  static String appClienteEmergenciaTalleresCandidatos(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/talleres-candidatos';

  static String appClienteEmergenciaSeleccionarTaller(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/seleccionar-taller';

  static String appClienteEmergenciaUbicaciones(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/ubicaciones';

  static String appClienteEmergenciaEvidencias(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/evidencias';

  static String appClienteEmergenciaEvidenciasArchivo(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$id/evidencias/archivo';

  /// Notificaciones, mensajes y FCM.
  static String get appClienteNotificaciones =>
      '${AppEnv.apiBaseUrl}/app/cliente/notificaciones';

  static String appClienteNotificacionLeida(int id) =>
      '${AppEnv.apiBaseUrl}/app/cliente/notificaciones/$id/leida';

  static String appClienteEmergenciaMensajes(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$solicitudId/mensajes';

  /// Pagos por solicitud.
  static String appClienteEmergenciaPagos(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$solicitudId/pagos';

  static String appClienteEmergenciaPagoCompletarSimulado(int solicitudId, int pagoId) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$solicitudId/pagos/$pagoId/completar-simulado';

  static String appClienteEmergenciaPagoConfirmarStripe(int solicitudId, int pagoId) =>
      '${AppEnv.apiBaseUrl}/app/cliente/emergencias/$solicitudId/pagos/$pagoId/confirmar-stripe';

  static String get appClienteFcm => '${AppEnv.apiBaseUrl}/app/cliente/dispositivos/fcm';

  static String get appTecnicoFcm => '${AppEnv.apiBaseUrl}/app/tecnico/dispositivos/fcm';

  static String get usuarios => '${AppEnv.apiBaseUrl}/usuarios';
  static String get vehiculos => '${AppEnv.apiBaseUrl}/vehiculos';
  static String get vehiculosMarcas => '${AppEnv.apiBaseUrl}/vehiculos/marcas';
  static String vehiculosModelos({int? marcaId}) => marcaId != null
      ? '${AppEnv.apiBaseUrl}/vehiculos/modelos?marca_id=$marcaId'
      : '${AppEnv.apiBaseUrl}/vehiculos/modelos';
  static String get vehiculosTipos => '${AppEnv.apiBaseUrl}/vehiculos/tipos';
  static String get talleres => '${AppEnv.apiBaseUrl}/talleres';

  static String tallerById(int id) => '${AppEnv.apiBaseUrl}/talleres/$id';
  static String get tecnicos => '${AppEnv.apiBaseUrl}/tecnicos';
  static String get bitacora => '${AppEnv.apiBaseUrl}/bitacora';

  static Duration get connectTimeout => AppEnv.apiConnectTimeout;
  static Duration get receiveTimeout => AppEnv.apiReceiveTimeout;
}
