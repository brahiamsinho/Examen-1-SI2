import '../../../tecnico/domain/models/auth_me.dart';

/// Perfil del responsable de taller para UI mobile.
final class TallerPerfil {
  const TallerPerfil({
    required this.usuarioId,
    required this.tallerId,
    required this.nombres,
    required this.apellidos,
    required this.email,
    required this.roles,
    this.telefono,
    this.tallerNombre,
    this.tallerEstado,
    this.ciudad,
  });

  final int usuarioId;
  final int tallerId;
  final String nombres;
  final String apellidos;
  final String email;
  final List<String> roles;
  final String? telefono;
  final String? tallerNombre;
  final String? tallerEstado;
  final String? ciudad;

  String get nombreCompleto => ('$nombres $apellidos').trim();

  factory TallerPerfil.fromMiTaller({
    required AuthMe me,
    required Map<String, dynamic> tallerJson,
  }) {
    return TallerPerfil(
      usuarioId: me.id,
      tallerId: tallerJson['id'] as int? ?? 0,
      nombres: tallerJson['responsable_nombres'] as String? ?? me.nombres,
      apellidos: tallerJson['responsable_apellidos'] as String? ?? me.apellidos,
      email: tallerJson['responsable_email'] as String? ?? me.email,
      roles: me.roles,
      telefono: tallerJson['responsable_telefono'] as String?,
      tallerNombre: tallerJson['nombre_comercial'] as String?,
      tallerEstado: (tallerJson['estado'] ?? '').toString(),
      ciudad: tallerJson['ciudad'] as String?,
    );
  }

  factory TallerPerfil.minimal(AuthMe me) {
    return TallerPerfil(
      usuarioId: me.id,
      tallerId: 0,
      nombres: me.nombres,
      apellidos: me.apellidos,
      email: me.email,
      roles: me.roles,
    );
  }
}
