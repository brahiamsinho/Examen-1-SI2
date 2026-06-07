import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../domain/solicitud_eta_models.dart';

/// CU44 — último ETA consultado por solicitud (fallback sin red).
final class EtaCacheRepo {
  EtaCacheRepo(this._prefs);

  final SharedPreferences _prefs;
  static const _prefix = 'cu44_eta_cache_';

  SolicitudEtaConsulta? read(int solicitudId) {
    final raw = _prefs.getString('$_prefix$solicitudId');
    if (raw == null || raw.isEmpty) return null;
    try {
      return SolicitudEtaConsulta.fromJson(jsonDecode(raw) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  Future<void> write(SolicitudEtaConsulta eta) async {
    await _prefs.setString('$_prefix${eta.solicitudId}', jsonEncode(eta.toJson()));
  }
}
