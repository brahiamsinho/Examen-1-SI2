import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import '../../domain/models/bandeja_models.dart';

class TallerBandejaListScreen extends ConsumerWidget {
  const TallerBandejaListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerBandejaProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Bandeja de emergencias')),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Text(e.toString().replaceFirst('Exception: ', '')),
          ),
        ),
        data: (list) {
          if (list.isEmpty) {
            return RefreshIndicator(
              onRefresh: () async => ref.invalidate(tallerBandejaProvider),
              child: ListView(
                children: const [
                  SizedBox(height: 120),
                  Center(child: Text('No hay solicitudes pendientes en bandeja.')),
                ],
              ),
            );
          }
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(tallerBandejaProvider),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: list.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, i) => _BandejaTile(
                item: list[i],
                fecha: BoliviaTime.format(list[i].createdAt, pattern: 'dd/MM HH:mm'),
                onTap: () => context.push('/taller/app/bandeja/${list[i].bandejaId}'),
              ),
            ),
          );
        },
      ),
    );
  }
}

class _BandejaTile extends StatelessWidget {
  const _BandejaTile({required this.item, required this.fecha, required this.onTap});

  final BandejaIncidente item;
  final String fecha;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final prioridad = item.nivelPrioridad?.toUpperCase();
    return Material(
      color: scheme.surfaceContainerHighest.withValues(alpha: 0.5),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      item.placa,
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                    ),
                  ),
                  if (prioridad != null && prioridad.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: scheme.primary.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(prioridad, style: TextStyle(fontSize: 11, color: scheme.primary)),
                    ),
                ],
              ),
              const SizedBox(height: 4),
              Text(item.clienteNombre, style: TextStyle(color: scheme.onSurfaceVariant)),
              if (item.descripcionTexto != null && item.descripcionTexto!.trim().isNotEmpty) ...[
                const SizedBox(height: 6),
                Text(
                  item.descripcionTexto!.trim(),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
              const SizedBox(height: 8),
              Text(fecha, style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant)),
            ],
          ),
        ),
      ),
    );
  }
}
