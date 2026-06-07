import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:http_parser/http_parser.dart';

import '../../core/constants/api_constants.dart';
import '../../core/network/api_error.dart';
import '../domain/models/bandeja_models.dart';
import '../domain/models/tecnico_portal_models.dart';
import '../domain/models/taller_dashboard.dart';
import '../domain/models/taller_modulos_models.dart';

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

  Future<TallerDisponibilidad> fetchDisponibilidad() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerEmergenciasDisponibilidad);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return TallerDisponibilidad.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<TallerDisponibilidad> updateDisponibilidad({
    required bool aceptaNuevasSolicitudes,
    required int capacidadMaximaDiaria,
    String? observacion,
  }) async {
    try {
      final res = await _dio.put<Map<String, dynamic>>(
        ApiConstants.appTallerEmergenciasDisponibilidad,
        data: {
          'acepta_nuevas_solicitudes': aceptaNuevasSolicitudes,
          'capacidad_maxima_diaria': capacidadMaximaDiaria,
          if (observacion != null && observacion.trim().isNotEmpty) 'observacion': observacion.trim(),
        },
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida.');
      return TallerDisponibilidad.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ResumenComisiones> fetchResumenComisiones() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerEmergenciasComisionesResumen);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ResumenComisiones.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<ComisionTaller>> listComisiones() async {
    try {
      final res = await _dio.get<List<dynamic>>(ApiConstants.appTallerEmergenciasComisiones);
      return (res.data ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ComisionTaller.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<HistorialAtencion>> listHistorialAtenciones({int limit = 50}) async {
    try {
      final res = await _dio.get<List<dynamic>>(
        ApiConstants.appTallerEmergenciasHistorial,
        queryParameters: {'limit': limit},
      );
      return (res.data ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(HistorialAtencion.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReporteTallerDashboard> fetchReporteDashboard() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerEmergenciasReportesDashboard);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ReporteTallerDashboard.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<ReportPlantilla>> listReportPlantillas({bool? systemOnly}) async {
    try {
      final res = await _dio.get<List<dynamic>>(
        ApiConstants.appTallerReportesPlantillas,
        queryParameters: systemOnly == null ? null : {'is_system_report': systemOnly},
      );
      return (res.data ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(ReportPlantilla.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReportRunResult> runReportPlantilla(int id) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(ApiConstants.appTallerReportePlantillaRun(id));
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ReportRunResult.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReportExecuteResult> executeReportQbe(QbePayload qbe) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerReportesExecute,
        data: qbe.toJson(),
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ReportExecuteResult.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReportNlQueryResult> nlReportQuery(String query) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerReportesNlQuery,
        data: {'query': query.trim()},
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ReportNlQueryResult.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReportVoiceTranscribeResult> voiceReportQuery({
    required String filePath,
    String filename = 'consulta-reporte.m4a',
    String mimeType = 'audio/mp4',
  }) async {
    try {
      final form = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          filePath,
          filename: filename,
          contentType: MediaType.parse(mimeType),
        ),
      });
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerReportesVoice,
        data: form,
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return ReportVoiceTranscribeResult.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<Uint8List> exportReportQbe(QbePayload qbe, ReportExportFormat fmt) async {
    try {
      final res = await _dio.post<List<int>>(
        ApiConstants.appTallerReporteExport(fmt.apiValue),
        data: qbe.toJson(),
        options: Options(responseType: ResponseType.bytes),
      );
      final bytes = res.data;
      if (bytes == null || bytes.isEmpty) throw Exception('Archivo vacío.');
      return Uint8List.fromList(bytes);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<ReportPlantilla> createReportPlantilla({
    required String nombre,
    required QbePayload qbe,
    String? descripcion,
  }) async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(
        ApiConstants.appTallerReportesPlantillas,
        data: {
          'nombre': nombre.trim(),
          'descripcion': descripcion?.trim() ?? '',
          'qbe_payload': qbe.toJson(),
        },
      );
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida.');
      return ReportPlantilla.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<void> deleteReportPlantilla(int id) async {
    try {
      await _dio.delete<void>(ApiConstants.appTallerReportePlantilla(id));
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<TallerSuscripcionInfo> fetchSuscripcion() async {
    try {
      final res = await _dio.get<Map<String, dynamic>>(ApiConstants.appTallerSuscripcion);
      final data = res.data;
      if (data == null) throw Exception('Respuesta vacía.');
      return TallerSuscripcionInfo.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<TallerBitacoraEntry>> listBitacora({int limit = 40}) async {
    try {
      final res = await _dio.get<List<dynamic>>(
        ApiConstants.appTallerBitacora,
        queryParameters: {'limit': limit},
      );
      return (res.data ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(TallerBitacoraEntry.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<List<TallerBackupEntry>> listBackups() async {
    try {
      final res = await _dio.get<List<dynamic>>(ApiConstants.appTallerBackups);
      return (res.data ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(TallerBackupEntry.fromJson)
          .toList();
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }

  Future<TallerBackupEntry> createBackup() async {
    try {
      final res = await _dio.post<Map<String, dynamic>>(ApiConstants.appTallerBackups);
      final data = res.data;
      if (data == null) throw Exception('Respuesta inválida.');
      return TallerBackupEntry.fromJson(data);
    } on DioException catch (e) {
      throw Exception(messageFromDio(e));
    }
  }
}
