import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../../../core/utils/bolivia_time.dart';
import '../../../domain/ubicacion_tecnico_compartida.dart';

/// Tarjeta ETA + distancia calculada con ruta VRT (OSRM o fallback).
class RutaVrtEtaCard extends StatelessWidget {
  const RutaVrtEtaCard({super.key, required this.ruta});

  final RutaSeguimientoVrt ruta;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final minutos = ruta.duracionMinutos;
    final etaTexto = minutos > 0 ? '$minutos min' : '< 1 min';
    final distKm = ruta.distanciaKm;
    final distTexto = distKm >= 1 ? '${distKm.toStringAsFixed(1)} km' : '${ruta.distanciaMetros.round()} m';
    final fuente = ruta.esRutaPorCalles
        ? 'Ruta por calles (OSRM)'
        : 'Aproximación directa (sin motor de calles)';

    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.route_outlined, color: scheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Llegada estimada (VRT)',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              etaTexto,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 6),
            Text(
              'Hora estimada: ${BoliviaTime.formatWithZone(ruta.etaLlegadaAt, pattern: 'HH:mm')}',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 8),
            Text(
              'Distancia: $distTexto',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: scheme.onSurfaceVariant),
            ),
            const SizedBox(height: 4),
            Text(
              fuente,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant, height: 1.35),
            ),
          ],
        ),
      ),
    );
  }
}
