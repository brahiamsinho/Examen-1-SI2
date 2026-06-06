// lib/core/theme/app_theme.dart
// Tema centralizado — delega en MobileAuthTheme (Paleta A oscura).
import 'package:flutter/material.dart';

import 'mobile_auth_theme.dart';

class AppTheme {
  // Compatibilidad con código existente
  static const Color primaryColor = MobileAuthTheme.accentIndigo;
  static const Color secondaryColor = MobileAuthTheme.accentAmber;
  static const Color errorColor = MobileAuthTheme.errorSoft;
  static const Color successColor = MobileAuthTheme.successSoft;

  static ThemeData get dark => MobileAuthTheme.themeData;

  /// Tema claro reservado (no usado en producción mobile).
  static ThemeData get light => dark;
}
