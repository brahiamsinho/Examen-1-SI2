import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/network_reachability.dart';
import '../data/solicitud_draft_repo.dart';
import '../domain/solicitud_draft.dart';
import 'emergencias_providers.dart';
import 'sync_orquestador.dart';
import 'sync_pendientes.dart';

final solicitudDraftRepoProvider = Provider<SolicitudDraftRepo>((ref) {
  return SolicitudDraftRepo();
});

final networkReachabilityProvider = Provider<NetworkReachability>((ref) {
  return NetworkReachability();
});

final syncPendientesProvider = Provider<SyncPendientes>((ref) {
  return SyncPendientes(
    emergenciasRepo: ref.watch(emergenciasRepositoryProvider),
    draftRepo: ref.watch(solicitudDraftRepoProvider),
  );
});

final syncOrquestadorProvider = Provider<SyncOrquestador>((ref) {
  final orch = SyncOrquestador(
    draftRepo: ref.watch(solicitudDraftRepoProvider),
    syncPendientes: ref.watch(syncPendientesProvider),
    reachability: ref.watch(networkReachabilityProvider),
    onComplete: (result) {
      ref.read(lastSyncResultProvider.notifier).set(result);
      if (result.sent > 0 || result.failed > 0) {
        ref.read(offlineSyncTickProvider.notifier).bump();
        ref.invalidate(misSolicitudesEmergenciasProvider);
      }
    },
  );
  ref.onDispose(orch.dispose);
  return orch;
});

/// Borradores locales pendientes o en borrador (CU45).
final solicitudDraftsProvider = FutureProvider.autoDispose<List<SolicitudDraft>>((ref) async {
  ref.watch(offlineSyncTickProvider);
  return ref.watch(solicitudDraftRepoProvider).listAll();
});

/// Contador para badge de pendientes.
final pendingDraftsCountProvider = FutureProvider.autoDispose<int>((ref) async {
  ref.watch(offlineSyncTickProvider);
  return ref.watch(solicitudDraftRepoProvider).pendingCount();
});

/// Incrementar tras sync manual o automático para refrescar UI.
final offlineSyncTickProvider = NotifierProvider<OfflineSyncTickNotifier, int>(
  OfflineSyncTickNotifier.new,
);

class OfflineSyncTickNotifier extends Notifier<int> {
  @override
  int build() => 0;

  void bump() => state++;
}

/// Resultado del último ciclo de sincronización.
final lastSyncResultProvider = NotifierProvider<LastSyncResultNotifier, SyncBatchResult?>(
  LastSyncResultNotifier.new,
);

class LastSyncResultNotifier extends Notifier<SyncBatchResult?> {
  @override
  SyncBatchResult? build() => null;

  void set(SyncBatchResult? r) => state = r;
}

/// Ejecuta sync manual y actualiza providers relacionados.
final offlineSyncManualProvider = Provider<Future<SyncBatchResult> Function()>((ref) {
  return () async {
    final orch = ref.read(syncOrquestadorProvider);
    final result = await orch.syncNow();
    ref.read(lastSyncResultProvider.notifier).set(result);
    ref.read(offlineSyncTickProvider.notifier).bump();
    ref.invalidate(misSolicitudesEmergenciasProvider);
    return result;
  };
});
