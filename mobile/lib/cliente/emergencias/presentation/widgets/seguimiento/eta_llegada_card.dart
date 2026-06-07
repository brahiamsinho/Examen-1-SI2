import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../../../core/utils/bolivia_time.dart';
import '../../../domain/solicitud_emergencia_models.dart';
import '../../../domain/solicitud_eta_models.dart';

/// CU44 — tiempo estimado de reparación/atención con mensaje contextual.
class EtaReparacionCu44Card extends StatelessWidget {
  const EtaReparacionCu44Card({
    super.key,
    required this.eta,
    this.fromCache = false,
  });

  final SolicitudEtaConsulta eta;
  final bool fromCache;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final icon = switch (eta.disponibilidad) {
      EtaDisponibilidad.disponible => Icons.timer_outlined,
      EtaDisponibilidad.pendiente => Icons.hourglass_empty_outlined,
      EtaDisponibilidad.historico => Icons.history,
      EtaDisponibilidad.noAplicable => Icons.info_outline,
    };

    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(icon, color: scheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Tiempo estimado de reparación',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
              ],
            ),
            if (fromCache) ...[
              const SizedBox(height: 10),
              Material(
                color: scheme.tertiaryContainer.withValues(alpha: 0.45),
                borderRadius: BorderRadius.circular(8),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  child: Row(
                    children: [
                      Icon(Icons.cloud_off, size: 16, color: scheme.tertiary),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(
                          'Sin conexión — mostrando último valor guardado.',
                          style: TextStyle(fontSize: 12, color: scheme.onTertiaryContainer),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 12),
            if (eta.tieneMinutos) ...[
              Text(
                eta.duracionLegible,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
              ),
              const SizedBox(height: 8),
            ],
            Text(
              eta.mensaje,
              style: TextStyle(color: scheme.onSurfaceVariant, height: 1.45),
            ),
            const SizedBox(height: 8),
            Text(
              'Actualizado: ${BoliviaTime.formatWithZone(eta.actualizadoAt, pattern: 'dd/MM/yyyy HH:mm')}',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(color: scheme.onSurfaceVariant),
            ),
          ],
        ),
      ),
    );
  }
}

/// Compatibilidad CU18 — delega en modelo simple cuando no hay CU44.
class EtaLlegadaCard extends StatelessWidget {
  const EtaLlegadaCard({super.key, required this.minutos, this.actualizadoEn});

  final int? minutos;
  final DateTime? actualizadoEn;

  @override
  Widget build(BuildContext context) {
    final eta = SolicitudEtaConsulta(
      solicitudId: 0,
      estado: EstadoSolicitudEmergencia.enCamino,
      tiempoEstimadoMin: minutos,
      disponibilidad: minutos != null && minutos! >= 0
          ? EtaDisponibilidad.disponible
          : EtaDisponibilidad.pendiente,
      etaAplicable: true,
      mensaje: minutos != null && minutos! >= 0
          ? 'Tiempo estimado de llegada: $minutos min.'
          : 'Aún no hay ETA publicada. El taller la actualizará cuando asigne la movilización.',
      actualizadoAt: actualizadoEn ?? DateTime.now().toUtc(),
    );
    return EtaReparacionCu44Card(eta: eta);
  }
}
