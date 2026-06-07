import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/network/api_error.dart';
import '../data/emergencias_repository.dart';
import '../data/eta_cache_repo.dart';
import '../domain/solicitud_eta_models.dart';
import 'emergencias_providers.dart';

final etaCacheRepoProvider = FutureProvider<EtaCacheRepo>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  return EtaCacheRepo(prefs);
});

/// CU44 — consulta ETA con caché offline.
final consultarEtaProvider =
    FutureProvider.autoDispose.family<ConsultarEtaResult, int>((ref, solicitudId) async {
  final repo = ref.watch(emergenciasRepositoryProvider);
  final cache = await ref.watch(etaCacheRepoProvider.future);
  try {
    final eta = await repo.fetchEtaReparacion(solicitudId);
    await cache.write(eta);
    return ConsultarEtaResult(eta: eta, fromCache: false);
  } on DioException catch (e) {
    final isOffline = e.type == DioExceptionType.connectionError ||
        e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.receiveTimeout;
    if (isOffline) {
      final cached = cache.read(solicitudId);
      if (cached != null) {
        return ConsultarEtaResult(eta: cached, fromCache: true);
      }
    }
    throw Exception(messageFromDio(e));
  }
});
