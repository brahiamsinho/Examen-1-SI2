import 'package:dio/dio.dart';

import '../../core/constants/api_constants.dart';
import '../../core/network/api_error.dart';
import '../domain/models/bandeja_models.dart';
import '../domain/models/tecnico_portal_models.dart';
import '../domain/models/taller_dashboard.dart';

final class TallerRepository {
  TallerRepository(this._dio);

  final Dio _dio;

  Future<TallerDashboard> fetchDashboard() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerDashboard);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía del dashboard.');
      return TallerDashboard.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<BandejaIncidente>> listBandejaDisponibles() async {
    try {
      final res = await _dio.get<List<dynamic>>(ApiConstants.appTallerEmergenciasBandejaDisponibles);
      final list = res.data ?? const [];
      return list
          .whereType<Map<String, dynamic>>()
          .map(BandejaIncidente.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<BandejaIncidente> fetchBandejaDetalle(int bandejaId) async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(
        ApiConstants.appTallerEmergenciasBandejaDetalle(bandejaId),
      );
      final data = res.data;
      if (data == null) throw Exception('Incidente no encontrado.');
      return BandejaIncidente.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<BandejaIncidente> aceptarBandeja(int bandejaId) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerEmergenciasBandejaAceptar(bandejaId),
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida al aceptar.');
      return BandejaIncidente.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<BandejaIncidente> rechazarBandeja(int bandejaId, String motivo) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerEmergenciasBandejaRechazar(bandejaId),
        data: {'motivo_rechazo': motivo.trim()},
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida al rechazar.');
      return BandejaIncidente.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<TecnicoPortal>> listTecnicos() async {
    try {
      final res = await _dio.get<List<dynamic>>(ApiConstants.appTallerTecnicos);
      final list = res.data ?? const [];
      return list.whereType<Map<String, dynamic>>().map(TecnicoPortal.fromJson).toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<void> asignarTecnico({
    required int solicitudId,
    required int tecnicoId,
    int? tiempoEstimadoMin,
    String? observacion,
  }) async {
    try {
      await _dio.post<void>(
        ApiConstants.appTallerEmergenciasAsignarTecnico(solicitudId),
        data: {
          'tecnico_id': tecnicoId,
          if (tiempoEstimadoMin != null) 'tiempo_estimado_min': tiempoEstimadoMin,
          if (observacion != null && observacion.trim().isNotEmpty) 'observacion': observacion.trim(),
        },
      );
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<AsignacionTecnico>> listAsignaciones(int solicitudId) async {
    try {
      final res = await _dio.get<List<dynamic>>(
        ApiConstants.appTallerEmergenciasAsignaciones(solicitudId),
      );
      final list = res.data ?? const [];
      return list.whereType<Map<String, dynamic>>().map(AsignacionTecnico.fromJson).toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }
}
