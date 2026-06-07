import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../emergencias/presentation/widgets/offline_sync_bootstrap.dart';
import '../../../core/widgets/mobile/mobile_shell_widgets.dart';
import '../widgets/cliente_panel_ui.dart';

/// Bottom navigation + área de contenido para el área autenticada `/cliente/app/*`.
class ClienteAppShell extends StatelessWidget {
  const ClienteAppShell({super.key, required this.child});

  final Widget child;

  static bool _showBottomNav(String path) {
    if (path.startsWith('/cliente/app/vehiculos/')) return false;
    if (path.startsWith('/cliente/app/emergencias/')) return false;
    if (path.startsWith('/cliente/app/notificaciones/')) return false;
    if (path == '/cliente/app/notificaciones') return false;
    return true;
  }

  static int _indexForPath(String path) {
    if (path.startsWith('/cliente/app/perfil')) return 2;
    if (path.startsWith('/cliente/app/vehiculos')) return 1;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final loc = GoRouterState.of(context).uri.path;
    final showNav = _showBottomNav(loc);
    final index = _indexForPath(loc);

    return Scaffold(
      body: SafeArea(
        child: OfflineSyncBootstrap(child: child),
      ),
      bottomNavigationBar: showNav
          ? NavigationBar(
              selectedIndex: index,
              onDestinationSelected: (i) {
    return MobileAppShell(
      bottomNav: showNav
          ? ClientePanelBottomNav(
              index: index,
              onChanged: (i) {
                switch (i) {
                  case 0:
                    context.go('/cliente/app/home');
                  case 1:
                    context.go('/cliente/app/vehiculos');
                  default:
                    context.go('/cliente/app/perfil');
                }
              },
            )
          : null,
      child: child,
    );
  }
}
