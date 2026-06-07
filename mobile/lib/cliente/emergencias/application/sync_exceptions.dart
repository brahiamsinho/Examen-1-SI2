/// Sesión expirada durante sync — pausar cola hasta nuevo login (CU43).
final class SessionExpiredSyncException implements Exception {
  SessionExpiredSyncException([this.message = 'Sesión expirada']);

  final String message;

  @override
  String toString() => message;
}

/// Error de validación permanente (422) — no reintentar automáticamente.
final class PermanentSyncException implements Exception {
  PermanentSyncException(this.message);

  final String message;

  @override
  String toString() => message;
}
