// CU44 — GET `/app/cliente/emergencias/{id}/seguimiento/eta`.
import 'package:flutter/foundation.dart';

import '../../../core/utils/api_datetime.dart';
import 'solicitud_emergencia_models.dart';

enum EtaDisponibilidad {
  pendiente('PENDIENTE'),
  disponible('DISPONIBLE'),
  noAplicable('NO_APLICABLE'),
  historico('HISTORICO');

  const EtaDisponibilidad(this.apiValue);
  final String apiValue;

  static EtaDisponibilidad parse(String raw) {
    return EtaDisponibilidad.values.firstWhere(
      (e) => e.apiValue == raw,
      orElse: () => EtaDisponibilidad.pendiente,
    );
  }
}

@immutable
class SolicitudEtaConsulta {
  const SolicitudEtaConsulta({
    required this.solicitudId,
    required this.estado,
    required this.disponibilidad,
    required this.etaAplicable,
    required this.mensaje,
    required this.actualizadoAt,
    this.tiempoEstimadoMin,
    this.tallerId,
    this.tecnicoId,
  });

  final int solicitudId;
  final EstadoSolicitudEmergencia estado;
  final int? tiempoEstimadoMin;
  final EtaDisponibilidad disponibilidad;
  final bool etaAplicable;
  final String mensaje;
  final DateTime actualizadoAt;
  final int? tallerId;
  final int? tecnicoId;

  bool get tieneMinutos => tiempoEstimadoMin != null && tiempoEstimadoMin! >= 0;

  /// Texto amigable: "1 h 20 min" o "45 min".
  String get duracionLegible {
    final m = tiempoEstimadoMin;
    if (m == null || m < 0) return '';
    if (m < 60) return '$m min';
    final h = m ~/ 60;
    final r = m % 60;
    if (r == 0) return '$h h';
    return '$h h $r min';
  }

  factory SolicitudEtaConsulta.fromJson(Map<String, dynamic> j) {
    return SolicitudEtaConsulta(
      solicitudId: j['solicitud_id'] as int,
      estado: EstadoSolicitudEmergencia.parse(j['estado'] as String),
      tiempoEstimadoMin: j['tiempo_estimado_min'] as int?,
      disponibilidad: EtaDisponibilidad.parse(j['disponibilidad'] as String),
      etaAplicable: j['eta_aplicable'] as bool? ?? false,
      mensaje: j['mensaje'] as String,
      actualizadoAt: parseApiDateTime(j['actualizado_at']),
      tallerId: j['taller_id'] as int?,
      tecnicoId: j['tecnico_id'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
        'solicitud_id': solicitudId,
        'estado': estado.apiValue,
        if (tiempoEstimadoMin != null) 'tiempo_estimado_min': tiempoEstimadoMin,
        'disponibilidad': disponibilidad.apiValue,
        'eta_aplicable': etaAplicable,
        'mensaje': mensaje,
        'actualizado_at': actualizadoAt.toIso8601String(),
        if (tallerId != null) 'taller_id': tallerId,
        if (tecnicoId != null) 'tecnico_id': tecnicoId,
      };
}

@immutable
class ConsultarEtaResult {
  const ConsultarEtaResult({
    required this.eta,
    required this.fromCache,
  });

  final SolicitudEtaConsulta eta;
  final bool fromCache;
}
