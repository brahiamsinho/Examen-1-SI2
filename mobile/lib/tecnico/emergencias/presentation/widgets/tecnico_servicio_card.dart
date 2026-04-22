import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../domain/tecnico_servicio_models.dart';
import 'tecnico_estado_servicio_badge.dart';

/// Tarjeta táctil grande para lista de servicios asignados (CU32).
class TecnicoServicioCard extends StatelessWidget {
  const TecnicoServicioCard({
    super.key,
    required this.servicio,
    required this.onTap,
  });

  final ServicioAsignadoTecnico servicio;
  final VoidCallback onTap;

  static final _fecha = DateFormat('dd/MM/yy HH:mm');

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Semantics(
      label: 'Servicio ${servicio.solicitudId}, ${servicio.estado.etiquetaUi}, ${servicio.clienteNombreCompleto}',
      button: true,
      child: Material(
        color: scheme.surfaceContainerHighest.withValues(alpha: 0.55),
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onTap,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Text(
                        servicio.clienteNombreCompleto,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 17),
                      ),
                    ),
                    TecnicoEstadoServicioBadge(estado: servicio.estado, compact: true),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  servicio.vehiculoLinea,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: scheme.onSurface.withValues(alpha: 0.85),
                      ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(Icons.schedule_rounded, size: 18, color: scheme.onSurfaceVariant),
                    const SizedBox(width: 6),
                    Text(
                      _fecha.format(servicio.updatedAt.toLocal()),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: scheme.onSurfaceVariant,
                            fontWeight: FontWeight.w500,
                          ),
                    ),
                    if (servicio.tiempoEstimadoMin != null) ...[
                      const SizedBox(width: 12),
                      Icon(Icons.timer_outlined, size: 18, color: scheme.primary),
                      const SizedBox(width: 4),
                      Text(
                        '~${servicio.tiempoEstimadoMin} min',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: scheme.primary,
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ],
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Text(
                      'Ver detalle',
                      style: TextStyle(
                        color: scheme.primary,
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                      ),
                    ),
                    Icon(Icons.chevron_right_rounded, color: scheme.primary),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
