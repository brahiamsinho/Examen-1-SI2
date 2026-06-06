import 'package:flutter/material.dart';

import '../../theme/mobile_auth_theme.dart';

/// Fondo gradiente Paleta A para cualquier pantalla/shell mobile.
class MobileGradientBackground extends StatelessWidget {
  const MobileGradientBackground({super.key, required this.child, this.safeArea = true});

  final Widget child;
  final bool safeArea;

  @override
  Widget build(BuildContext context) {
    final body = DecoratedBox(
      decoration: const BoxDecoration(gradient: MobileAuthTheme.gradient),
      child: child,
    );
    return safeArea ? SafeArea(child: body) : body;
  }
}

/// Bottom nav pill reutilizable (cliente, técnico, taller).
class MobilePanelBottomNav extends StatelessWidget {
  const MobilePanelBottomNav({
    super.key,
    required this.index,
    required this.onChanged,
    required this.items,
  });

  final int index;
  final ValueChanged<int> onChanged;
  final List<({IconData icon, String label})> items;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: MobileAuthTheme.cardColor.withValues(alpha: 0.96),
        border: Border(top: BorderSide(color: MobileAuthTheme.borderColor.withValues(alpha: 0.8))),
      ),
      child: SafeArea(
        top: false,
        child: Padding(
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 8),
          child: Row(
            children: List.generate(items.length, (i) {
              final item = items[i];
              final selected = i == index;
              return Expanded(
                child: Material(
                  color: Colors.transparent,
                  child: InkWell(
                    onTap: () => onChanged(i),
                    borderRadius: BorderRadius.circular(14),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 200),
                      padding: const EdgeInsets.symmetric(vertical: 8),
                      decoration: BoxDecoration(
                        color: selected
                            ? MobileAuthTheme.accentIndigo.withValues(alpha: 0.22)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(14),
                        border: selected
                            ? Border.all(color: MobileAuthTheme.accentIndigo.withValues(alpha: 0.45))
                            : null,
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            item.icon,
                            size: 22,
                            color: selected ? cs.primary : cs.onSurface.withValues(alpha: 0.55),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            item.label,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                              color: selected ? cs.onSurface : cs.onSurface.withValues(alpha: 0.55),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
        ),
      ),
    );
  }
}

/// Shell estándar: gradiente + contenido + bottom nav opcional.
class MobileAppShell extends StatelessWidget {
  const MobileAppShell({
    super.key,
    required this.child,
    this.bottomNav,
  });

  final Widget child;
  final Widget? bottomNav;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(gradient: MobileAuthTheme.gradient),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: child,
        bottomNavigationBar: bottomNav,
      ),
    );
  }
}
