import 'dart:convert';

import 'package:hive_flutter/hive_flutter.dart';

import '../domain/solicitud_draft.dart';

/// Persistencia local de borradores CU45 (Hive, sin code-gen).
final class SolicitudDraftRepo {
  SolicitudDraftRepo();

  static const _boxName = 'solicitud_drafts_v1';
  Box<String>? _box;

  Future<void> init() async {
    if (_box != null && _box!.isOpen) return;
    _box = await Hive.openBox<String>(_boxName);
  }

  Box<String> get _store {
    final b = _box;
    if (b == null || !b.isOpen) {
      throw StateError('SolicitudDraftRepo no inicializado. Llamá init() en main.');
    }
    return b;
  }

  Future<List<SolicitudDraft>> listAll() async {
    final out = <SolicitudDraft>[];
    for (final raw in _store.values) {
      try {
        final m = jsonDecode(raw) as Map<String, dynamic>;
        out.add(SolicitudDraft.fromJson(m));
      } catch (_) {
        // ignorar entradas corruptas
      }
    }
    out.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    return out;
  }

  Future<List<SolicitudDraft>> listPendingSync() async {
    final all = await listAll();
    return all.where((d) => d.isPendingSync).toList();
  }

  Future<SolicitudDraft?> getById(String clientRequestId) async {
    final raw = _store.get(clientRequestId);
    if (raw == null) return null;
    return SolicitudDraft.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<void> save(SolicitudDraft draft) async {
    await _store.put(draft.clientRequestId, jsonEncode(draft.toJson()));
  }

  Future<void> delete(String clientRequestId) async {
    await _store.delete(clientRequestId);
  }

  Future<int> pendingCount() async {
    return (await listPendingSync()).length;
  }
}
