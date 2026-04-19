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

  /// Portal taller (responsable): taller y datos del responsable.
  static String get portalTallerMiTaller => '${AppEnv.apiBaseUrl}/portal/taller/mi-taller';

  // Portal móvil cliente (ciclo 1)
  static String get portalClienteRegistro => '${AppEnv.apiBaseUrl}/portal/cliente/registro';
  static String get portalClienteMiPerfil => '${AppEnv.apiBaseUrl}/portal/cliente/mi-perfil';
  static String get portalClienteMisVehiculos => '${AppEnv.apiBaseUrl}/portal/cliente/mis-vehiculos';

  static String portalClienteMisVehiculo(int id) =>
      '${AppEnv.apiBaseUrl}/portal/cliente/mis-vehiculos/$id';

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
