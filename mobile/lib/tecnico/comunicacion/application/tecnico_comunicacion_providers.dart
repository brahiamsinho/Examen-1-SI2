import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../application/tecnico_injection.dart';
import '../data/tecnico_comunicacion_repository.dart';
import '../../../cliente/comunicacion/domain/notificacion_models.dart';

final tecnicoComunicacionRepositoryProvider = Provider<TecnicoComunicacionRepository>((ref) {
  return TecnicoComunicacionRepository(ref.watch(tecnicoDioProvider));
});

final notificacionesTecnicoProvider =
    FutureProvider.family<List<NotificacionRead>, bool>((ref, soloNoLeidas) async {
  final repo = ref.watch(tecnicoComunicacionRepositoryProvider);
  return repo.listarNotificaciones(soloNoLeidas: soloNoLeidas);
});
