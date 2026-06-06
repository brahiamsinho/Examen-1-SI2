import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Paleta A — mobile completo (auth + paneles). Oscuro suave, sin blancos puros.
abstract final class MobileAuthTheme {
  // ── Superficies ───────────────────────────────────────────
  static const gradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF0B1020),
      Color(0xFF121A30),
      Color(0xFF0F1628),
    ],
  );

  static const scaffoldBg = Color(0xFF0B1020);
  static const cardColor = Color(0xFF141B2E);
  static const borderColor = Color(0xFF2A3658);
  static const inputFill = Color(0xFF1E2740);

  // ── Acentos ───────────────────────────────────────────────
  static const accentIndigo = Color(0xFF5C6BC0);
  static const accentCyan = Color(0xFF0EA5E9);
  static const accentAmber = Color(0xFFF59E0B);

  // ── Texto (no usar #FFFFFF en párrafos largos) ───────────
  static const textPrimary = Color(0xFFE8EAF6);
  static const textSecondary = Color(0xFF9FA8DA);
  static const textMuted = Color(0xFF7986CB);

  static const errorSoft = Color(0xFFEF5350);
  static const successSoft = Color(0xFF66BB6A);

  static BoxDecoration cardDecoration({Color? border}) => BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: border ?? borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.35),
            blurRadius: 24,
            offset: const Offset(0, 12),
          ),
        ],
      );

  static BoxDecoration selectorFieldDecoration({bool focused = false}) => BoxDecoration(
        color: inputFill,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: focused ? accentIndigo : borderColor,
          width: focused ? 1.5 : 1,
        ),
      );

  /// Esquema de color explícito (evita `fromSeed` que aclara superficies).
  static ColorScheme get colorScheme => const ColorScheme(
        brightness: Brightness.dark,
        primary: accentIndigo,
        onPrimary: textPrimary,
        primaryContainer: Color(0xFF283593),
        onPrimaryContainer: textPrimary,
        secondary: accentCyan,
        onSecondary: scaffoldBg,
        secondaryContainer: Color(0xFF1A3A52),
        onSecondaryContainer: textPrimary,
        tertiary: accentAmber,
        onTertiary: scaffoldBg,
        error: errorSoft,
        onError: textPrimary,
        surface: cardColor,
        onSurface: textPrimary,
        onSurfaceVariant: textSecondary,
        outline: borderColor,
        outlineVariant: Color(0xFF1E2740),
        shadow: Colors.black,
        scrim: Color(0xCC000000),
        inverseSurface: textPrimary,
        onInverseSurface: scaffoldBg,
        inversePrimary: accentIndigo,
        surfaceTint: Colors.transparent,
        surfaceContainerHighest: inputFill,
        surfaceContainerHigh: Color(0xFF1A2238),
        surfaceContainer: Color(0xFF161D32),
        surfaceContainerLow: Color(0xFF12182C),
        surfaceContainerLowest: scaffoldBg,
      );

  /// Tema Material global de la app (cliente, técnico, taller).
  static ThemeData get themeData {
    final cs = colorScheme;
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: cs,
      scaffoldBackgroundColor: scaffoldBg,
      canvasColor: scaffoldBg,
      fontFamily: 'Roboto',
      splashColor: accentIndigo.withValues(alpha: 0.12),
      highlightColor: accentIndigo.withValues(alpha: 0.08),
      dividerColor: borderColor.withValues(alpha: 0.7),
      iconTheme: const IconThemeData(color: textSecondary),
      appBarTheme: const AppBarTheme(
        backgroundColor: scaffoldBg,
        foregroundColor: textPrimary,
        elevation: 0,
        scrolledUnderElevation: 0,
        surfaceTintColor: Colors.transparent,
        systemOverlayStyle: SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Brightness.light,
          systemNavigationBarColor: cardColor,
          systemNavigationBarIconBrightness: Brightness.light,
        ),
      ),
      cardTheme: CardThemeData(
        color: cardColor,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderColor),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: cardColor,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titleTextStyle: const TextStyle(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w700,
        ),
        contentTextStyle: const TextStyle(color: textSecondary, height: 1.4),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: cardColor,
        surfaceTintColor: Colors.transparent,
        modalBackgroundColor: cardColor,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: inputFill,
        contentTextStyle: const TextStyle(color: textPrimary),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: cardColor.withValues(alpha: 0.96),
        indicatorColor: accentIndigo.withValues(alpha: 0.22),
        surfaceTintColor: Colors.transparent,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 11,
            fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
            color: selected ? textPrimary : textMuted,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected ? accentIndigo : textMuted,
            size: 22,
          );
        }),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: accentIndigo,
          foregroundColor: textPrimary,
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: accentIndigo,
          foregroundColor: textPrimary,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: textPrimary,
          side: const BorderSide(color: borderColor),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: accentCyan),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: inputFill,
        labelStyle: const TextStyle(color: textSecondary),
        hintStyle: TextStyle(color: textMuted.withValues(alpha: 0.85)),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: borderColor),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: accentIndigo, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: errorSoft.withValues(alpha: 0.8)),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      dropdownMenuTheme: DropdownMenuThemeData(
        menuStyle: MenuStyle(
          backgroundColor: WidgetStatePropertyAll(inputFill),
          surfaceTintColor: const WidgetStatePropertyAll(Colors.transparent),
        ),
        textStyle: const TextStyle(color: textPrimary),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: inputFill,
        selectedColor: accentIndigo.withValues(alpha: 0.25),
        disabledColor: inputFill.withValues(alpha: 0.5),
        labelStyle: const TextStyle(color: textPrimary, fontSize: 13),
        secondaryLabelStyle: const TextStyle(color: textSecondary),
        side: const BorderSide(color: borderColor),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
        checkmarkColor: accentIndigo,
      ),
      progressIndicatorTheme: const ProgressIndicatorThemeData(
        color: accentIndigo,
        linearTrackColor: borderColor,
      ),
      listTileTheme: const ListTileThemeData(
        iconColor: textSecondary,
        textColor: textPrimary,
      ),
      textTheme: const TextTheme(
        displayLarge: TextStyle(color: textPrimary),
        displayMedium: TextStyle(color: textPrimary),
        displaySmall: TextStyle(color: textPrimary),
        headlineLarge: TextStyle(color: textPrimary, fontWeight: FontWeight.w800),
        headlineMedium: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
        headlineSmall: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
        titleLarge: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
        titleMedium: TextStyle(color: textPrimary, fontWeight: FontWeight.w600),
        titleSmall: TextStyle(color: textPrimary, fontWeight: FontWeight.w600),
        bodyLarge: TextStyle(color: textPrimary, height: 1.4),
        bodyMedium: TextStyle(color: textSecondary, height: 1.4),
        bodySmall: TextStyle(color: textMuted, height: 1.35),
        labelLarge: TextStyle(color: textSecondary, fontWeight: FontWeight.w600),
        labelMedium: TextStyle(color: textMuted),
        labelSmall: TextStyle(color: textMuted, letterSpacing: 0.4),
      ),
    );
  }
}
