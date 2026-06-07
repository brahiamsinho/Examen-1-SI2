import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/widgets/mobile/mobile_shell_widgets.dart';

/// Navegación principal técnico: Inicio · Servicios · Perfil.
class TecnicoAppShell extends StatelessWidget {
  const TecnicoAppShell({super.key, required this.child});

  final Widget child;

  static const _navItems = [
    (icon: Icons.home_rounded, label: 'Inicio'),
    (icon: Icons.assignment_rounded, label: 'Servicios'),
    (icon: Icons.person_rounded, label: 'Perfil'),
  ];

  static bool _showBottomNav(String path) {
    if (path.startsWith('/tecnico/app/historial')) return false;
    if (path.startsWith('/tecnico/app/notificaciones')) return false;
    // Detalle / ubicación / estado / chat: pantalla completa sin barra inferior.
    if (path.startsWith('/tecnico/app/servicios/')) return false;
    return true;
  }

  static int _indexForPath(String path) {
    if (path.startsWith('/tecnico/app/perfil')) return 2;
    if (path.startsWith('/tecnico/app/servicios')) return 1;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final loc = GoRouterState.of(context).uri.path;
    final showNav = _showBottomNav(loc);
    final index = _indexForPath(loc);

    return MobileAppShell(
      bottomNav: showNav
          ? MobilePanelBottomNav(
              index: index,
              items: _navItems,
              onChanged: (i) {
                switch (i) {
                  case 0:
                    context.go('/tecnico/app/inicio');
                  case 1:
                    context.go('/tecnico/app/servicios');
                  default:
                    context.go('/tecnico/app/perfil');
                }
              },
            )
          : null,
      child: child,
    );
  }
}
