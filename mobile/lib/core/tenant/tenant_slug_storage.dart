import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Slug de organización (SaaS) para header `X-Tenant-Slug`.
final class TenantSlugStorage {
  TenantSlugStorage({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  static const _key = 'tenant_slug';

  final FlutterSecureStorage _storage;

  Future<String?> read() => _storage.read(key: _key);

  Future<void> write(String slug) async {
    final s = slug.trim().toLowerCase();
    if (s.isEmpty) {
      await _storage.delete(key: _key);
      return;
    }
    await _storage.write(key: _key, value: s);
  }

  Future<void> clear() => _storage.delete(key: _key);
}
