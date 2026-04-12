// lib/core/theme/app_theme.dart
// =========================================================
// Tema centralizado de la app móvil
// Colores, tipografía y estilos consistentes
// =========================================================
import 'package:flutter/material.dart';

class AppTheme {
  // ── Colores primarios ───────────────────────────────────
  static const Color primaryColor = Color(0xFF1A237E);    // Azul profundo
  static const Color secondaryColor = Color(0xFFFF6F00);  // Naranja emergencia
  static const Color errorColor = Color(0xFFB71C1C);
  static const Color successColor = Color(0xFF2E7D32);

  // ── Tema claro ──────────────────────────────────────────
  static ThemeData get light => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: primaryColor,
      secondary: secondaryColor,
    ),
    fontFamily: 'Roboto',
    appBarTheme: const AppBarTheme(
      backgroundColor: primaryColor,
      foregroundColor: Colors.white,
      elevation: 0,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
    ),
  );
}
