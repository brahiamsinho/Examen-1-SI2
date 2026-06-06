import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import 'mobile_auth_theme.dart';

/// Tema Shadcn alineado con Paleta A mobile (oscuro suave).
class EmergenciasShadTheme {
  EmergenciasShadTheme._();

  static ShadThemeData dark() {
    return ShadThemeData(
      brightness: Brightness.dark,
      colorScheme: const ShadSlateColorScheme.dark(
        background: MobileAuthTheme.scaffoldBg,
        foreground: MobileAuthTheme.textPrimary,
        card: MobileAuthTheme.cardColor,
        cardForeground: MobileAuthTheme.textPrimary,
        popover: MobileAuthTheme.cardColor,
        popoverForeground: MobileAuthTheme.textPrimary,
        primary: MobileAuthTheme.accentIndigo,
        primaryForeground: MobileAuthTheme.textPrimary,
        secondary: MobileAuthTheme.inputFill,
        secondaryForeground: MobileAuthTheme.accentAmber,
        muted: MobileAuthTheme.inputFill,
        mutedForeground: MobileAuthTheme.textSecondary,
        accent: MobileAuthTheme.accentCyan,
        accentForeground: MobileAuthTheme.scaffoldBg,
        destructive: MobileAuthTheme.errorSoft,
        destructiveForeground: MobileAuthTheme.textPrimary,
        border: MobileAuthTheme.borderColor,
        input: MobileAuthTheme.borderColor,
        ring: MobileAuthTheme.accentIndigo,
      ),
    );
  }
}
