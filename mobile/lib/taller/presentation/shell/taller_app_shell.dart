import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// Navegación principal responsable de taller.
class TallerAppShell extends StatelessWidget {
  const TallerAppShell({super.key, required this.child});

  final Widget child;

  static bool _showBottomNav(String path) {
    if (path.startsWith('/taller/app/bandeja/') && path != '/taller/app/bandeja') return false;
    if (path == '/taller/app/mas') return false;
    return true;
  }

  static int _indexForPath(String path) {
    if (path.startsWith('/taller/app/tecnicos')) return 2;
    if (path.startsWith('/taller/app/bandeja')) return 1;
    if (path.startsWith('/taller/app/perfil')) return 3;
    return 0;
  }

  @override
  Widget build(BuildContext context) {
    final loc = GoRouterState.of(context).uri.path;
    final showNav = _showBottomNav(loc);
    final index = _indexForPath(loc);

    return Scaffold(
      body: SafeArea(child: child),
      bottomNavigationBar: showNav
          ? NavigationBar(
              selectedIndex: index,
              onDestinationSelected: (i) {
                switch (i) {
                  case 0:
                    context.go('/taller/app/inicio');
                  case 1:
                    context.go('/taller/app/bandeja');
                  case 2:
                    context.go('/taller/app/tecnicos');
                  default:
                    context.go('/taller/app/perfil');
                }
              },
              destinations: const [
                NavigationDestination(
                  icon: Icon(Icons.dashboard_outlined),
                  selectedIcon: Icon(Icons.dashboard_rounded),
                  label: 'Inicio',
                ),
                NavigationDestination(
                  icon: Icon(Icons.inbox_outlined),
                  selectedIcon: Icon(Icons.inbox_rounded),
                  label: 'Bandeja',
                ),
                NavigationDestination(
                  icon: Icon(Icons.groups_outlined),
                  selectedIcon: Icon(Icons.groups_rounded),
                  label: 'Técnicos',
                ),
                NavigationDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person_rounded),
                  label: 'Perfil',
                ),
              ],
            )
          : null,
    );
  }
}
