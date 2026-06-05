// CU45 — borrador local de solicitud; CU43 — cola de sincronización.

enum SolicitudDraftStatus {
  building,
  readyToSync,
  syncing,
  failed,
  failedPermanent,
}

extension SolicitudDraftStatusX on SolicitudDraftStatus {
  String get label => switch (this) {
        SolicitudDraftStatus.building => 'En borrador',
        SolicitudDraftStatus.readyToSync => 'Pendiente de envío',
        SolicitudDraftStatus.syncing => 'Enviando…',
        SolicitudDraftStatus.failed => 'Reintentar',
        SolicitudDraftStatus.failedPermanent => 'Error permanente',
      };

  String get apiValue => name;

  static SolicitudDraftStatus fromApi(String? raw) {
    if (raw == null || raw.isEmpty) return SolicitudDraftStatus.building;
    return SolicitudDraftStatus.values.firstWhere(
      (e) => e.name == raw,
      orElse: () => SolicitudDraftStatus.building,
    );
  }
}

final class SolicitudDraft {
  const SolicitudDraft({
    required this.clientRequestId,
    required this.vehiculoId,
    required this.createdAt,
    required this.updatedAt,
    this.descripcionInicial,
    this.latitud,
    this.longitud,
    this.precisionMetros,
    this.fotoPath,
    this.fotoMime,
    this.fotoNombre,
    this.audioPath,
    this.textoAdicional,
    this.status = SolicitudDraftStatus.building,
    this.retryCount = 0,
    this.lastError,
    this.syncedSolicitudId,
  });

  final String clientRequestId;
  final int vehiculoId;
  final String? descripcionInicial;
  final double? latitud;
  final double? longitud;
  final double? precisionMetros;
  final String? fotoPath;
  final String? fotoMime;
  final String? fotoNombre;
  final String? audioPath;
  final String? textoAdicional;
  final SolicitudDraftStatus status;
  final int retryCount;
  final String? lastError;
  final int? syncedSolicitudId;
  final DateTime createdAt;
  final DateTime updatedAt;

  bool get isPendingSync =>
      status == SolicitudDraftStatus.readyToSync || status == SolicitudDraftStatus.failed;

  SolicitudDraft copyWith({
    String? descripcionInicial,
    double? latitud,
    double? longitud,
    double? precisionMetros,
    String? fotoPath,
    String? fotoMime,
    String? fotoNombre,
    String? audioPath,
    String? textoAdicional,
    SolicitudDraftStatus? status,
    int? retryCount,
    String? lastError,
    int? syncedSolicitudId,
    DateTime? updatedAt,
  }) {
    return SolicitudDraft(
      clientRequestId: clientRequestId,
      vehiculoId: vehiculoId,
      descripcionInicial: descripcionInicial ?? this.descripcionInicial,
      latitud: latitud ?? this.latitud,
      longitud: longitud ?? this.longitud,
      precisionMetros: precisionMetros ?? this.precisionMetros,
      fotoPath: fotoPath ?? this.fotoPath,
      fotoMime: fotoMime ?? this.fotoMime,
      fotoNombre: fotoNombre ?? this.fotoNombre,
      audioPath: audioPath ?? this.audioPath,
      textoAdicional: textoAdicional ?? this.textoAdicional,
      status: status ?? this.status,
      retryCount: retryCount ?? this.retryCount,
      lastError: lastError,
      syncedSolicitudId: syncedSolicitudId ?? this.syncedSolicitudId,
      createdAt: createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'client_request_id': clientRequestId,
        'vehiculo_id': vehiculoId,
        if (descripcionInicial != null) 'descripcion_inicial': descripcionInicial,
        if (latitud != null) 'latitud': latitud,
        if (longitud != null) 'longitud': longitud,
        if (precisionMetros != null) 'precision_metros': precisionMetros,
        if (fotoPath != null) 'foto_path': fotoPath,
        if (fotoMime != null) 'foto_mime': fotoMime,
        if (fotoNombre != null) 'foto_nombre': fotoNombre,
        if (audioPath != null) 'audio_path': audioPath,
        if (textoAdicional != null) 'texto_adicional': textoAdicional,
        'status': status.apiValue,
        'retry_count': retryCount,
        if (lastError != null) 'last_error': lastError,
        if (syncedSolicitudId != null) 'synced_solicitud_id': syncedSolicitudId,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
      };

  factory SolicitudDraft.fromJson(Map<String, dynamic> json) {
    return SolicitudDraft(
      clientRequestId: json['client_request_id'] as String,
      vehiculoId: json['vehiculo_id'] as int,
      descripcionInicial: json['descripcion_inicial'] as String?,
      latitud: (json['latitud'] as num?)?.toDouble(),
      longitud: (json['longitud'] as num?)?.toDouble(),
      precisionMetros: (json['precision_metros'] as num?)?.toDouble(),
      fotoPath: json['foto_path'] as String?,
      fotoMime: json['foto_mime'] as String?,
      fotoNombre: json['foto_nombre'] as String?,
      audioPath: json['audio_path'] as String?,
      textoAdicional: json['texto_adicional'] as String?,
      status: SolicitudDraftStatusX.fromApi(json['status'] as String?),
      retryCount: json['retry_count'] as int? ?? 0,
      lastError: json['last_error'] as String?,
      syncedSolicitudId: json['synced_solicitud_id'] as int?,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }
}

final class SyncBatchResult {
  const SyncBatchResult({
    required this.sent,
    required this.failed,
    required this.skippedAuth,
    this.lastMessage,
  });

  final int sent;
  final int failed;
  final bool skippedAuth;
  final String? lastMessage;
}
