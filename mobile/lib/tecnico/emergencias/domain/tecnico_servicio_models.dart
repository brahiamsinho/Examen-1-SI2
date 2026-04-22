// Modelos — API `/portal/tecnico/emergencias` (CU32–CU34).
import 'package:flutter/foundation.dart';

import '../../../cliente/emergencias/domain/solicitud_emergencia_models.dart';

double? _asDoubleNullable(Object? v) {
  if (v == null) return null;
  if (v is num) return v.toDouble();
  if (v is String) return double.parse(v);
  throw FormatException('No es número: $v');
}

double _asDouble(Object? v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.parse(v);
  throw FormatException('No es número: $v');
}

DateTime _asDateTime(Object? v) {
  if (v is String) return DateTime.parse(v);
  throw FormatException('No es fecha: $v');
}

/// Respuesta de `GET .../servicios-asignados` y `PATCH .../estado`.
@immutable
final class ServicioAsignadoTecnico {
  const ServicioAsignadoTecnico({
    required this.solicitudId,
    required this.tecnicoId,
    this.tallerId,
    required this.estado,
    this.tiempoEstimadoMin,
    required this.createdAt,
    required this.updatedAt,
    required this.clienteId,
    required this.nombres,
    required this.apellidos,
    required this.telefono,
    required this.placa,
    this.marca,
    this.modelo,
    this.tipoVehiculo,
    this.latitud,
    this.longitud,
    this.direccionReferencia,
  });

  final int solicitudId;
  final int tecnicoId;
  final int? tallerId;
  final EstadoSolicitudEmergencia estado;
  final int? tiempoEstimadoMin;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int clienteId;
  final String nombres;
  final String apellidos;
  final String telefono;
  final String placa;
  final String? marca;
  final String? modelo;
  final String? tipoVehiculo;
  final double? latitud;
  final double? longitud;
  final String? direccionReferencia;

  String get clienteNombreCompleto => ('$nombres $apellidos').trim();

  String get vehiculoLinea {
    final parts = <String>[
      placa,
      if (marca != null && marca!.trim().isNotEmpty) marca!.trim(),
      if (modelo != null && modelo!.trim().isNotEmpty) modelo!.trim(),
    ];
    return parts.join(' · ');
  }

  bool get esTerminal =>
      estado == EstadoSolicitudEmergencia.finalizada || estado == EstadoSolicitudEmergencia.cancelada;

  factory ServicioAsignadoTecnico.fromJson(Map<String, dynamic> j) {
    return ServicioAsignadoTecnico(
      solicitudId: j['solicitud_id'] as int,
      tecnicoId: j['tecnico_id'] as int,
      tallerId: j['taller_id'] as int?,
      estado: EstadoSolicitudEmergencia.parse(j['estado'] as String),
      tiempoEstimadoMin: j['tiempo_estimado_min'] as int?,
      createdAt: _asDateTime(j['created_at']),
      updatedAt: _asDateTime(j['updated_at']),
      clienteId: j['cliente_id'] as int,
      nombres: j['nombres'] as String? ?? '',
      apellidos: j['apellidos'] as String? ?? '',
      telefono: j['telefono'] as String? ?? '',
      placa: j['placa'] as String? ?? '',
      marca: j['marca'] as String?,
      modelo: j['modelo'] as String?,
      tipoVehiculo: j['tipo_vehiculo'] as String?,
      latitud: _asDoubleNullable(j['latitud']),
      longitud: _asDoubleNullable(j['longitud']),
      direccionReferencia: j['direccion_referencia'] as String?,
    );
  }
}

/// Transiciones permitidas por el backend (CU34).
List<EstadoSolicitudEmergencia> estadosDestinoPermitidos(EstadoSolicitudEmergencia actual) {
  return switch (actual) {
    EstadoSolicitudEmergencia.tecnicoAsignado => const [EstadoSolicitudEmergencia.enCamino],
    EstadoSolicitudEmergencia.enCamino => const [EstadoSolicitudEmergencia.enAtencion],
    EstadoSolicitudEmergencia.enAtencion => const [EstadoSolicitudEmergencia.finalizada],
    _ => const [],
  };
}

String etiquetaAccionEstado(EstadoSolicitudEmergencia destino) => switch (destino) {
      EstadoSolicitudEmergencia.enCamino => 'En camino',
      EstadoSolicitudEmergencia.enAtencion => 'En atención',
      EstadoSolicitudEmergencia.finalizada => 'Finalizar servicio',
      _ => destino.etiquetaUi,
    };

/// `GET .../solicitudes/{id}/ubicacion` (CU33).
@immutable
final class UbicacionClienteActual {
  const UbicacionClienteActual({
    required this.solicitudId,
    required this.latitud,
    required this.longitud,
    this.precisionMetros,
    this.direccionReferencia,
    required this.registradoAt,
  });

  final int solicitudId;
  final double latitud;
  final double longitud;
  final double? precisionMetros;
  final String? direccionReferencia;
  final DateTime registradoAt;

  factory UbicacionClienteActual.fromJson(Map<String, dynamic> j) {
    return UbicacionClienteActual(
      solicitudId: j['solicitud_id'] as int,
      latitud: _asDouble(j['latitud']),
      longitud: _asDouble(j['longitud']),
      precisionMetros: j['precision_metros'] != null ? _asDouble(j['precision_metros']) : null,
      direccionReferencia: j['direccion_referencia'] as String?,
      registradoAt: _asDateTime(j['registrado_at']),
    );
  }
}
