final class TallerDashboard {
  const TallerDashboard({
    required this.tecnicosRegistrados,
    required this.tecnicosActivos,
    required this.disponibilidadGeneral,
    required this.tallerEstado,
    required this.usuariosActivos,
    required this.clientesRegistrados,
  });

  final int tecnicosRegistrados;
  final int tecnicosActivos;
  final String disponibilidadGeneral;
  final String tallerEstado;
  final int usuariosActivos;
  final int clientesRegistrados;

  factory TallerDashboard.fromJson(Map<String, dynamic> j) {
    return TallerDashboard(
      tecnicosRegistrados: j['tecnicos_registrados'] as int? ?? 0,
      tecnicosActivos: j['tecnicos_activos'] as int? ?? 0,
      disponibilidadGeneral: j['disponibilidad_general'] as String? ?? '—',
      tallerEstado: (j['taller_estado'] ?? '—').toString(),
      usuariosActivos: j['usuarios_activos'] as int? ?? 0,
      clientesRegistrados: j['clientes_registrados'] as int? ?? 0,
    );
  }
}
