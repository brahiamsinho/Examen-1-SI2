// Modelo v1 alineado a `post_create` → `solicitud.ai_payload` (JSON).
import 'package:flutter/foundation.dart';

/// Payload opcional de IA devuelto por GET detalle / seguimiento.
@immutable
class SolicitudAiPayloadV1 {
  const SolicitudAiPayloadV1({
    required this.version,
    this.clasificacion,
    this.prioridad,
    this.resumenEstructurado,
    this.transcripcionAudio,
    this.hallazgosVision = const [],
    this.sugerenciaAsignacion,
  });

  final int version;
  final ClasificacionIa? clasificacion;
  final PrioridadIa? prioridad;
  final ResumenEstructuradoIa? resumenEstructurado;
  final String? transcripcionAudio;
  final List<String> hallazgosVision;
  final Map<String, dynamic>? sugerenciaAsignacion;

  static SolicitudAiPayloadV1? tryParse(Object? raw) {
    if (raw == null) return null;
    if (raw is! Map) return null;
    final m = Map<String, dynamic>.from(raw);
    final v = m['version'];
    final version = v is int ? v : (v is num ? v.toInt() : 1);
    return SolicitudAiPayloadV1(
      version: version,
      clasificacion: ClasificacionIa.tryParse(m['clasificacion']),
      prioridad: PrioridadIa.tryParse(m['prioridad']),
      resumenEstructurado: ResumenEstructuradoIa.tryParse(m['resumen_estructurado']),
      transcripcionAudio: m['transcripcion_audio'] is String ? m['transcripcion_audio'] as String? : null,
      hallazgosVision: _stringList(m['hallazgos_vision']),
      sugerenciaAsignacion: m['sugerencia_asignacion'] is Map
          ? Map<String, dynamic>.from(m['sugerencia_asignacion'] as Map)
          : null,
    );
  }

  bool get tieneContenidoUtil =>
      resumenEstructurado != null ||
      clasificacion != null ||
      prioridad != null ||
      (transcripcionAudio != null && transcripcionAudio!.trim().isNotEmpty) ||
      hallazgosVision.isNotEmpty ||
      sugerenciaAsignacion != null;
}

List<String> _stringList(Object? o) {
  if (o is! List) return const [];
  return [for (final e in o) if (e != null) e.toString()];

}

@immutable
class ClasificacionIa {
  const ClasificacionIa({required this.categoria, required this.confianza, this.fuentes = const []});

  final String categoria;
  final double confianza;
  final List<String> fuentes;

  static ClasificacionIa? tryParse(Object? o) {
    if (o is! Map) return null;
    final m = o as Map<String, dynamic>;
    final cat = m['categoria'];
    if (cat is! String) return null;
    final conf = m['confianza'];
    final c = conf is num ? conf.toDouble() : 0.0;
    return ClasificacionIa(
      categoria: cat,
      confianza: c.clamp(0.0, 1.0),
      fuentes: _stringList(m['fuentes']),
    );
  }
}

@immutable
class PrioridadIa {
  const PrioridadIa({required this.nivelPrioridad, this.motivo = const []});

  final String nivelPrioridad;
  final List<String> motivo;

  static PrioridadIa? tryParse(Object? o) {
    if (o is! Map) return null;
    final m = o as Map<String, dynamic>;
    final n = m['nivel_prioridad'];
    if (n is! String) return null;
    return PrioridadIa(nivelPrioridad: n, motivo: _stringList(m['motivo']));
  }
}

@immutable
class FichaIncidenteIa {
  const FichaIncidenteIa({
    required this.tipoProblema,
    required this.ubicacionValida,
    required this.evidenciaAudio,
    required this.evidenciaImagen,
    required this.incertidumbre,
  });

  final String tipoProblema;
  final bool ubicacionValida;
  final bool evidenciaAudio;
  final bool evidenciaImagen;
  final String incertidumbre;

  static FichaIncidenteIa? tryParse(Object? o) {
    if (o is! Map) return null;
    final m = o as Map<String, dynamic>;
    final t = m['tipo_problema'];
    if (t is! String) return null;
    return FichaIncidenteIa(
      tipoProblema: t,
      ubicacionValida: m['ubicacion_valida'] as bool? ?? false,
      evidenciaAudio: m['evidencia_audio'] as bool? ?? false,
      evidenciaImagen: m['evidencia_imagen'] as bool? ?? false,
      incertidumbre: m['incertidumbre'] as String? ?? 'MEDIA',
    );
  }
}

@immutable
class ResumenEstructuradoIa {
  const ResumenEstructuradoIa({required this.resumen, this.ficha});

  final String resumen;
  final FichaIncidenteIa? ficha;

  static ResumenEstructuradoIa? tryParse(Object? o) {
    if (o is! Map) return null;
    final m = o as Map<String, dynamic>;
    final r = m['resumen'];
    if (r is! String) return null;
    return ResumenEstructuradoIa(
      resumen: r,
      ficha: FichaIncidenteIa.tryParse(m['ficha']),
    );
  }
}

/// Etiquetas cortas en español para enums del backend.
String etiquetaCategoriaIa(String categoria) {
  return switch (categoria.toUpperCase()) {
    'BATERIA' => 'Batería',
    'LLANTA' => 'Llanta / pinchazo',
    'CHOQUE' => 'Choque / colisión',
    'MOTOR' => 'Motor',
    'OTROS' => 'Otros',
    _ => categoria,
  };
}

String etiquetaPrioridadIa(String nivel) {
  return switch (nivel.toUpperCase()) {
    'ALTA' => 'Alta',
    'MEDIA' => 'Media',
    'BAJA' => 'Baja',
    'REVISION_MANUAL' => 'Revisión manual',
    _ => nivel,
  };
}
