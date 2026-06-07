import 'dart:io';

import 'package:dio/dio.dart';

import '../data/emergencias_repository.dart';
import '../data/solicitud_draft_repo.dart';
import '../domain/solicitud_draft.dart';
import 'sync_exceptions.dart';

/// Envía un borrador completo al API en orden (CU43 replay con client_request_id).
final class SyncPendientes {
  SyncPendientes({
    required EmergenciasRepository emergenciasRepo,
    required SolicitudDraftRepo draftRepo,
  })  : _emergenciasRepo = emergenciasRepo,
        _draftRepo = draftRepo;

  final EmergenciasRepository _emergenciasRepo;
  final SolicitudDraftRepo _draftRepo;

  Future<int> syncDraft(SolicitudDraft draft) async {
    final now = DateTime.now().toUtc();
    var working = draft.copyWith(
      status: SolicitudDraftStatus.syncing,
      lastError: null,
      updatedAt: now,
    );
    await _draftRepo.save(working);

    try {
      final ubicacionInicial = (working.latitud != null && working.longitud != null)
          ? {
              'latitud': working.latitud,
              'longitud': working.longitud,
              if (working.precisionMetros != null) 'precision_metros': working.precisionMetros,
              'es_actual': true,
            }
          : null;

      var detail = await _emergenciasRepo.create(
        vehiculoId: working.vehiculoId,
        descripcionTexto: working.descripcionInicial,
        ubicacionInicial: ubicacionInicial,
        clientRequestId: working.clientRequestId,
      );
      final sid = detail.id;

      if (ubicacionInicial == null &&
          working.latitud != null &&
          working.longitud != null) {
        detail = await _emergenciasRepo.postUbicacion(
          sid,
          latitud: working.latitud!,
          longitud: working.longitud!,
          precisionMetros: working.precisionMetros,
          esActual: true,
        );
      }

      if (working.fotoPath != null && working.fotoPath!.isNotEmpty) {
        final f = File(working.fotoPath!);
        if (await f.exists()) {
          detail = await _emergenciasRepo.postEvidenciaArchivo(
            sid,
            tipoApi: 'FOTO',
            filePath: working.fotoPath!,
            filename: working.fotoNombre?.isNotEmpty == true ? working.fotoNombre! : 'foto.jpg',
            mimeType: working.fotoMime,
          );
        }
      }

      if (working.audioPath != null && working.audioPath!.isNotEmpty) {
        final a = File(working.audioPath!);
        if (await a.exists()) {
          detail = await _emergenciasRepo.postEvidenciaArchivo(
            sid,
            tipoApi: 'AUDIO',
            filePath: working.audioPath!,
            filename: 'grabacion.m4a',
            mimeType: 'audio/mp4',
          );
        }
      }

      final texto = working.textoAdicional?.trim();
      final inicial = working.descripcionInicial?.trim();
      if (texto != null && texto.isNotEmpty && texto != inicial) {
        detail = await _emergenciasRepo.patchTexto(sid, descripcionTexto: texto);
      }

      await _draftRepo.delete(working.clientRequestId);
      return detail.id;
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw SessionExpiredSyncException();
      }
      if (e.response?.statusCode == 422) {
        final msg = e.response?.data?.toString() ?? 'Datos inválidos';
        await _draftRepo.save(
          working.copyWith(
            status: SolicitudDraftStatus.failedPermanent,
            lastError: msg,
            updatedAt: DateTime.now().toUtc(),
          ),
        );
        throw PermanentSyncException(msg);
      }
      final retries = working.retryCount + 1;
      await _draftRepo.save(
        working.copyWith(
          status: SolicitudDraftStatus.failed,
          retryCount: retries,
          lastError: e.message ?? e.type.name,
          updatedAt: DateTime.now().toUtc(),
        ),
      );
      rethrow;
    } catch (e) {
      if (e is SessionExpiredSyncException || e is PermanentSyncException) rethrow;
      final retries = working.retryCount + 1;
      await _draftRepo.save(
        working.copyWith(
          status: SolicitudDraftStatus.failed,
          retryCount: retries,
          lastError: e.toString(),
          updatedAt: DateTime.now().toUtc(),
        ),
      );
      rethrow;
    }
  }
}
