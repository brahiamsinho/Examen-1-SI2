// lib/core/constants/api_constants.dart
// =========================================================
// Constantes de la API — centralizadas aquí para no duplicar
// La URL base se lee de --dart-define en tiempo de compilación
// =========================================================

class ApiConstants {
  // En desarrollo: apuntar al backend local
  // En producción: definir con --dart-define=API_BASE_URL=https://tu-dominio.com/api/v1
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api', // 10.0.2.2 = localhost desde Android Emulator
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
