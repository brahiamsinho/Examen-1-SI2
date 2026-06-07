import 'dart:async';
import 'dart:math';

import 'package:connectivity_plus/connectivity_plus.dart';

import '../data/network_reachability.dart';
import '../data/solicitud_draft_repo.dart';
import '../domain/solicitud_draft.dart';
import 'sync_exceptions.dart';
import 'sync_pendientes.dart';

/// CU43 — detecta red, procesa cola local con backoff exponencial.
final class SyncOrquestador {
  SyncOrquestador({
    required SolicitudDraftRepo draftRepo,
    required SyncPendientes syncPendientes,
    required NetworkReachability reachability,
    void Function(SyncBatchResult result)? onComplete,
  })  : _draftRepo = draftRepo,
        _syncPendientes = syncPendientes,
        _reachability = reachability,
        _onComplete = onComplete;

  final SolicitudDraftRepo _draftRepo;
  final SyncPendientes _syncPendientes;
  final NetworkReachability _reachability;
  final void Function(SyncBatchResult result)? _onComplete;

  StreamSubscription<List<ConnectivityResult>>? _connSub;
  bool _pausedAuth = false;
  bool _running = false;
  SyncBatchResult _lastResult = const SyncBatchResult(sent: 0, failed: 0, skippedAuth: false);

  SyncBatchResult get lastResult => _lastResult;
  bool get isRunning => _running;
  bool get pausedForAuth => _pausedAuth;

  void start() {
    _connSub ??= _reachability.onConnectivityChanged.listen((_) {
      unawaited(syncNow());
    });
    unawaited(syncNow());
  }

  void resumeAfterLogin() {
    _pausedAuth = false;
    unawaited(syncNow());
  }

  void dispose() {
    _connSub?.cancel();
    _connSub = null;
  }

  Future<SyncBatchResult> syncNow() async {
    if (_pausedAuth || _running) return _lastResult;
    if (!await _reachability.hasConnectivity()) {
      return _lastResult;
    }

    _running = true;
    var sent = 0;
    var failed = 0;
    String? lastMsg;

    try {
      final pending = await _draftRepo.listPendingSync();
      for (final draft in pending) {
        if (_pausedAuth) break;
        final delaySec = _backoffSeconds(draft.retryCount);
        if (delaySec > 0 && draft.status == SolicitudDraftStatus.failed) {
          final age = DateTime.now().toUtc().difference(draft.updatedAt).inSeconds;
          if (age < delaySec) continue;
        }
        try {
          final sid = await _syncPendientes.syncDraft(draft);
          sent++;
          lastMsg = 'Solicitud #$sid sincronizada';
        } on SessionExpiredSyncException {
          _pausedAuth = true;
          lastMsg = 'Sesión expirada — iniciá sesión para continuar';
          break;
        } on PermanentSyncException catch (e) {
          failed++;
          lastMsg = e.message;
        } catch (_) {
          failed++;
          lastMsg = 'Error al sincronizar borrador';
        }
      }
    } finally {
      _running = false;
      _lastResult = SyncBatchResult(
        sent: sent,
        failed: failed,
        skippedAuth: _pausedAuth,
        lastMessage: lastMsg,
      );
      _onComplete?.call(_lastResult);
    }
    return _lastResult;
  }

  int _backoffSeconds(int retryCount) {
    if (retryCount <= 0) return 0;
    final base = min(300, pow(2, min(retryCount, 8)).toInt());
    return base;
  }
}
