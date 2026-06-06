import 'package:dio/dio.dart';

import '../../core/constants/api_constants.dart';
import '../../core/network/api_error.dart';
import '../../core/network/taller_api_client.dart';
import '../../core/tenant/tenant_slug_storage.dart';
import '../../tecnico/domain/models/auth_me.dart';
import '../domain/models/taller_perfil.dart';

/// Autenticación del flujo responsable de taller (tokens propios).
final class TallerAuthRepository {
  TallerAuthRepository(this._dio, {TallerApiClient? api}) : _api = api ?? TallerApiClient();

  final Dio _dio;
  final TallerApiClient _api;

  static bool rolesPermitidosTallerApp(List<String> roles) {
    return roles.contains('TALLER_RESPONSABLE');
  }

  Future<AuthMe> login({
    required String email,
    required String password,
    String? tenantSlug,
  }) async {
    try {
      if (tenantSlug != null && tenantSlug.trim().isNotEmpty) {
        await TenantSlugStorage().write(tenantSlug);
      }
      final slug = await TenantSlugStorage().read();
      final headers = <String, String>{};
      if (slug != null && slug.isNotEmpty) {
        headers['X-Tenant-Slug'] = slug;
      }
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.login,
        data: {'email': email.trim(), 'password': password},
        options: Options(headers: headers),
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida del servidor.');
      final access = data['access_token'] as String?;
      final refresh = data['refresh_token'] as String?;
      if (access == null || refresh == null) {
        throw Exception('Respuesta inválida del servidor.');
      }
      await _api.persistTokens(access: access, refresh: refresh);

      final me = await fetchMe();
      if (!rolesPermitidosTallerApp(me.roles)) {
        await logoutLocal();
        throw Exception(
          'Esta cuenta no es responsable de taller. '
          'Usá acceso técnico o cliente según tu rol.',
        );
      }
      return me;
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<AuthMe> fetchMe() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.me);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía de /auth/me');
      return AuthMe.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<TallerPerfil> fetchPerfilCompleto(AuthMe me) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerMiTaller);
      final data = res.data;
      if (data == null) return TallerPerfil.minimal(me);
      return TallerPerfil.fromMiTaller(me: me, tallerJson: data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<void> logout() async {
    try {
      await _dio.post<void>(ApiConstants.logout);
    } catch (_) {
      // Limpia sesión local aunque falle el backend.
    } finally {
      await _api.clearTokens();
    }
  }

  Future<void> logoutLocal() async {
    await _api.clearTokens();
  }

  Future<String?> readAccessToken() => _api.readAccessToken();
}
