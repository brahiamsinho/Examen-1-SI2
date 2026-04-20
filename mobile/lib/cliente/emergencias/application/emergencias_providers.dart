import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../application/cliente_injection.dart';
import '../data/emergencias_repository.dart';
import '../data/optional_public_upload_service.dart';
import '../domain/solicitud_emergencia_models.dart';
import '../domain/solicitud_seguimiento_models.dart';

final emergenciasRepositoryProvider = Provider<EmergenciasRepository>((ref) {
  return EmergenciasRepository(ref.watch(dioProvider));
});

final optionalPublicUploadServiceProvider = Provider<OptionalPublicUploadService>((ref) {
  return OptionalPublicUploadService();
});

/// Lista de solicitudes del cliente (polling: invalidar este provider).
final misSolicitudesEmergenciasProvider =
    FutureProvider.autoDispose<List<SolicitudEmergenciaListItem>>((ref) async {
  return ref.watch(emergenciasRepositoryProvider).listMine();
});

/// Detalle fase 1 (+ campos fase 2 en JSON).
final emergenciaDetailProvider =
    FutureProvider.autoDispose.family<SolicitudEmergenciaDetail, int>((ref, solicitudId) async {
  return ref.watch(emergenciasRepositoryProvider).fetchDetail(solicitudId);
});

/// Seguimiento agregado CU16–CU18.
final emergenciaSeguimientoProvider =
    FutureProvider.autoDispose.family<SolicitudSeguimiento, int>((ref, solicitudId) async {
  return ref.watch(emergenciasRepositoryProvider).fetchSeguimiento(solicitudId);
});
