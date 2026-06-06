import '../config/app_env.dart';
import 'tenant_slug_storage.dart';

/// Slug persistido o default de `.env`.
Future<String> resolveInitialTenantSlug() async {
  final stored = await TenantSlugStorage().read();
  if (stored != null && stored.trim().isNotEmpty) {
    return stored.trim().toLowerCase();
  }
  return AppEnv.tenantSlugDefault.trim().toLowerCase();
}

Future<void> persistTenantSlug(String slug) async {
  await TenantSlugStorage().write(slug.trim().toLowerCase());
}
