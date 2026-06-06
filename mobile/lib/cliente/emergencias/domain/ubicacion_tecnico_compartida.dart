import 'package:flutter/foundation.dart';
import '../../../core/utils/api_datetime.dart';

double _asDouble(Object? v) {
  if (v is num) return v.toDouble();
  if (v is String) return double.parse(v);
  throw FormatException('No es número: $v');
}

double? _asDoubleNullable(Object? v) {
  if (v == null) return null;
  return _asDouble(v);
}

DateTime _asDateTime(Object? v) {
  return parseApiDateTime(v);
}

/// Ruta VRT (Vehicle Routing & Tracking) técnico → cliente con ETA.
@immutable
final class RutaSeguimientoVrt {
  const RutaSeguimientoVrt({
    required this.distanciaMetros,
    required this.duracionSegundos,
    required this.duracionMinutos,
    required this.etaLlegadaAt,
    required this.geometria,
    required this.proveedor,
  });

  final double distanciaMetros;
  final int duracionSegundos;
  final int duracionMinutos;
  final DateTime etaLlegadaAt;
  /// Puntos [lat, lon] para polyline en el mapa.
  final List<List<double>> geometria;
  /// `osrm` (por calles) o `haversine` (línea directa aproximada).
  final String proveedor;

  bool get esRutaPorCalles => proveedor == 'osrm';

  double get distanciaKm => distanciaMetros / 1000.0;

  factory RutaSeguimientoVrt.fromJson(Map<String, dynamic> j) {
    final geomRaw = j['geometria'] as List<dynamic>? ?? const [];
    final geometria = geomRaw
        .map((p) {
          final pair = p as List<dynamic>;
          return [_asDouble(pair[0]), _asDouble(pair[1])];
        })
        .toList(growable: false);
    return RutaSeguimientoVrt(
      distanciaMetros: _asDouble(j['distancia_metros']),
      duracionSegundos: j['duracion_segundos'] as int,
      duracionMinutos: j['duracion_minutos'] as int,
      etaLlegadaAt: _asDateTime(j['eta_llegada_at']),
      geometria: geometria,
      proveedor: (j['proveedor'] ?? '').toString(),
    );
  }
}

/// Respuesta de `GET .../ubicacion-tecnico` (cliente) y `POST .../ubicacion-tecnico` (técnico).
@immutable
final class UbicacionTecnicoCompartida {
  const UbicacionTecnicoCompartida({
    required this.solicitudId,
    required this.latitud,
    required this.longitud,
    this.precisionMetros,
    required this.actualizadoAt,
    this.clienteLatitud,
    this.clienteLongitud,
    this.ruta,
  });

  final int solicitudId;
  final double latitud;
  final double longitud;
  final double? precisionMetros;
  final DateTime actualizadoAt;
  final double? clienteLatitud;
  final double? clienteLongitud;
  final RutaSeguimientoVrt? ruta;

  factory UbicacionTecnicoCompartida.fromJson(Map<String, dynamic> j) {
    return UbicacionTecnicoCompartida(
      solicitudId: j['solicitud_id'] as int,
      latitud: _asDouble(j['latitud']),
      longitud: _asDouble(j['longitud']),
      precisionMetros: j['precision_metros'] != null ? _asDoubleNullable(j['precision_metros']) : null,
      actualizadoAt: _asDateTime(j['actualizado_at']),
      clienteLatitud: j['cliente_latitud'] != null ? _asDoubleNullable(j['cliente_latitud']) : null,
      clienteLongitud: j['cliente_longitud'] != null ? _asDoubleNullable(j['cliente_longitud']) : null,
      ruta: j['ruta'] != null ? RutaSeguimientoVrt.fromJson(j['ruta'] as Map<String, dynamic>) : null,
    );
  }
}
