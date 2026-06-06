// Modelos CU37 — ranking y selección de taller.
class TallerCandidato {
  const TallerCandidato({
    required this.tallerId,
    required this.nombreComercial,
    required this.score,
    this.abiertoAhora = true,
    this.distanciaKm,
    this.cargaBandeja,
  });

  final int tallerId;
  final String nombreComercial;
  final double score;
  final bool abiertoAhora;
  final double? distanciaKm;
  final int? cargaBandeja;

  factory TallerCandidato.fromJson(Map<String, dynamic> json) {
    final detalle = json['detalle'];
    double? dist;
    int? carga;
    if (detalle is Map<String, dynamic>) {
      final d = detalle['distancia_km'];
      if (d is num) dist = d.toDouble();
      final c = detalle['carga_bandeja'];
      if (c is num) carga = c.toInt();
    }
    return TallerCandidato(
      tallerId: (json['taller_id'] as num).toInt(),
      nombreComercial: json['nombre_comercial'] as String? ?? 'Taller',
      score: (json['score'] as num?)?.toDouble() ?? 0,
      abiertoAhora: json['abierto_ahora'] as bool? ?? true,
      distanciaKm: dist,
      cargaBandeja: carga,
    );
  }
}

class TalleresCandidatosResponse {
  const TalleresCandidatosResponse({
    required this.candidatos,
    this.mejorTallerId,
  });

  final List<TallerCandidato> candidatos;
  final int? mejorTallerId;

  factory TalleresCandidatosResponse.fromJson(Map<String, dynamic> json) {
    final raw = json['candidatos'];
    final list = <TallerCandidato>[];
    if (raw is List) {
      for (final e in raw) {
        if (e is Map<String, dynamic>) list.add(TallerCandidato.fromJson(e));
      }
    }
    final mejor = json['mejor_taller_id'];
    return TalleresCandidatosResponse(
      candidatos: list,
      mejorTallerId: mejor is num ? mejor.toInt() : null,
    );
  }
}

class SeleccionTallerResult {
  const SeleccionTallerResult({
    required this.solicitudId,
    required this.tallerId,
    required this.bandejaId,
    required this.estado,
  });

  final int solicitudId;
  final int tallerId;
  final int bandejaId;
  final String estado;

  factory SeleccionTallerResult.fromJson(Map<String, dynamic> json) {
    return SeleccionTallerResult(
      solicitudId: (json['solicitud_id'] as num).toInt(),
      tallerId: (json['taller_id'] as num).toInt(),
      bandejaId: (json['bandeja_id'] as num).toInt(),
      estado: json['estado'] as String? ?? 'EN_REVISION',
    );
  }
}
