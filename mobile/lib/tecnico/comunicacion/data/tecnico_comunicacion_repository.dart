import 'package:dio/dio.dart';

import '../../../core/constants/api_constants.dart';
import '../../../core/network/api_error.dart';
import '../../../cliente/comunicacion/domain/notificacion_models.dart';

final class TecnicoComunicacionRepository {
  TecnicoComunicacionRepository(this._dio);

  final Dio _dio;

  Future<List<NotificacionRead>> listarNotificaciones({
    bool soloNoLeidas = false,
    int limit = 100,
  }) async {
    try {
      final res = await _dio.get<List<dynamic>>(
        ApiConstants.appTecnicoNotificaciones,
        queryParameters: {
          'no_leidas': soloNoLeidas,
          'limit': limit,
        },
      );
      final raw = res.data ?? [];
      return [
        for (final e in raw)
          if (e is Map<String, dynamic>) NotificacionRead.fromJson(e),
      ];
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<NotificacionRead> marcarNotificacionLeida(int notificacionId) async {
    try {
      final res = await _dio.patch<Map<String, dynamic>>(
        ApiConstants.appTecnicoNotificacionLeida(notificacionId),
      );
      final m = res.data;
      if (m == null) throw Exception('Respuesta vacía');
      return NotificacionRead.fromJson(m);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }
}
