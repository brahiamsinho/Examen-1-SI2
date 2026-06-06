import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../application/taller_injection.dart';
import '../../domain/models/tecnico_portal_models.dart';

class TallerTecnicosListScreen extends ConsumerWidget {
  const TallerTecnicosListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerTecnicosProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Equipo técnico')),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text(e.toString().replaceFirst('Exception: ', ''))),
        data: (list) {
          if (list.isEmpty) {
            return RefreshIndicator(
              onRefresh: () async => ref.invalidate(tallerTecnicosProvider),
              child: ListView(
                children: const [
                  SizedBox(height: 120),
                  Center(child: Text('No hay técnicos registrados.')),
                  SizedBox(height: 8),
                  Center(child: Text('Alta y edición completa en portal web /taller')),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(tallerTecnicosProvider),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: list.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, i) => _TecnicoTile(t: list[i]),
            ),
          );
        },
      ),
    );
  }
}

class _TecnicoTile extends StatelessWidget {
  const _TecnicoTile({required this.t});

  final TecnicoPortal t;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final activo = t.activo;
    return DecoratedBox(
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: activo ? scheme.primary.withValues(alpha: 0.2) : scheme.outline.withValues(alpha: 0.2),
          child: Icon(Icons.engineering_outlined, color: activo ? scheme.primary : scheme.onSurfaceVariant),
        ),
        title: Text(t.nombreCompleto, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('${t.especialidadNombre ?? 'Sin especialidad'} · ${t.estado}'),
        trailing: Text(t.telefono, style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant)),
      ),
    );
  }
}
