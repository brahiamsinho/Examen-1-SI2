// Registro y baja de token FCM (CU19) al iniciar o cerrar sesión cliente / técnico.
import 'dart:async';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart' show debugPrint, defaultTargetPlatform, kIsWeb, TargetPlatform;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';

import '../../cliente/application/cliente_injection.dart';
import '../../tecnico/application/tecnico_injection.dart';
import '../constants/api_constants.dart';
import 'firebase_bootstrap.dart';

@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  debugPrint('FCM background: ${message.messageId} data=${message.data}');
}

final _lastClienteToken = <String, String?>{'t': null};
final _lastTecnicoToken = <String, String?>{'t': null};

Future<String?> _ensurePermissionAndToken() async {
  if (kIsWeb || !firebaseReady) {
    return null;
  }
  if (defaultTargetPlatform == TargetPlatform.android) {
    final s = await Permission.notification.status;
    if (!s.isGranted) {
      final r = await Permission.notification.request();
      if (!r.isGranted) return null;
    }
  } else {
    final settings = await FirebaseMessaging.instance.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    if (settings.authorizationStatus == AuthorizationStatus.denied) {
      return null;
    }
  }
  return FirebaseMessaging.instance.getToken();
}

String _androidOrIos() {
  if (kIsWeb) return 'web';
  if (defaultTargetPlatform == TargetPlatform.android) return 'android';
  if (defaultTargetPlatform == TargetPlatform.iOS) return 'ios';
  return 'unknown';
}

class FcmRegistration {
  FcmRegistration(this._ref);

  final Ref _ref;
  StreamSubscription<String>? _tokenRefreshSub;
  bool _listeningRefresh = false;

  void _ensureTokenRefreshListener() {
    if (_listeningRefresh || kIsWeb || !firebaseReady) return;
    _listeningRefresh = true;
    _tokenRefreshSub = FirebaseMessaging.instance.onTokenRefresh.listen((token) async {
      debugPrint('FCM token refresh: ${token.substring(0, 8)}…');
      if (_lastClienteToken['t'] != null) {
        _lastClienteToken['t'] = token;
        try {
          await _ref.read(comunicacionRepositoryProvider).registrarTokenFcm(
                token: token,
                platform: _androidOrIos(),
              );
        } catch (e) {
          debugPrint('FCM refresh registro cliente falló: $e');
        }
      }
      if (_lastTecnicoToken['t'] != null) {
        _lastTecnicoToken['t'] = token;
        try {
          await _ref.read(tecnicoDioProvider).post<void>(
                ApiConstants.appTecnicoFcm,
                data: {'token': token, 'platform': _androidOrIos()},
              );
        } catch (e) {
          debugPrint('FCM refresh registro técnico falló: $e');
        }
      }
    });
  }

  void dispose() {
    unawaited(_tokenRefreshSub?.cancel());
    _tokenRefreshSub = null;
    _listeningRefresh = false;
  }

  /// Tras login o al restaurar sesión (cliente).
  Future<void> onClienteSessionActive() async {
    if (kIsWeb) {
      return;
    }
    _ensureTokenRefreshListener();
    final token = await _ensurePermissionAndToken();
    if (token == null) {
      debugPrint('FCM cliente: sin permiso o token nulo');
      return;
    }
    _lastClienteToken['t'] = token;
    final repo = _ref.read(comunicacionRepositoryProvider);
    try {
      await repo.registrarTokenFcm(token: token, platform: _androidOrIos());
      debugPrint('FCM cliente registrado (${token.substring(0, 8)}…)');
    } catch (e) {
      debugPrint('FCM registro cliente falló: $e');
    }
  }

  /// Antes de [AuthRepository.logout] (Authorization aún válido).
  Future<void> beforeClienteLogout() async {
    if (kIsWeb) {
      return;
    }
    final t = _lastClienteToken['t'] ?? await FirebaseMessaging.instance.getToken();
    if (t == null) return;
    final repo = _ref.read(comunicacionRepositoryProvider);
    try {
      await repo.eliminarTokenFcm(token: t, platform: _androidOrIos());
    } catch (_) {}
    _lastClienteToken['t'] = null;
  }

  /// Tras login o al restaurar sesión (técnico).
  Future<void> onTecnicoSessionActive() async {
    if (kIsWeb) {
      return;
    }
    _ensureTokenRefreshListener();
    final token = await _ensurePermissionAndToken();
    if (token == null) {
      debugPrint('FCM técnico: sin permiso o token nulo');
      return;
    }
    _lastTecnicoToken['t'] = token;
    final dio = _ref.read(tecnicoDioProvider);
    try {
      await dio.post<void>(
        ApiConstants.appTecnicoFcm,
        data: {'token': token, 'platform': _androidOrIos()},
      );
      debugPrint('FCM técnico registrado (${token.substring(0, 8)}…)');
    } catch (e) {
      debugPrint('FCM registro técnico falló: $e');
    }
  }

  /// Antes de cerrar sesión técnico.
  Future<void> beforeTecnicoLogout() async {
    if (kIsWeb) {
      return;
    }
    final t = _lastTecnicoToken['t'] ?? await FirebaseMessaging.instance.getToken();
    if (t == null) return;
    final dio = _ref.read(tecnicoDioProvider);
    try {
      await dio.delete<void>(ApiConstants.appTecnicoFcm, data: {'token': t, 'platform': _androidOrIos()});
    } catch (_) {}
    _lastTecnicoToken['t'] = null;
  }
}

final fcmRegistrationProvider = Provider<FcmRegistration>((ref) {
  return FcmRegistration(ref);
});
