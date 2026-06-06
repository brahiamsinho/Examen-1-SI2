final class TecnicoPortal {
  const TecnicoPortal({
    required this.id,
    required this.usuarioId,
    required this.nombreCompleto,
    required this.email,
    required this.telefono,
    required this.estado,
    this.especialidadNombre,
  });

  final int id;
  final int usuarioId;
  final String nombreCompleto;
  final String email;
  final String telefono;
  final String estado;
  final String? especialidadNombre;

  bool get activo => estado.toUpperCase() == 'ACTIVO';

  factory TecnicoPortal.fromJson(Map<String, dynamic> j) {
    final n = j['nombres'] as String? ?? '';
    final a = j['apellidos'] as String? ?? '';
    return TecnicoPortal(
      id: j['id'] as int,
      usuarioId: j['usuario_id'] as int,
      nombreCompleto: ('$n $a').trim(),
      email: j['email'] as String? ?? '',
      telefono: j['telefono'] as String? ?? '',
      estado: (j['estado'] ?? '').toString(),
      especialidadNombre: j['especialidad_nombre'] as String?,
    );
  }
}
