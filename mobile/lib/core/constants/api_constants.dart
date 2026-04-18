// lib/core/constants/api_constants.dart
// =========================================================
// Constantes de la API — centralizadas aquí para no duplicar
// La URL base se lee de --dart-define en tiempo de compilación
// =========================================================

class ApiConstants {
  // Sin .env en runtime: usar --dart-define=API_BASE_URL=...
  // Debe coincidir con BACKEND_URL + API_PREFIX del .env raíz (p. ej. http://127.0.0.1:8000/api).
  // Android Emulator: suele ser http://10.0.2.2:8000/api
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',
  );

  // Endpoints
  static const String login = '$baseUrl/auth/login';
  static const String logout = '$baseUrl/auth/logout';
  static const String me = '$baseUrl/auth/me';
  static const String usuarios = '$baseUrl/usuarios';
  static const String vehiculos = '$baseUrl/vehiculos';
  static const String talleres = '$baseUrl/talleres';
  static const String tecnicos = '$baseUrl/tecnicos';
  static const String bitacora = '$baseUrl/bitacora';

  // Timeouts
  static const Duration connectTimeout = Duration(seconds: 10);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
