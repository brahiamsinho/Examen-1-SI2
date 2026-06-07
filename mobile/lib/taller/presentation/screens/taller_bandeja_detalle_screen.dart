import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/network/solicitud_realtime_providers.dart';
import '../../application/taller_injection.dart';

class TallerBandejaDetalleScreen extends ConsumerStatefulWidget {
  const TallerBandejaDetalleScreen({super.key, required this.bandejaId});

  final int bandejaId;

  @override
  ConsumerState<TallerBandejaDetalleScreen> createState() => _TallerBandejaDetalleScreenState();
}

class _TallerBandejaDetalleScreenState extends ConsumerState<TallerBandejaDetalleScreen> {
  bool _busy = false;
  String? _error;
  int? _tecnicoSeleccionado;
  final _motivoRechazo = TextEditingController();
  final _etaMin = TextEditingController(text: '30');

  @override
  void dispose() {
    _motivoRechazo.dispose();
    _etaMin.dispose();
    super.dispose();
  }

  Future<void> _aceptar(int solicitudId) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(tallerRepositoryProvider).aceptarBandeja(widget.bandejaId);
      ref.invalidate(tallerBandejaDetalleProvider(widget.bandejaId));
      ref.invalidate(tallerBandejaProvider);
      ref.invalidate(tallerAsignacionesProvider(solicitudId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Solicitud aceptada. Podés asignar un técnico.')),
        );
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _rechazar() async {
    final motivo = _motivoRechazo.text.trim();
    if (motivo.length < 3) {
      setState(() => _error = 'Indicá un motivo de al menos 3 caracteres.');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(tallerRepositoryProvider).rechazarBandeja(widget.bandejaId, motivo);
      ref.invalidate(tallerBandejaProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Solicitud rechazada.')));
        context.pop();
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _asignar(int solicitudId) async {
    final tecnicoId = _tecnicoSeleccionado;
    if (tecnicoId == null) {
      setState(() => _error = 'Seleccioná un técnico.');
      return;
    }
    final eta = int.tryParse(_etaMin.text.trim());
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await ref.read(tallerRepositoryProvider).asignarTecnico(
            solicitudId: solicitudId,
            tecnicoId: tecnicoId,
            tiempoEstimadoMin: eta,
          );
      ref.invalidate(tallerAsignacionesProvider(solicitudId));
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Técnico asignado.')));
      }
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final detalleAsync = ref.watch(tallerBandejaDetalleProvider(widget.bandejaId));
    final tecnicosAsync = ref.watch(tallerTecnicosProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Detalle incidente')),
      body: detalleAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text(e.toString())),
        data: (item) {
          ref.listen(tallerSolicitudRealtimeEventsProvider(item.solicitudId), (prev, next) {
            next.whenData((ev) {
              if (realtimeEventAffectsTallerOperacion(ev.tipo)) {
                ref.invalidate(tallerBandejaDetalleProvider(widget.bandejaId));
                ref.invalidate(tallerAsignacionesProvider(item.solicitudId));
                ref.invalidate(tallerBandejaProvider);
              }
            });
          });

          final asignacionesAsync = ref.watch(tallerAsignacionesProvider(item.solicitudId));
          final estadoBandeja = (item.estadoBandeja ?? 'PENDIENTE').toUpperCase();
          final pendiente = estadoBandeja == 'PENDIENTE';
          final aceptada = estadoBandeja == 'ACEPTADA';

          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text(item.placa, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: 4),
              Text('${item.clienteNombre} · ${item.estadoSolicitud}'),
              if (item.marca != null || item.modelo != null)
                Text('${item.marca ?? ''} ${item.modelo ?? ''}'.trim()),
              const SizedBox(height: 12),
              if (item.descripcionTexto != null)
                Text(item.descripcionTexto!, style: const TextStyle(height: 1.4)),
              const SizedBox(height: 16),
              if (_error != null) Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
              if (pendiente) ...[
                ShadButton(
                  width: double.infinity,
                  onPressed: _busy ? null : () => _aceptar(item.solicitudId),
                  child: const Text('Aceptar solicitud'),
                ),
                const SizedBox(height: 12),
                Text('Motivo de rechazo', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 8),
                ShadInput(
                  controller: _motivoRechazo,
                  placeholder: const Text('Ej.: fuera de cobertura hoy'),
                  maxLines: 2,
                ),
                const SizedBox(height: 10),
                ShadButton.outline(
                  width: double.infinity,
                  onPressed: _busy ? null : _rechazar,
                  child: const Text('Rechazar'),
                ),
              ],
              if (aceptada || !pendiente) ...[
                const SizedBox(height: 8),
                Text('Asignar técnico', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                tecnicosAsync.when(
                  loading: () => const CircularProgressIndicator(),
                  error: (e, _) => Text(e.toString()),
                  data: (tecnicos) {
                    final activos = tecnicos.where((t) => t.activo).toList();
                    if (activos.isEmpty) {
                      return const Text('No hay técnicos activos. Creálos en el portal web.');
                    }
                    return DropdownButtonFormField<int>(
                      value: _tecnicoSeleccionado,
                      decoration: const InputDecoration(labelText: 'Técnico'),
                      items: activos
                          .map(
                            (t) => DropdownMenuItem(
                              value: t.id,
                              child: Text(t.nombreCompleto),
                            ),
                          )
                          .toList(),
                      onChanged: _busy ? null : (v) => setState(() => _tecnicoSeleccionado = v),
                    );
                  },
                ),
                const SizedBox(height: 10),
                ShadInput(
                  controller: _etaMin,
                  keyboardType: TextInputType.number,
                  placeholder: const Text('ETA minutos'),
                ),
                const SizedBox(height: 12),
                ShadButton(
                  width: double.infinity,
                  onPressed: _busy ? null : () => _asignar(item.solicitudId),
                  child: const Text('Asignar técnico'),
                ),
                const SizedBox(height: 20),
                Text('Historial de asignaciones', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 8),
                asignacionesAsync.when(
                  loading: () => const SizedBox.shrink(),
                  error: (_, __) => const SizedBox.shrink(),
                  data: (rows) {
                    if (rows.isEmpty) return const Text('Sin asignaciones aún.');
                    return Column(
                      children: rows
                          .map(
                            (a) => ListTile(
                              dense: true,
                              title: Text('Técnico #${a.tecnicoId}'),
                              subtitle: Text('${a.estado}${a.observacion != null ? ' · ${a.observacion}' : ''}'),
                            ),
                          )
                          .toList(),
                    );
                  },
                ),
              ],
            ],
          );
        },
      ),
    );
  }
}
