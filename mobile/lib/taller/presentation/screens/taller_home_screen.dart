import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../application/taller_auth_provider.dart';
import '../../application/taller_injection.dart';

class TallerHomeScreen extends ConsumerWidget {
  const TallerHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final perfil = ref.watch(tallerAuthNotifierProvider).perfil;
    final dashAsync = ref.watch(tallerDashboardProvider);
    final bandejaAsync = ref.watch(tallerBandejaProvider);
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Panel taller'),
        actions: [
          IconButton(
            tooltip: 'Más opciones',
            onPressed: () => context.push('/taller/app/mas'),
            icon: const Icon(Icons.more_horiz_rounded),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(tallerDashboardProvider);
          ref.invalidate(tallerBandejaProvider);
          await ref.read(tallerDashboardProvider.future);
        },
        child: ListView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          children: [
            Text(
              'Hola, ${perfil?.nombres.split(' ').first ?? 'Responsable'}',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 6),
            Text(
              perfil?.tallerNombre ?? 'Tu taller',
              style: TextStyle(color: scheme.onSurface.withValues(alpha: 0.72)),
            ),
            const SizedBox(height: 20),
            dashAsync.when(
              loading: () => const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator())),
              error: (e, _) => _Card(
                title: 'Resumen',
                child: Text(e.toString().replaceFirst('Exception: ', ''), style: TextStyle(color: scheme.error)),
              ),
              data: (d) => _Card(
                title: 'Resumen operativo',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _kv('Estado taller', d.tallerEstado),
                    _kv('Técnicos activos', '${d.tecnicosActivos} / ${d.tecnicosRegistrados}'),
                    _kv('Disponibilidad', d.disponibilidadGeneral),
                    _kv('Clientes', '${d.clientesRegistrados}'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            bandejaAsync.when(
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
              data: (list) => _Card(
                title: 'Bandeja pendiente',
                child: Text(
                  '${list.length} solicitudes esperando respuesta',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('Accesos rápidos', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            _QuickTile(
              icon: Icons.inbox_rounded,
              title: 'Bandeja de emergencias',
              subtitle: 'Aceptar o rechazar solicitudes',
              onTap: () => context.go('/taller/app/bandeja'),
            ),
            const SizedBox(height: 10),
            _QuickTile(
              icon: Icons.groups_rounded,
              title: 'Equipo técnico',
              subtitle: 'Ver técnicos del taller',
              onTap: () => context.go('/taller/app/tecnicos'),
            ),
            const SizedBox(height: 10),
            _QuickTile(
              icon: Icons.settings_outlined,
              title: 'Más módulos',
              subtitle: 'Comisiones, suscripción, etc.',
              onTap: () => context.push('/taller/app/mas'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _kv(String k, String v) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(width: 130, child: Text(k, style: const TextStyle(fontSize: 13))),
          Expanded(child: Text(v, style: const TextStyle(fontWeight: FontWeight.w600))),
        ],
      ),
    );
  }
}

class _Card extends StatelessWidget {
  const _Card({required this.title, required this.child});
  final String title;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: scheme.outline.withValues(alpha: 0.2)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
            const SizedBox(height: 10),
            child,
          ],
        ),
      ),
    );
  }
}

class _QuickTile extends StatelessWidget {
  const _QuickTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: scheme.surfaceContainerHighest.withValues(alpha: 0.45),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          child: Row(
            children: [
              Icon(icon, color: scheme.primary),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                    Text(subtitle, style: TextStyle(color: scheme.onSurfaceVariant, fontSize: 13)),
                  ],
                ),
              ),
              Icon(Icons.chevron_right_rounded, color: scheme.onSurfaceVariant),
            ],
          ),
        ),
      ),
    );
  }
}
