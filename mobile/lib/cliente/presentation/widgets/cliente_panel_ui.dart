import 'package:flutter/material.dart';

import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/mobile/mobile_shell_widgets.dart';

/// Layout y componentes del panel autenticado del cliente (`/cliente/app/*`).
abstract final class ClientePanelUi {
  static const pagePadding = EdgeInsets.fromLTRB(20, 8, 20, 24);
}

/// Fondo gradiente + SafeArea para tabs del shell.
typedef ClientePanelBackground = MobileGradientBackground;

/// Bottom nav estilo Paleta A (pill activo).
class ClientePanelBottomNav extends StatelessWidget {
  const ClientePanelBottomNav({
    super.key,
    required this.index,
    required this.onChanged,
  });

  final int index;
  final ValueChanged<int> onChanged;

  static const _items = [
    (icon: Icons.home_rounded, label: 'Inicio'),
    (icon: Icons.directions_car_rounded, label: 'Vehículos'),
    (icon: Icons.person_rounded, label: 'Perfil'),
  ];

  @override
  Widget build(BuildContext context) {
    return MobilePanelBottomNav(index: index, onChanged: onChanged, items: _items);
  }
}

/// Encabezado de tab (Inicio / Vehículos / Perfil).
class ClienteTabHeader extends StatelessWidget {
  const ClienteTabHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.trailing,
  });

  final String title;
  final String? subtitle;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.4,
                ),
              ),
              if (subtitle != null) ...[
                const SizedBox(height: 6),
                Text(
                  subtitle!,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.68),
                    height: 1.35,
                  ),
                ),
              ],
            ],
          ),
        ),
        if (trailing != null) trailing!,
      ],
    );
  }
}

/// Subpágina con botón atrás (emergencias, notificaciones, formularios).
class ClienteSubpageScaffold extends StatelessWidget {
  const ClienteSubpageScaffold({
    super.key,
    required this.title,
    required this.body,
    this.actions,
    this.onBack,
    this.useCloseIcon = false,
  });

  final String title;
  final Widget body;
  final List<Widget>? actions;
  final VoidCallback? onBack;
  final bool useCloseIcon;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: const BoxDecoration(gradient: MobileAuthTheme.gradient),
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(4, 4, 8, 0),
                child: Row(
                  children: [
                    IconButton(
                      onPressed: onBack ?? () => Navigator.maybePop(context),
                      icon: Icon(useCloseIcon ? Icons.close_rounded : Icons.arrow_back_rounded),
                    ),
                    Expanded(
                      child: Text(
                        title,
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                    ),
                    if (actions != null) ...actions!,
                  ],
                ),
              ),
              Expanded(child: body),
            ],
          ),
        ),
      ),
    );
  }
}

/// Tarjeta de acción rápida (home y menús).
class ClienteActionTile extends StatelessWidget {
  const ClienteActionTile({
    super.key,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
    this.accent = MobileAuthTheme.accentIndigo,
    this.emphasis = false,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final Color accent;
  final bool emphasis;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Material(
      color: MobileAuthTheme.cardColor,
      borderRadius: BorderRadius.circular(18),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(18),
        child: Ink(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            border: Border.all(
              color: emphasis ? accent.withValues(alpha: 0.55) : MobileAuthTheme.borderColor,
              width: emphasis ? 1.5 : 1,
            ),
            gradient: emphasis
                ? LinearGradient(
                    colors: [
                      accent.withValues(alpha: 0.12),
                      MobileAuthTheme.cardColor,
                    ],
                  )
                : null,
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                DecoratedBox(
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: accent.withValues(alpha: 0.35)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(10),
                    child: Icon(icon, color: accent, size: 24),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                      ),
                      const SizedBox(height: 3),
                      Text(
                        subtitle,
                        style: TextStyle(
                          fontSize: 12,
                          color: cs.onSurface.withValues(alpha: 0.65),
                          height: 1.35,
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right_rounded, color: cs.onSurface.withValues(alpha: 0.45)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Banner informativo (vehículos registrados, avisos).
class ClienteInfoBanner extends StatelessWidget {
  const ClienteInfoBanner({
    super.key,
    required this.message,
    this.icon = Icons.check_circle_outline_rounded,
    this.tone = ClienteBannerTone.success,
  });

  final String message;
  final IconData icon;
  final ClienteBannerTone tone;

  @override
  Widget build(BuildContext context) {
    final (bg, border, fg) = switch (tone) {
      ClienteBannerTone.success => (
          Colors.teal.withValues(alpha: 0.12),
          Colors.teal.withValues(alpha: 0.4),
          Colors.tealAccent.shade100,
        ),
      ClienteBannerTone.warning => (
          Colors.orange.withValues(alpha: 0.12),
          Colors.orange.withValues(alpha: 0.4),
          Colors.orange.shade200,
        ),
      ClienteBannerTone.info => (
          MobileAuthTheme.accentIndigo.withValues(alpha: 0.15),
          MobileAuthTheme.accentIndigo.withValues(alpha: 0.35),
          MobileAuthTheme.accentIndigo,
        ),
    };

    return DecoratedBox(
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: border),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(icon, color: fg, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.35),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

enum ClienteBannerTone { success, warning, info }

class ClienteSectionLabel extends StatelessWidget {
  const ClienteSectionLabel(this.text, {super.key});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10, top: 4),
      child: Text(
        text,
        style: Theme.of(context).textTheme.labelLarge?.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 0.4,
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.72),
            ),
      ),
    );
  }
}

class ClienteEmptyState extends StatelessWidget {
  const ClienteEmptyState({
    super.key,
    required this.icon,
    required this.title,
    required this.message,
    this.actionLabel,
    this.onAction,
  });

  final IconData icon;
  final String title;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28),
        child: DecoratedBox(
          decoration: MobileAuthTheme.cardDecoration(),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 52, color: cs.onSurface.withValues(alpha: 0.45)),
                const SizedBox(height: 16),
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text(
                  message,
                  textAlign: TextAlign.center,
                  style: TextStyle(color: cs.onSurface.withValues(alpha: 0.65), height: 1.4),
                ),
                if (actionLabel != null && onAction != null) ...[
                  const SizedBox(height: 20),
                  FilledButton(onPressed: onAction, child: Text(actionLabel!)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class ClienteFilterChips extends StatelessWidget {
  const ClienteFilterChips({
    super.key,
    required this.options,
    required this.selectedIndex,
    required this.onSelected,
  });

  final List<String> options;
  final int selectedIndex;
  final ValueChanged<int> onSelected;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: List.generate(options.length, (i) {
          final selected = i == selectedIndex;
          return Padding(
            padding: EdgeInsets.only(right: i < options.length - 1 ? 8 : 0),
            child: FilterChip(
              label: Text(options[i]),
              selected: selected,
              onSelected: (_) => onSelected(i),
              backgroundColor: MobileAuthTheme.inputFill,
              selectedColor: MobileAuthTheme.accentIndigo.withValues(alpha: 0.25),
              checkmarkColor: MobileAuthTheme.accentIndigo,
              side: BorderSide(
                color: selected
                    ? MobileAuthTheme.accentIndigo.withValues(alpha: 0.5)
                    : MobileAuthTheme.borderColor,
              ),
            ),
          );
        }),
      ),
    );
  }
}
