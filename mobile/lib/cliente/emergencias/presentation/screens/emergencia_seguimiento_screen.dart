import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../presentation/widgets/cliente_panel_ui.dart';
import '../../../../core/utils/bolivia_time.dart';
import '../../../pagos/presentation/widgets/solicitud_pago_cta_block.dart';
import '../../../../core/network/solicitud_realtime_providers.dart';
import '../../application/consultar_eta_providers.dart';
import '../../application/emergencias_providers.dart';
import '../../domain/solicitud_emergencia_models.dart';
import '../widgets/seguimiento/estado_solicitud_badge.dart';
import '../widgets/ai/solicitud_ai_resumen_card.dart';
import '../widgets/seguimiento/eta_llegada_card.dart';
import '../widgets/seguimiento/seguimiento_timeline.dart';
import '../widgets/seguimiento/taller_cliente_resumen_card.dart';
import '../widgets/seguimiento/taller_asignado_card.dart';
import '../widgets/seguimiento/tecnico_asignado_card.dart';
import '../widgets/seguimiento/elegir_taller_prompt_card.dart';

/// Seguimiento de solicitud — CU44 ETA + estado, taller, técnico, historial (WS + pull).
class EmergenciaSeguimientoScreen extends ConsumerStatefulWidget {
  const EmergenciaSeguimientoScreen({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  ConsumerState<EmergenciaSeguimientoScreen> createState() => _EmergenciaSeguimientoScreenState();
}

class _EmergenciaSeguimientoScreenState extends ConsumerState<EmergenciaSeguimientoScreen> {
  bool _cancelando = false;

  Future<void> _refresh() async {
    final solicitudId = widget.solicitudId;
    ref.invalidate(emergenciaSeguimientoProvider(solicitudId));
    ref.invalidate(consultarEtaProvider(solicitudId));
    await Future.wait([
      ref.read(emergenciaSeguimientoProvider(solicitudId).future),
      ref.read(consultarEtaProvider(solicitudId).future),
    ]);
  }

  Future<void> _confirmarCancelacion() async {
    final motivoCtrl = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cancelar solicitud'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              '¿Seguro que querés cancelar esta emergencia? El taller y el técnico serán notificados.',
            ),
            const SizedBox(height: 12),
            TextField(
              controller: motivoCtrl,
              maxLength: 500,
              decoration: const InputDecoration(
                labelText: 'Motivo (opcional)',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Volver')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: FilledButton.styleFrom(backgroundColor: Theme.of(ctx).colorScheme.error),
            child: const Text('Cancelar solicitud'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;

    setState(() => _cancelando = true);
    try {
      await ref.read(emergenciasRepositoryProvider).cancelar(
            widget.solicitudId,
            motivo: motivoCtrl.text.trim().isEmpty ? null : motivoCtrl.text.trim(),
          );
      ref.invalidate(emergenciaSeguimientoProvider(widget.solicitudId));
      ref.invalidate(consultarEtaProvider(widget.solicitudId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Solicitud cancelada.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      motivoCtrl.dispose();
      if (mounted) setState(() => _cancelando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final solicitudId = widget.solicitudId;

    ref.listen(solicitudRealtimeEventsProvider(solicitudId), (prev, next) {
      next.whenData((ev) {
        if (realtimeEventAffectsSeguimiento(ev.tipo)) {
          ref.invalidate(emergenciaSeguimientoProvider(solicitudId));
        }
      });
    });

    final async = ref.watch(emergenciaSeguimientoProvider(solicitudId));
    final wsLive = ref.watch(solicitudRealtimeEventsProvider(solicitudId)).hasValue;
    final etaAsync = ref.watch(consultarEtaProvider(solicitudId));

    return ClienteSubpageScaffold(
      title: 'Seguimiento',
      onBack: () => context.canPop() ? context.pop() : context.go('/cliente/app/emergencias/solicitudes/$solicitudId'),
      actions: wsLive
          ? [
              Padding(
                padding: const EdgeInsets.only(right: 12),
                child: Center(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.circle, size: 8, color: Theme.of(context).colorScheme.primary),
                      const SizedBox(width: 6),
                      Text(
                        'En vivo',
                        style: Theme.of(context).textTheme.labelSmall?.copyWith(
                              color: Theme.of(context).colorScheme.primary,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ],
                  ),
                ),
              ),
            ]
          : null,
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => _ErrorBody(
          message: e.toString(),
          onRetry: () => _refresh(),
        ),
        data: (s) => RefreshIndicator(
          onRefresh: () => _refresh(),
          child: ListView(
            padding: ClientePanelUi.pagePadding,
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
              Text('Tiempo estimado', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              etaAsync.when(
                loading: () => const ShadCard(
                  child: Padding(
                    padding: EdgeInsets.all(24),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                ),
                error: (e, _) => ShadCard(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'No se pudo consultar el ETA.',
                          style: TextStyle(color: Theme.of(context).colorScheme.error),
                        ),
                        const SizedBox(height: 8),
                        Text(e.toString(), style: Theme.of(context).textTheme.bodySmall),
                        const SizedBox(height: 12),
                        ShadButton.outline(
                          onPressed: () => ref.invalidate(consultarEtaProvider(solicitudId)),
                          child: const Text('Reintentar ETA'),
                        ),
                      ],
                    ),
                  ),
                ),
                data: (r) => EtaReparacionCu44Card(eta: r.eta, fromCache: r.fromCache),
              ),
              const SizedBox(height: 20),
              Text('Análisis asistido (IA)', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              SolicitudAiResumenCard(
                payload: s.aiPayload,
                tieneUbicacionServidor: s.tieneUbicacionCliente,
                tieneFotoServidor: s.tieneEvidenciaFoto,
                tieneAudioServidor: s.tieneEvidenciaAudio,
              ),
              const SizedBox(height: 24),
              Text('Taller', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              if (s.taller == null)
                s.estado.puedeElegirTaller
                    ? ElegirTallerPromptCard(solicitudId: solicitudId)
                    : const _InfoPlaceholder(
                        icon: Icons.store_outlined,
                        text: 'Sin taller asignado para esta solicitud.',
                      )
              else if (s.estado == EstadoSolicitudEmergencia.enRevision)
                TallerClienteResumenCard(taller: s.taller!, estado: s.estado)
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
                const SizedBox(height: 10),
                ShadButton.outline(
                  onPressed: () =>
                      context.push('/cliente/app/emergencias/solicitudes/$solicitudId/ubicacion-tecnico'),
                  leading: const Icon(Icons.engineering_outlined, size: 20),
                  child: const Text('Ver ubicación del técnico'),
                ),
              ],
              if (s.presupuestoBob != null) ...[
                const SizedBox(height: 24),
                Text('Presupuesto en sitio', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 10),
                ShadCard(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Bs. ${s.presupuestoBob!.toStringAsFixed(2)}',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w800,
                                color: Theme.of(context).colorScheme.primary,
                              ),
                        ),
                        if (s.presupuestoRegistradoAt != null) ...[
                          const SizedBox(height: 8),
                          Text(
                            'Registrado: ${BoliviaTime.formatWithZone(s.presupuestoRegistradoAt!, pattern: 'dd/MM/yyyy HH:mm')}',
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                                ),
                          ),
                        ],
                        const SizedBox(height: 8),
                        Text(
                          'Monto indicado por el técnico al iniciar la atención. El pago formal sigue en la sección de abajo.',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 24),
              Text('Historial de estado', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              ShadCard(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: SeguimientoTimeline(items: s.historialEstados),
                ),
              ),
              const SizedBox(height: 24),
              Text('Pago del servicio', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 10),
              SolicitudPagoCtaBlock(solicitudId: solicitudId, estado: s.estado),
              if (s.estado.puedeCancelar) ...[
                const SizedBox(height: 16),
                ShadButton.outline(
                  onPressed: _cancelando ? null : _confirmarCancelacion,
                  leading: _cancelando
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Icon(Icons.cancel_outlined, size: 20, color: Theme.of(context).colorScheme.error),
                  child: Text(
                    'Cancelar solicitud',
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                  ),
                ),
              ],
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
    return ClienteEmptyState(
      icon: Icons.error_outline,
      title: 'Error al cargar',
      message: message,
      actionLabel: 'Reintentar',
      onAction: onRetry,
    );
  }
}
