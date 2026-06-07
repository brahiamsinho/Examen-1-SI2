import 'package:flutter/material.dart';

import '../../../../../core/theme/mobile_auth_theme.dart';
import '../../../domain/solicitud_emergencia_models.dart';
import '../../../domain/solicitud_seguimiento_models.dart';

/// Muestra el taller elegido o confirmado en flujos del cliente.
class TallerClienteResumenCard extends StatelessWidget {
  const TallerClienteResumenCard({
    super.key,
    required this.taller,
    required this.estado,
  });

  final TallerSeguimientoRead taller;
  final EstadoSolicitudEmergencia estado;

  bool get _pendiente => estado == EstadoSolicitudEmergencia.enRevision;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final title = _pendiente ? 'Taller que elegiste' : 'Taller asignado';
    final subtitle = _pendiente
        ? 'Esperando que el taller confirme tu solicitud en su bandeja.'
        : 'Este taller está atendiendo tu emergencia.';

    return DecoratedBox(
      decoration: BoxDecoration(
        color: MobileAuthTheme.cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: _pendiente
              ? MobileAuthTheme.accentAmber.withValues(alpha: 0.45)
              : MobileAuthTheme.borderColor,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.storefront_rounded,
                  color: _pendiente ? MobileAuthTheme.accentAmber : scheme.primary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(title, style: Theme.of(context).textTheme.titleMedium),
                ),
                if (_pendiente)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: MobileAuthTheme.accentAmber.withValues(alpha: 0.18),
                      borderRadius: BorderRadius.circular(999),
                      border: Border.all(color: MobileAuthTheme.accentAmber.withValues(alpha: 0.4)),
                    ),
                    child: const Text(
                      'Pendiente',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              taller.nombreComercial,
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 17),
            ),
            const SizedBox(height: 6),
            Text(
              subtitle,
              style: TextStyle(
                color: scheme.onSurface.withValues(alpha: 0.68),
                height: 1.35,
                fontSize: 13,
              ),
            ),
            const SizedBox(height: 10),
            _row(Icons.place_outlined, '${taller.direccion}, ${taller.ciudad}'),
            _row(Icons.phone_outlined, taller.telefonoContacto),
          ],
        ),
      ),
    );
  }

  Widget _row(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 17, color: MobileAuthTheme.textMuted),
          const SizedBox(width: 8),
          Expanded(child: Text(text, style: const TextStyle(height: 1.35, fontSize: 13))),
        ],
      ),
    );
  }
}

/// Banner compacto al elegir taller (pantalla CU37).
class TallerSeleccionResumenBanner extends StatelessWidget {
  const TallerSeleccionResumenBanner({
    super.key,
    required this.nombreComercial,
    this.distanciaKm,
    this.compatibilidadPct,
  });

  final String nombreComercial;
  final double? distanciaKm;
  final int? compatibilidadPct;

  @override
  Widget build(BuildContext context) {
    final extras = <String>[
      if (compatibilidadPct != null) 'Compatibilidad $compatibilidadPct%',
      if (distanciaKm != null) '~${distanciaKm!.toStringAsFixed(1)} km',
    ];

    return DecoratedBox(
      decoration: BoxDecoration(
        color: MobileAuthTheme.accentIndigo.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: MobileAuthTheme.accentIndigo.withValues(alpha: 0.4)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Icon(Icons.check_circle_outline_rounded, color: MobileAuthTheme.accentIndigo),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Tu selección',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          color: MobileAuthTheme.textSecondary,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    nombreComercial,
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                  ),
                  if (extras.isNotEmpty)
                    Text(
                      extras.join(' · '),
                      style: TextStyle(
                        fontSize: 12,
                        color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.65),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
