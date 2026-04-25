// lib/core/constants/api_constants.dart
// =========================================================
// Rutas de la API — la base y timeouts vienen de mobile/.env (ver AppEnv).
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

  /// Portal taller (responsable): taller y datos del responsable.
  static String get portalTallerMiTaller => '${AppEnv.apiBaseUrl}/portal/taller/mi-taller';

  /// Portal técnico — emergencias (ciclo 3, CU32–CU35).
  static String get portalTecnicoEmergenciasServiciosAsignados =>
      '${AppEnv.apiBaseUrl}/portal/tecnico/emergencias/servicios-asignados';

  static String portalTecnicoEmergenciaUbicacion(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/tecnico/emergencias/solicitudes/$solicitudId/ubicacion';

  static String portalTecnicoEmergenciaUbicacionTecnico(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/tecnico/emergencias/solicitudes/$solicitudId/ubicacion-tecnico';

  static String portalTecnicoEmergenciaEstado(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/tecnico/emergencias/solicitudes/$solicitudId/estado';

  static String portalTecnicoEmergenciaMensajes(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/tecnico/emergencias/$solicitudId/mensajes';

  // Portal móvil cliente (ciclo 1)
  static String get portalClienteRegistro => '${AppEnv.apiBaseUrl}/portal/cliente/registro';
  static String get portalClienteMiPerfil => '${AppEnv.apiBaseUrl}/portal/cliente/mi-perfil';
  static String get portalClienteMisVehiculos => '${AppEnv.apiBaseUrl}/portal/cliente/mis-vehiculos';

  static String portalClienteMisVehiculo(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/mis-vehiculos/$id';

  /// Ciclo 2 fase 1 — solicitudes de emergencia (cliente autenticado).
  static String get portalClienteEmergencias => '${AppEnv.apiBaseUrl}/portal/cliente/emergencias';

  static String portalClienteEmergencia(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id';

  /// Ciclo 2 fase 2 — CU16–CU18 (seguimiento, taller, técnico, ETA).
  static String portalClienteEmergenciaSeguimiento(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id/seguimiento';

  static String portalClienteEmergenciaUbicacionTecnico(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id/ubicacion-tecnico';

  static String portalClienteEmergenciaUbicaciones(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id/ubicaciones';

  static String portalClienteEmergenciaEvidencias(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id/evidencias';

  static String portalClienteEmergenciaEvidenciasArchivo(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$id/evidencias/archivo';

  /// Ciclo 2 fase 3 — CU19 notificaciones, CU21 mensajes, FCM.
  static String get portalClienteNotificaciones =>
      '${AppEnv.apiBaseUrl}/portal/cliente/notificaciones';

  static String portalClienteNotificacionLeida(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/notificaciones/$id/leida';

  static String portalClienteEmergenciaMensajes(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$solicitudId/mensajes';

  /// Ciclo 2 fase 4 — CU20 pagos por solicitud.
  static String portalClienteEmergenciaPagos(int solicitudId) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$solicitudId/pagos';

  static String portalClienteEmergenciaPagoCompletarSimulado(int solicitudId, int pagoId) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$solicitudId/pagos/$pagoId/completar-simulado';

  static String portalClienteEmergenciaPagoConfirmarStripe(int solicitudId, int pagoId) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/emergencias/$solicitudId/pagos/$pagoId/confirmar-stripe';

  static String get portalClienteFcm => '${AppEnv.apiBaseUrl}/portal/cliente/dispositivos/fcm';

  static String get portalTecnicoFcm => '${AppEnv.apiBaseUrl}/portal/tecnico/dispositivos/fcm';

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
