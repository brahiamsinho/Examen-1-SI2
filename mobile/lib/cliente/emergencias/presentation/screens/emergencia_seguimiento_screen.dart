import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../pagos/presentation/widgets/solicitud_pago_cta_block.dart';
import '../../application/emergencias_providers.dart';
import '../widgets/seguimiento/estado_solicitud_badge.dart';
import '../widgets/seguimiento/eta_llegada_card.dart';
import '../widgets/seguimiento/seguimiento_timeline.dart';
import '../widgets/seguimiento/taller_asignado_card.dart';
import '../widgets/seguimiento/tecnico_asignado_card.dart';

/// CU16, CU17 y CU18 — pantalla única de seguimiento (estado, taller, técnico, ETA, historial).
class EmergenciaSeguimientoScreen extends ConsumerWidget {
  const EmergenciaSeguimientoScreen({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(emergenciaSeguimientoProvider(solicitudId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Seguimiento'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.canPop() ? context.pop() : context.go('/cliente/app/emergencias/solicitudes/$solicitudId'),
        ),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => _ErrorBody(
          message: e.toString(),
          onRetry: () => ref.invalidate(emergenciaSeguimientoProvider(solicitudId)),
        ),
        data: (s) => RefreshIndicator(
          onRefresh: () => ref.refresh(emergenciaSeguimientoProvider(solicitudId).future),
          child: ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text('Solicitud #${s.solicitudId}', style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 12),
              Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Text('Estado actual', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(width: 10),
                  EstadoSolicitudBadge(estado: s.estado),
                ],
              ),
              const SizedBox(height: 20),
              Text('Tiempo estimado (CU18)', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              EtaLlegadaCard(minutos: s.tiempoEstimadoMin, actualizadoEn: s.updatedAt),
              const SizedBox(height: 24),
              Text('Taller (CU17)', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              if (s.taller == null)
                const _InfoPlaceholder(
                  icon: Icons.store_outlined,
                  text: 'Todavía no hay taller asignado a esta solicitud.',
                )
              else
                TallerAsignadoCard(taller: s.taller!),
              const SizedBox(height: 24),
              Text('Técnico', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              if (s.tecnico == null)
                const _InfoPlaceholder(
                  icon: Icons.person_outline,
                  text: 'Sin técnico asignado. Se mostrará cuando el taller designe movilización.',
                )
              else
                TecnicoAsignadoCard(tecnico: s.tecnico!),
              if (s.tecnico != null) ...[
                const SizedBox(height: 16),
                ShadButton(
                  onPressed: () => context.push('/cliente/app/emergencias/solicitudes/$solicitudId/chat'),
                  leading: const Icon(Icons.chat_bubble_outline_rounded, size: 20),
                  child: const Text('Abrir chat con el técnico'),
                ),
              ],
              const SizedBox(height: 24),
              Text('Historial de estado (CU16)', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              ShadCard(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: SeguimientoTimeline(items: s.historialEstados),
                ),
              ),
              const SizedBox(height: 24),
              Text('Pago del servicio (CU20)', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              SolicitudPagoCtaBlock(solicitudId: solicitudId, estado: s.estado),
              const SizedBox(height: 24),
              ShadButton.outline(
                onPressed: () => context.push('/cliente/app/emergencias/solicitudes/$solicitudId'),
                child: const Text('Ver detalle de la solicitud'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoPlaceholder extends StatelessWidget {
  const _InfoPlaceholder({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: scheme.onSurfaceVariant),
            const SizedBox(width: 12),
            Expanded(child: Text(text, style: TextStyle(color: scheme.onSurfaceVariant, height: 1.4))),
          ],
        ),
      ),
    );
  }
}

class _ErrorBody extends StatelessWidget {
  const _ErrorBody({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(message, textAlign: TextAlign.center, style: TextStyle(color: Theme.of(context).colorScheme.error)),
            const SizedBox(height: 16),
            ShadButton.outline(onPressed: onRetry, child: const Text('Reintentar')),
          ],
        ),
      ),
    );
  }
}
