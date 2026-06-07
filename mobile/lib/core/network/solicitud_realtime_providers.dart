import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../cliente/application/cliente_injection.dart';
import '../../core/network/tecnico_api_client.dart';
import '../../core/network/taller_api_client.dart';
import 'solicitud_realtime_ws_client.dart';

Stream<RealtimeWsEvent> _solicitudWsStream({
  required int solicitudId,
  required Future<String?> Function() readToken,
  required void Function(SolicitudRealtimeWsClient client) onDispose,
}) async* {
  final token = await readToken();
  if (token == null || token.isEmpty) {
    throw StateError('Sin token para WebSocket');
  }
  final client = SolicitudRealtimeWsClient(
    solicitudId: solicitudId,
    accessToken: token,
  );
  onDispose(client);
  client.connect();
  yield* client.events;
}

/// Escucha eventos WS de una solicitud (cliente autenticado).
final solicitudRealtimeEventsProvider = StreamProvider.autoDispose
    .family<RealtimeWsEvent, int>((ref, solicitudId) {
  SolicitudRealtimeWsClient? client;
  ref.onDispose(() => client?.dispose());
  return _solicitudWsStream(
    solicitudId: solicitudId,
    readToken: () => ref.read(authRepositoryProvider).readAccessToken(),
    onDispose: (c) => client = c,
  );
});

/// Escucha eventos WS (app técnico).
final tecnicoSolicitudRealtimeEventsProvider = StreamProvider.autoDispose
    .family<RealtimeWsEvent, int>((ref, solicitudId) {
  SolicitudRealtimeWsClient? client;
  ref.onDispose(() => client?.dispose());
  return _solicitudWsStream(
    solicitudId: solicitudId,
    readToken: () => TecnicoApiClient().readAccessToken(),
    onDispose: (c) => client = c,
  );
});

/// Escucha eventos WS (app taller responsable).
final tallerSolicitudRealtimeEventsProvider = StreamProvider.autoDispose
    .family<RealtimeWsEvent, int>((ref, solicitudId) {
  SolicitudRealtimeWsClient? client;
  ref.onDispose(() => client?.dispose());
  return _solicitudWsStream(
    solicitudId: solicitudId,
    readToken: () => TallerApiClient().readAccessToken(),
    onDispose: (c) => client = c,
  );
});

bool realtimeEventAffectsSeguimiento(String tipo) {
  return tipo == 'estado_incidente' ||
      tipo == 'tecnico_asignado' ||
      tipo == 'bandeja_actualizada' ||
      tipo == 'seguimiento_actualizado' ||
      tipo == 'taller_seleccionado' ||
      tipo == 'pago_confirmado';
}

bool realtimeEventAffectsUbicacion(String tipo) => tipo == 'ubicacion_tecnico';

bool realtimeEventAffectsChat(String tipo) => tipo == 'mensaje_nuevo';

bool realtimeEventAffectsTallerOperacion(String tipo) {
  return realtimeEventAffectsSeguimiento(tipo) ||
      realtimeEventAffectsChat(tipo) ||
      realtimeEventAffectsUbicacion(tipo);
}

bool realtimeEventAffectsTecnicoServicio(String tipo) {
  return tipo == 'estado_incidente' ||
      tipo == 'mensaje_nuevo' ||
      tipo == 'ubicacion_tecnico' ||
      tipo == 'seguimiento_actualizado';
}
