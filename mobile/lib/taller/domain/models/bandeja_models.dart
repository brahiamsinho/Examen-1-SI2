final class BandejaIncidente {
  const BandejaIncidente({
    required this.bandejaId,
    required this.solicitudId,
    required this.estadoSolicitud,
    required this.descripcionTexto,
    required this.createdAt,
    required this.placa,
    required this.clienteNombre,
    this.marca,
    this.modelo,
    this.nivelPrioridad,
    this.estadoBandeja,
    this.motivoRechazo,
    this.evidenciasCount = 0,
  });

  final int bandejaId;
  final int solicitudId;
  final String estadoSolicitud;
  final String? descripcionTexto;
  final DateTime createdAt;
  final String placa;
  final String clienteNombre;
  final String? marca;
  final String? modelo;
  final String? nivelPrioridad;
  final String? estadoBandeja;
  final String? motivoRechazo;
  final int evidenciasCount;

  factory BandejaIncidente.fromJson(Map<String, dynamic> j) {
    final nombres = j['nombres'] as String? ?? '';
    final apellidos = j['apellidos'] as String? ?? '';
    final evidencias = j['evidencias'];
    return BandejaIncidente(
      bandejaId: j['bandeja_id'] as int,
      solicitudId: j['solicitud_id'] as int,
      estadoSolicitud: (j['estado_solicitud'] ?? '').toString(),
      descripcionTexto: j['descripcion_texto'] as String?,
      createdAt: DateTime.parse(j['created_at'] as String),
      placa: j['placa'] as String? ?? '—',
      clienteNombre: ('$nombres $apellidos').trim(),
      marca: j['marca'] as String?,
      modelo: j['modelo'] as String?,
      nivelPrioridad: j['nivel_prioridad'] as String?,
      estadoBandeja: j['estado_bandeja'] as String?,
      motivoRechazo: j['motivo_rechazo'] as String?,
      evidenciasCount: evidencias is List ? evidencias.length : 0,
    );
  }
}

final class AsignacionTecnico {
  const AsignacionTecnico({
    required this.id,
    required this.tecnicoId,
    required this.estado,
    required this.createdAt,
    this.observacion,
  });

  final int id;
  final int tecnicoId;
  final String estado;
  final DateTime createdAt;
  final String? observacion;

  factory AsignacionTecnico.fromJson(Map<String, dynamic> j) {
    return AsignacionTecnico(
      id: j['id'] as int,
      tecnicoId: j['tecnico_id'] as int,
      estado: (j['estado'] ?? '').toString(),
      createdAt: DateTime.parse(j['created_at'] as String),
      observacion: j['observacion'] as String?,
    );
  }
}
