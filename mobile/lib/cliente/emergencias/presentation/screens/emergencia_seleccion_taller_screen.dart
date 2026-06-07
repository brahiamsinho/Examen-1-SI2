import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../presentation/widgets/cliente_panel_ui.dart';
import '../../application/emergencias_providers.dart';
import '../../domain/taller_candidato_models.dart';
import '../widgets/seguimiento/taller_cliente_resumen_card.dart';

/// CU37 — el cliente elige el taller que atenderá la emergencia.
class EmergenciaSeleccionTallerScreen extends ConsumerStatefulWidget {
  const EmergenciaSeleccionTallerScreen({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  ConsumerState<EmergenciaSeleccionTallerScreen> createState() =>
      _EmergenciaSeleccionTallerScreenState();
}

class _EmergenciaSeleccionTallerScreenState extends ConsumerState<EmergenciaSeleccionTallerScreen> {
  int? _selectedId;
  bool _submitting = false;

  Future<void> _confirmar() async {
    final asyncVal = ref.read(talleresCandidatosProvider(widget.solicitudId));
    final data = asyncVal.asData?.value;
    final tallerId = _selectedId ??
        data?.mejorTallerId ??
        (data != null && data.candidatos.isNotEmpty ? data.candidatos.first.tallerId : null);
    if (tallerId == null || _submitting) return;
    setState(() => _submitting = true);
    try {
      await ref.read(emergenciasRepositoryProvider).seleccionarTaller(widget.solicitudId, tallerId);
      if (!mounted) return;
      ref.invalidate(emergenciaSeguimientoProvider(widget.solicitudId));
      ref.invalidate(emergenciaDetailProvider(widget.solicitudId));
      context.go('/cliente/app/emergencias/solicitudes/${widget.solicitudId}/seguimiento');
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
      );
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(talleresCandidatosProvider(widget.solicitudId));
    final scheme = Theme.of(context).colorScheme;

    return ClienteSubpageScaffold(
      title: 'Elegir taller',
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => _ErrorBody(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(talleresCandidatosProvider(widget.solicitudId)),
        ),
        data: (data) {
          if (data.candidatos.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  'No hay talleres disponibles en tu organización.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: scheme.onSurfaceVariant),
                ),
              ),
            );
          }

          final mejor = data.mejorTallerId;
          final abiertos = data.candidatos.where((c) => c.abiertoAhora).toList();
          final effectiveSelected = _selectedId ??
              mejor ??
              (abiertos.isNotEmpty ? abiertos.first.tallerId : data.candidatos.first.tallerId);
          final selected = data.candidatos.firstWhere((c) => c.tallerId == effectiveSelected);
          final compatPct = (selected.score * 100).clamp(0, 100).round();
          final puedeConfirmar = selected.abiertoAhora && !_submitting;

          return Column(
            children: [
              Expanded(
                child: ListView(
                  padding: ClientePanelUi.pagePadding.copyWith(bottom: 12),
                  children: [
                    Text(
                      'Talleres recomendados',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Ordenados por proximidad, carga de trabajo y especialidad según tu reporte.',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: scheme.onSurfaceVariant,
                            height: 1.35,
                          ),
                    ),
                    const SizedBox(height: 16),
                    for (final c in data.candidatos)
                      _CandidatoTile(
                        candidato: c,
                        recomendado: c.tallerId == mejor && c.abiertoAhora,
                        selected: c.tallerId == effectiveSelected,
                        onTap: c.abiertoAhora ? () => setState(() => _selectedId = c.tallerId) : null,
                      ),
                  ],
                ),
              ),
              SafeArea(
                minimum: const EdgeInsets.fromLTRB(20, 8, 20, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    TallerSeleccionResumenBanner(
                      nombreComercial: selected.nombreComercial,
                      distanciaKm: selected.distanciaKm,
                      compatibilidadPct: compatPct,
                    ),
                    const SizedBox(height: 12),
                    ShadButton(
                      onPressed: puedeConfirmar ? _confirmar : null,
                      child: Text(
                        _submitting
                            ? 'Enviando…'
                            : selected.abiertoAhora
                                ? 'Confirmar taller'
                                : 'Taller cerrado (fuera de horario)',
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _CandidatoTile extends StatelessWidget {
  const _CandidatoTile({
    required this.candidato,
    required this.recomendado,
    required this.selected,
    required this.onTap,
  });

  final TallerCandidato candidato;
  final bool recomendado;
  final bool selected;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final pct = (candidato.score * 100).clamp(0, 100).toStringAsFixed(0);

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Material(
        color: selected ? scheme.primaryContainer.withValues(alpha: 0.35) : scheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(
                  selected ? Icons.radio_button_checked : Icons.radio_button_off,
                  color: selected ? scheme.primary : scheme.outline,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              candidato.nombreComercial,
                              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.w700,
                                  ),
                            ),
                          ),
                          if (recomendado)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: scheme.primary,
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                'Recomendado',
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                      color: scheme.onPrimary,
                                    ),
                              ),
                            ),
                          if (!candidato.abiertoAhora)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: scheme.errorContainer,
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                'Cerrado',
                                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                      color: scheme.onErrorContainer,
                                    ),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text('Compatibilidad $pct%'),
                      if (candidato.distanciaKm != null)
                        Text('~${candidato.distanciaKm!.toStringAsFixed(1)} km'),
                      if (candidato.cargaBandeja != null)
                        Text('Solicitudes pendientes en bandeja: ${candidato.cargaBandeja}'),
                    ],
                  ),
                ),
              ],
            ),
          ),
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
