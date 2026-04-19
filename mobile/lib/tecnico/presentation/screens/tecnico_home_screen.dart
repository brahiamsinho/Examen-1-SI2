import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../application/tecnico_auth_provider.dart';
import '../../domain/models/tecnico_perfil.dart';

/// Home técnico — resumen operativo ciclo 1 (sin casos reales aún).
class TecnicoHomeScreen extends ConsumerWidget {
  const TecnicoHomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final auth = ref.watch(tecnicoAuthNotifierProvider);
    final perfil = auth.perfil;
    final scheme = Theme.of(context).colorScheme;
    final primerNombre = _primerNombre(perfil?.nombres);
    final tallerLine = () {
      final tn = perfil?.tallerNombre?.trim();
      if (tn != null && tn.isNotEmpty) return 'Resumen de tu cuenta en $tn';
      return 'Resumen de tu cuenta';
    }();

    return Scaffold(
      appBar: AppBar(title: const Text('Inicio')),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
        children: [
        Text(
          'Hola, $primerNombre',
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 6),
        Text(
          tallerLine,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: scheme.onSurface.withValues(alpha: 0.72),
              ),
        ),
        const SizedBox(height: 20),
        _EstadoCard(perfil: perfil),
        const SizedBox(height: 16),
        _DisponibilidadCard(perfil: perfil),
        const SizedBox(height: 24),
        Text(
          'Accesos rápidos',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 12),
        _QuickTile(
          icon: Icons.assignment_outlined,
          title: 'Servicios asignados',
          subtitle: 'Ver pendientes y en curso',
          onTap: () => context.go('/tecnico/app/servicios'),
        ),
        const SizedBox(height: 10),
        _QuickTile(
          icon: Icons.history_rounded,
          title: 'Historial',
          subtitle: 'Servicios finalizados',
          onTap: () => context.push('/tecnico/app/historial'),
        ),
        const SizedBox(height: 10),
        _QuickTile(
          icon: Icons.person_outline,
          title: 'Perfil',
          subtitle: 'Datos y disponibilidad',
          onTap: () => context.go('/tecnico/app/perfil'),
        ),
        const SizedBox(height: 28),
        DecoratedBox(
          decoration: BoxDecoration(
            color: scheme.surfaceContainerHighest.withValues(alpha: 0.45),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: scheme.outline.withValues(alpha: 0.25)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.info_outline_rounded, color: scheme.primary, size: 22),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Aún no tenés funciones operativas habilitadas en este ciclo. '
                    'Podrás gestionar servicios desde aquí en versiones posteriores.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          height: 1.4,
                          color: scheme.onSurface.withValues(alpha: 0.85),
                        ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
      ),
    );
  }
}

String _primerNombre(String? nombres) {
  final t = nombres?.trim() ?? '';
  if (t.isEmpty) return 'Técnico';
  return t.split(RegExp(r'\s+')).first;
}

class _EstadoCard extends StatelessWidget {
  const _EstadoCard({required this.perfil});

  final TecnicoPerfil? perfil;

  @override
  Widget build(BuildContext context) {
    final estado = perfil?.estadoEtiqueta ?? '—';
    final roles = perfil?.roles.join(', ') ?? '—';
    return _InfoCard(
      title: 'Estado de cuenta',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _kv(context, 'Estado', estado),
          const SizedBox(height: 8),
          _kv(context, 'Roles', roles),
        ],
      ),
    );
  }

  Widget _kv(BuildContext context, String k, String v) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 88,
          child: Text(
            k,
            style: Theme.of(context).textTheme.labelMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.65),
                ),
          ),
        ),
        Expanded(
          child: Text(v, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500)),
        ),
      ],
    );
  }
}

class _DisponibilidadCard extends StatelessWidget {
  const _DisponibilidadCard({required this.perfil});

  final TecnicoPerfil? perfil;

  @override
  Widget build(BuildContext context) {
    final disp = perfil?.disponibilidad;
    final text = (disp != null && disp.trim().isNotEmpty) ? disp : 'Sin preferencia registrada';
    return _InfoCard(
      title: 'Disponibilidad',
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.35),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({required this.title, required this.child});

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
            Text(title, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
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
              Icon(icon, color: scheme.primary, size: 28),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
                    const SizedBox(height: 2),
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
