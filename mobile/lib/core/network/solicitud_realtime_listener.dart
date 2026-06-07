import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'solicitud_realtime_providers.dart';
import 'solicitud_realtime_ws_client.dart';

/// Escucha WS de varias solicitudes activas y ejecuta [onEvent] (p. ej. invalidar lista).
class ClienteMultiSolicitudRealtimeListener extends ConsumerWidget {
  const ClienteMultiSolicitudRealtimeListener({
    super.key,
    required this.solicitudIds,
    required this.onEvent,
    required this.child,
    this.maxConnections = 5,
  });

  final List<int> solicitudIds;
  final void Function(RealtimeWsEvent event) onEvent;
  final Widget child;
  final int maxConnections;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    for (final id in solicitudIds.take(maxConnections)) {
      ref.listen(solicitudRealtimeEventsProvider(id), (prev, next) {
        next.whenData(onEvent);
      });
    }
    return child;
  }
}
