// Cliente HTTP para el módulo responsable de taller — tokens separados.
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../constants/api_constants.dart';
import '../tenant/tenant_slug_storage.dart';

class TallerApiClient {
  static final TallerApiClient _instance = TallerApiClient._internal();
  factory TallerApiClient() => _instance;

  late final Dio _dio;
  final _storage = const FlutterSecureStorage();
  final _tenantSlug = TenantSlugStorage();

  static const _accessKey = 'taller_access_token';
  static const _refreshKey = 'taller_refresh_token';

  TallerApiClient._internal() {
    _dio = Dio(BaseOptions(
      baseUrl: ApiConstants.baseUrl,
      connectTimeout: ApiConstants.connectTimeout,
      receiveTimeout: ApiConstants.receiveTimeout,
      headers: {'Content-Type': 'application/json'},
    ));

    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _storage.read(key: _accessKey);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        final slug = await _tenantSlug.read();
        if (slug != null && slug.isNotEmpty) {
          options.headers['X-Tenant-Slug'] = slug;
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        if (error.response?.statusCode == 401) {
          _storage.delete(key: _accessKey);
          _storage.delete(key: _refreshKey);
        }
        return handler.next(error);
      },
    ));
  }

  Dio get dio => _dio;

  Future<void> persistTokens({required String access, required String refresh}) async {
    await _storage.write(key: _accessKey, value: access);
    await _storage.write(key: _refreshKey, value: refresh);
  }

  Future<void> clearTokens() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  Future<String?> readAccessToken() => _storage.read(key: _accessKey);
}
