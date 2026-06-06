import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/app_env.dart';
import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/auth/org_slug_selector.dart';

/// Selector de actor: cliente / técnico / responsable de taller.
class ActorSelectScreen extends StatefulWidget {
  const ActorSelectScreen({super.key});

  @override
  State<ActorSelectScreen> createState() => _ActorSelectScreenState();
}

class _ActorSelectScreenState extends State<ActorSelectScreen> {
  String _tenantSlug = AppEnv.tenantSlugDefault;
  bool _loadingSlug = true;

  @override
  void initState() {
    super.initState();
    _loadSlug();
  }

  Future<void> _loadSlug() async {
    final slug = await resolveInitialTenantSlug();
    if (!mounted) return;
    setState(() {
      _tenantSlug = slug;
      _loadingSlug = false;
    });
  }

  Future<void> _onSlugChanged(String slug) async {
    setState(() => _tenantSlug = slug);
    await persistTenantSlug(slug);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(gradient: MobileAuthTheme.gradient),
        child: SafeArea(
          child: ListView(
            padding: const EdgeInsets.fromLTRB(24, 16, 24, 32),
            children: [
              Row(
                children: [
                  DecoratedBox(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(14),
                      gradient: LinearGradient(
                        colors: [
                          AppTheme.primaryColor.withValues(alpha: 0.95),
                          MobileAuthTheme.accentIndigo,
                        ],
                      ),
                    ),
                    child: const Padding(
                      padding: EdgeInsets.all(12),
                      child: Icon(Icons.directions_car_filled_rounded, color: Colors.white, size: 28),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          AppEnv.appName,
                          style: theme.textTheme.titleLarge?.copyWith(
                            fontWeight: FontWeight.w700,
                            letterSpacing: -0.3,
                          ),
                        ),
                        Text(
                          'Plataforma multi-organización',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: cs.onSurface.withValues(alpha: 0.65),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 28),
              Text(
                '¿Cómo vas a usar la app?',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.4,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Elige tu perfil y la organización. Podrás cambiar de modo más adelante.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: cs.onSurface.withValues(alpha: 0.72),
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 22),
              DecoratedBox(
                decoration: MobileAuthTheme.cardDecoration(
                  border: MobileAuthTheme.accentIndigo.withValues(alpha: 0.35),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: _loadingSlug
                      ? const Center(
                          child: Padding(
                            padding: EdgeInsets.all(12),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        )
                      : OrgSlugSelector(
                          value: _tenantSlug,
                          onChanged: _onSlugChanged,
                          hint: 'Aplica a cliente, técnico y responsable de taller.',
                        ),
                ),
              ),
              const SizedBox(height: 24),
              _ActorCard(
                title: 'Cliente',
                subtitle: 'Registro, vehículos y solicitudes de auxilio',
                icon: Icons.person_search_rounded,
                accent: MobileAuthTheme.accentIndigo,
                onTap: () => context.go('/cliente/login'),
              ),
              const SizedBox(height: 14),
              _ActorCard(
                title: 'Técnico / mecánico',
                subtitle: 'Servicios asignados en campo',
                icon: Icons.build_circle_rounded,
                accent: AppTheme.secondaryColor,
                onTap: () => context.go('/tecnico/splash'),
              ),
              const SizedBox(height: 14),
              _ActorCard(
                title: 'Responsable de taller',
                subtitle: 'Bandeja, técnicos y operaciones',
                icon: Icons.storefront_rounded,
                accent: MobileAuthTheme.accentCyan,
                onTap: () => context.go('/taller/splash'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActorCard extends StatelessWidget {
  const _ActorCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.accent,
    required this.onTap,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final Color accent;
  final VoidCallback onTap;

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
            border: Border.all(color: MobileAuthTheme.borderColor),
          ),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                DecoratedBox(
                  decoration: BoxDecoration(
                    color: accent.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: accent.withValues(alpha: 0.35)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Icon(icon, size: 28, color: accent),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: cs.onSurface.withValues(alpha: 0.68),
                          fontSize: 13,
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
