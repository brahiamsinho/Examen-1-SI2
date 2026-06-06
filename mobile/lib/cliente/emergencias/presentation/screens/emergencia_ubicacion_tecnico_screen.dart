import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../../core/utils/bolivia_time.dart';
import '../../application/emergencias_providers.dart';
import '../widgets/emergencia_ubicacion_osm_map.dart';
import '../widgets/seguimiento/ruta_vrt_eta_card.dart';

/// Mapa y datos de la última posición compartida por el técnico asignado (CU36 polling).
class EmergenciaUbicacionTecnicoScreen extends ConsumerStatefulWidget {
  const EmergenciaUbicacionTecnicoScreen({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  ConsumerState<EmergenciaUbicacionTecnicoScreen> createState() =>
      _EmergenciaUbicacionTecnicoScreenState();
}

class _EmergenciaUbicacionTecnicoScreenState extends ConsumerState<EmergenciaUbicacionTecnicoScreen> {
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _pollTimer = Timer.periodic(const Duration(seconds: 12), (_) {
      ref.invalidate(emergenciaUbicacionTecnicoProvider(widget.solicitudId));
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _abrirNavegacionExterna(double lat, double lng) async {
    final uri = Uri.parse('https://www.google.com/maps/search/?api=1&query=$lat,$lng');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(emergenciaUbicacionTecnicoProvider(widget.solicitudId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ubicación del técnico'),
        leading: BackButton(onPressed: () => context.pop()),
        actions: [
          IconButton(
            tooltip: 'Actualizar ahora',
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(emergenciaUbicacionTecnicoProvider(widget.solicitudId)),
          ),
        ],
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => _UbicacionError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(emergenciaUbicacionTecnicoProvider(widget.solicitudId)),
        ),
        data: (u) {
          final scheme = Theme.of(context).colorScheme;
          final ruta = u.ruta;
          final routeLabel = ruta == null
              ? null
              : ruta.esRutaPorCalles
                  ? 'Ruta por calles (OSRM) — técnico → tu ubicación'
                  : 'Ruta aproximada en línea recta — activá OSRM para calles reales';
          return ListView(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
            children: [
              Text(
                'Actualización automática cada 12 s',
                style: Theme.of(context).textTheme.labelMedium?.copyWith(color: scheme.onSurfaceVariant),
              ),
              const SizedBox(height: 8),
              if (ruta != null) ...[
                RutaVrtEtaCard(ruta: ruta),
                const SizedBox(height: 12),
              ],
              EmergenciaUbicacionOsmMap(
                latitude: u.latitud,
                longitude: u.longitud,
                routePoints: ruta?.geometria,
                routeToLatitude: u.clienteLatitud ?? ruta?.geometria.lastOrNull?.first,
                routeToLongitude: u.clienteLongitud ?? ruta?.geometria.lastOrNull?.last,
                height: 280,
                routeLabel: routeLabel,
              ),
              if (ruta != null) ...[
                const SizedBox(height: 8),
                Text(
                  'La línea azul sigue la ruta calculada hacia tu última ubicación compartida. '
                  'El ETA se recalcula en cada actualización.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: scheme.onSurfaceVariant,
                        height: 1.35,
                      ),
                ),
              ] else if (u.clienteLatitud != null) ...[
                const SizedBox(height: 8),
                Text(
                  'Sin ruta calculada: falta tu ubicación actual en la solicitud.',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
                ),
              ],
              const SizedBox(height: 16),
              Text(
                'Coordenadas',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
              ),
              const SizedBox(height: 6),
              SelectableText(
                '${u.latitud.toStringAsFixed(6)}, ${u.longitud.toStringAsFixed(6)}',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              if (u.precisionMetros != null) ...[
                const SizedBox(height: 8),
                Text(
                  'Precisión aprox.: ${u.precisionMetros!.toStringAsFixed(0)} m',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
                ),
              ],
              const SizedBox(height: 8),
              Text(
                'Actualizado: ${BoliviaTime.formatWithZone(u.actualizadoAt)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
              ),
              const SizedBox(height: 24),
              FilledButton.icon(
                icon: const Icon(Icons.navigation_rounded),
                label: const Padding(
                  padding: EdgeInsets.symmetric(vertical: 14),
                  child: Text('Abrir en mapas', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                ),
                onPressed: () => _abrirNavegacionExterna(u.latitud, u.longitud),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _UbicacionError extends StatelessWidget {
  const _UbicacionError({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.location_off_outlined, size: 52, color: scheme.onSurfaceVariant),
            const SizedBox(height: 16),
            Text(message, textAlign: TextAlign.center),
            const SizedBox(height: 16),
            FilledButton(onPressed: onRetry, child: const Text('Reintentar')),
          ],
        ),
      ),
    );
  }
}
