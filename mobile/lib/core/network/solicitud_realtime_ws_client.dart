// WebSocket por solicitud — eventos en tiempo real desde el backend.
import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../config/app_env.dart';

class RealtimeWsEvent {
  const RealtimeWsEvent({
    required this.tipo,
    required this.solicitudId,
    this.payload = const {},
    this.occurredAt,
  });

  final String tipo;
  final int solicitudId;
  final Map<String, dynamic> payload;
  final DateTime? occurredAt;

  factory RealtimeWsEvent.fromJson(Map<String, dynamic> json) {
    DateTime? occurred;
    final raw = json['occurred_at'];
    if (raw is String) occurred = DateTime.tryParse(raw);
    return RealtimeWsEvent(
      tipo: json['tipo']?.toString() ?? 'desconocido',
      solicitudId: (json['solicitud_id'] as num?)?.toInt() ?? 0,
      payload: json['payload'] is Map
          ? Map<String, dynamic>.from(json['payload'] as Map)
          : const {},
      occurredAt: occurred,
    );
  }
}

/// Cliente WS con reconexión simple. Cierra con [dispose].
class SolicitudRealtimeWsClient {
  SolicitudRealtimeWsClient({
    required this.solicitudId,
    required this.accessToken,
  });

  final int solicitudId;
  final String accessToken;

  final _controller = StreamController<RealtimeWsEvent>.broadcast();
  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _sub;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  var _disposed = false;
  var _attempt = 0;

  Stream<RealtimeWsEvent> get events => _controller.stream;

  void connect() {
    if (_disposed) return;
    _connectInternal();
  }

  void dispose() {
    _disposed = true;
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _sub?.cancel();
    _channel?.sink.close();
    _controller.close();
  }

  String _wsUrl() {
    final httpBase = AppEnv.apiBaseUrl;
    final wsBase = httpBase.replaceFirst(RegExp(r'^http'), 'ws');
    final token = Uri.encodeComponent(accessToken);
    return '$wsBase/ws/solicitudes/$solicitudId?token=$token';
  }

  void _connectInternal() {
    if (_disposed) return;
    _sub?.cancel();
    _channel?.sink.close();

    try {
      _channel = WebSocketChannel.connect(Uri.parse(_wsUrl()));
    } catch (e) {
      _scheduleReconnect();
      return;
    }

    _attempt = 0;
    _sub = _channel!.stream.listen(
      (raw) {
        if (raw is! String) return;
        try {
          final map = jsonDecode(raw) as Map<String, dynamic>;
          final ev = RealtimeWsEvent.fromJson(map);
          if (ev.tipo != 'pong') _controller.add(ev);
        } catch (_) {
          /* ignore */
        }
      },
      onError: (_) => _scheduleReconnect(),
      onDone: () => _scheduleReconnect(),
      cancelOnError: true,
    );

    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 45), (_) {
      if (_disposed) return;
      try {
        _channel?.sink.add('ping');
      } catch (_) {
        _scheduleReconnect();
      }
    });
  }

  void _scheduleReconnect() {
    if (_disposed) return;
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _attempt = (_attempt + 1).clamp(1, 6);
    final delay = Duration(seconds: _attempt * 2);
    _reconnectTimer = Timer(delay, _connectInternal);
  }
}
