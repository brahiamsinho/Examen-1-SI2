import 'package:flutter/material.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../domain/solicitud_ai_payload.dart';

/// Tarjeta informativa del análisis asistido (IA) guardado en la solicitud.
class SolicitudAiResumenCard extends StatelessWidget {
  const SolicitudAiResumenCard({super.key, required this.payload});

  final SolicitudAiPayloadV1? payload;

  @override
  Widget build(BuildContext context) {
    final raw = payload;
    if (raw == null || !raw.tieneContenidoUtil) {
      return ShadCard(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.psychology_outlined, color: Theme.of(context).colorScheme.onSurfaceVariant),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'El análisis asistido no está disponible todavía (sin datos de IA o el servicio estaba apagado).',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    }

    final p = raw;
    final scheme = Theme.of(context).colorScheme;
    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(Icons.auto_awesome, size: 22, color: scheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Análisis asistido (IA)',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                ),
              ],
            ),
            if (p.clasificacion != null) ...[
              const SizedBox(height: 12),
              _kv(
                context,
                'Categoría',
                '${etiquetaCategoriaIa(p.clasificacion!.categoria)} '
                '(${(p.clasificacion!.confianza * 100).toStringAsFixed(0)}%)',
              ),
            ],
            if (p.prioridad != null) ...[
              const SizedBox(height: 8),
              _kv(
                context,
                'Prioridad sugerida',
                etiquetaPrioridadIa(p.prioridad!.nivelPrioridad),
              ),
              if (p.prioridad!.motivo.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  p.prioridad!.motivo.join(' · '),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: scheme.onSurfaceVariant,
                        height: 1.35,
                      ),
                ),
              ],
            ],
            if (p.resumenEstructurado != null) ...[
              const SizedBox(height: 12),
              Text('Resumen', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 4),
              Text(
                p.resumenEstructurado!.resumen,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.4),
              ),
            ],
            if (p.resumenEstructurado?.ficha != null) ...[
              const SizedBox(height: 10),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  _chip(context, 'Ubicación', p.resumenEstructurado!.ficha!.ubicacionValida),
                  _chip(context, 'Audio', p.resumenEstructurado!.ficha!.evidenciaAudio),
                  _chip(context, 'Imagen', p.resumenEstructurado!.ficha!.evidenciaImagen),
                ],
              ),
            ],
            if (p.hallazgosVision.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text('Hallazgos (visión)', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 4),
              ...p.hallazgosVision.map(
                (h) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text('· $h', style: TextStyle(color: scheme.onSurfaceVariant, height: 1.3)),
                ),
              ),
            ],
            if (p.transcripcionAudio != null && p.transcripcionAudio!.trim().isNotEmpty) ...[
              const SizedBox(height: 10),
              Text('Transcripción de audio', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 4),
              Text(
                p.transcripcionAudio!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: scheme.onSurfaceVariant,
                      height: 1.35,
                    ),
              ),
            ],
            const SizedBox(height: 8),
            Text(
              'Sugerencia automática: puede requerir validación humana en taller.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: scheme.onSurfaceVariant,
                    fontStyle: FontStyle.italic,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  static Widget _kv(BuildContext context, String k, String v) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 150,
          child: Text(
            k,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                ),
          ),
        ),
        Expanded(child: Text(v, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600))),
      ],
    );
  }

  static Widget _chip(BuildContext context, String label, bool value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        '$label: ${value ? "sí" : "no"}',
        style: Theme.of(context).textTheme.labelSmall,
      ),
    );
  }
}
