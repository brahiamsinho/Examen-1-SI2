import '../../../core/utils/api_datetime.dart';

final class TallerDisponibilidad {
  const TallerDisponibilidad({
    required this.tallerId,
    required this.aceptaNuevasSolicitudes,
    required this.capacidadMaximaDiaria,
    required this.serviciosActivos,
    this.observacion,
    required this.updatedAt,
  });

  final int tallerId;
  final bool aceptaNuevasSolicitudes;
  final int capacidadMaximaDiaria;
  final int serviciosActivos;
  final String? observacion;
  final DateTime updatedAt;

  factory TallerDisponibilidad.fromJson(Map<String, dynamic> j) => TallerDisponibilidad(
        tallerId: j['taller_id'] as int,
        aceptaNuevasSolicitudes: j['acepta_nuevas_solicitudes'] as bool? ?? false,
        capacidadMaximaDiaria: j['capacidad_maxima_diaria'] as int? ?? 0,
        serviciosActivos: j['servicios_activos'] as int? ?? 0,
        observacion: j['observacion'] as String?,
        updatedAt: parseApiDateTime(j['updated_at']),
      );
}

final class ResumenComisiones {
  const ResumenComisiones({
    required this.totalRegistros,
    required this.totalServicios,
    required this.totalComision,
    required this.totalNeto,
  });

  final int totalRegistros;
  final String totalServicios;
  final String totalComision;
  final String totalNeto;

  factory ResumenComisiones.fromJson(Map<String, dynamic> j) => ResumenComisiones(
        totalRegistros: j['total_registros'] as int? ?? 0,
        totalServicios: (j['total_servicios'] ?? '0').toString(),
        totalComision: (j['total_comision'] ?? '0').toString(),
        totalNeto: (j['total_neto'] ?? '0').toString(),
      );
}

final class ComisionTaller {
  const ComisionTaller({
    required this.id,
    required this.solicitudId,
    required this.montoServicio,
    required this.montoComision,
    required this.montoTallerNeto,
    required this.estado,
    required this.calculadoAt,
  });

  final int id;
  final int solicitudId;
  final String montoServicio;
  final String montoComision;
  final String montoTallerNeto;
  final String estado;
  final DateTime calculadoAt;

  factory ComisionTaller.fromJson(Map<String, dynamic> j) => ComisionTaller(
        id: j['id'] as int,
        solicitudId: j['solicitud_id'] as int,
        montoServicio: (j['monto_servicio'] ?? '0').toString(),
        montoComision: (j['monto_comision'] ?? '0').toString(),
        montoTallerNeto: (j['monto_taller_neto'] ?? '0').toString(),
        estado: (j['estado'] ?? '').toString(),
        calculadoAt: parseApiDateTime(j['calculado_at']),
      );
}

final class HistorialAtencion {
  const HistorialAtencion({
    required this.solicitudId,
    this.bandejaId,
    required this.estado,
    required this.createdAt,
    this.finalizadaAt,
    required this.placa,
    required this.clienteNombre,
  });

  final int solicitudId;
  final int? bandejaId;
  final String estado;
  final DateTime createdAt;
  final DateTime? finalizadaAt;
  final String placa;
  final String clienteNombre;

  factory HistorialAtencion.fromJson(Map<String, dynamic> j) {
    final n = j['nombres'] as String? ?? '';
    final a = j['apellidos'] as String? ?? '';
    return HistorialAtencion(
      solicitudId: j['solicitud_id'] as int,
      bandejaId: j['bandeja_id'] as int?,
      estado: (j['estado'] ?? '').toString(),
      createdAt: parseApiDateTime(j['created_at']),
      finalizadaAt: j['finalizada_at'] != null ? parseApiDateTime(j['finalizada_at']) : null,
      placa: (j['placa'] ?? '').toString(),
      clienteNombre: '$n $a'.trim(),
    );
  }
}

final class ReporteTallerDashboard {
  const ReporteTallerDashboard({
    required this.bandejaPendientes,
    required this.resumenComisiones,
    required this.solicitudesPorEstado,
    this.analiticaOperacional,
  });

  final int bandejaPendientes;
  final ResumenComisiones resumenComisiones;
  final Map<String, int> solicitudesPorEstado;
  final OperationalKpis? analiticaOperacional;

  factory ReporteTallerDashboard.fromJson(Map<String, dynamic> j) {
    final raw = j['solicitudes_por_estado'];
    final map = <String, int>{};
    if (raw is Map) {
      raw.forEach((k, v) => map[k.toString()] = (v as num?)?.toInt() ?? 0);
    }
    final opRaw = j['analitica_operacional'];
    return ReporteTallerDashboard(
      bandejaPendientes: j['bandeja_pendientes'] as int? ?? 0,
      resumenComisiones: ResumenComisiones.fromJson(
        (j['resumen_comisiones'] as Map<String, dynamic>?) ?? const {},
      ),
      solicitudesPorEstado: map,
      analiticaOperacional: opRaw is Map<String, dynamic>
          ? OperationalKpis.fromJson(opRaw)
          : null,
    );
  }
}

final class OperationalKpis {
  const OperationalKpis({
    this.tiempoPromedioAsignacionMin,
    this.tiempoPromedioLlegadaMin,
    required this.incidentesPorTipo,
    required this.zonasMasIncidentes,
    required this.casosCancelados,
    required this.casosNoAtendidos,
    required this.sla,
  });

  final double? tiempoPromedioAsignacionMin;
  final double? tiempoPromedioLlegadaMin;
  final List<IncidentePorTipo> incidentesPorTipo;
  final List<ZonaIncidentes> zonasMasIncidentes;
  final int casosCancelados;
  final int casosNoAtendidos;
  final SlaCumplimiento sla;

  factory OperationalKpis.fromJson(Map<String, dynamic> j) {
    return OperationalKpis(
      tiempoPromedioAsignacionMin: (j['tiempo_promedio_asignacion_min'] as num?)?.toDouble(),
      tiempoPromedioLlegadaMin: (j['tiempo_promedio_llegada_min'] as num?)?.toDouble(),
      incidentesPorTipo: [
        for (final e in j['incidentes_por_tipo'] as List<dynamic>? ?? [])
          if (e is Map<String, dynamic>) IncidentePorTipo.fromJson(e),
      ],
      zonasMasIncidentes: [
        for (final e in j['zonas_mas_incidentes'] as List<dynamic>? ?? [])
          if (e is Map<String, dynamic>) ZonaIncidentes.fromJson(e),
      ],
      casosCancelados: j['casos_cancelados'] as int? ?? 0,
      casosNoAtendidos: j['casos_no_atendidos'] as int? ?? 0,
      sla: SlaCumplimiento.fromJson((j['sla'] as Map<String, dynamic>?) ?? const {}),
    );
  }
}

final class IncidentePorTipo {
  const IncidentePorTipo({required this.label, required this.total});

  final String label;
  final int total;

  factory IncidentePorTipo.fromJson(Map<String, dynamic> j) => IncidentePorTipo(
        label: (j['label'] ?? j['categoria'] ?? '—').toString(),
        total: j['total'] as int? ?? 0,
      );
}

final class ZonaIncidentes {
  const ZonaIncidentes({required this.zona, required this.total});

  final String zona;
  final int total;

  factory ZonaIncidentes.fromJson(Map<String, dynamic> j) => ZonaIncidentes(
        zona: (j['zona'] ?? '—').toString(),
        total: j['total'] as int? ?? 0,
      );
}

final class SlaCumplimiento {
  const SlaCumplimiento({
    required this.umbralMinutos,
    required this.serviciosEvaluados,
    required this.serviciosDentroSla,
    this.porcentajeCumplimiento,
  });

  final int umbralMinutos;
  final int serviciosEvaluados;
  final int serviciosDentroSla;
  final double? porcentajeCumplimiento;

  factory SlaCumplimiento.fromJson(Map<String, dynamic> j) => SlaCumplimiento(
        umbralMinutos: j['umbral_minutos'] as int? ?? 60,
        serviciosEvaluados: j['servicios_evaluados'] as int? ?? 0,
        serviciosDentroSla: j['servicios_dentro_sla'] as int? ?? 0,
        porcentajeCumplimiento: (j['porcentaje_cumplimiento'] as num?)?.toDouble(),
      );
}

String _formatMinutos(double? min) {
  if (min == null) return '—';
  if (min < 60) return '${min.round()} min';
  final h = min ~/ 60;
  final m = (min % 60).round();
  return m > 0 ? '$h h $m min' : '$h h';
}

String formatOperationalMinutos(double? min) => _formatMinutos(min);

final class ReportPlantilla {
  const ReportPlantilla({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.isSystemReport,
    this.qbePayload,
  });

  final int id;
  final String nombre;
  final String? descripcion;
  final bool isSystemReport;
  final QbePayload? qbePayload;

  factory ReportPlantilla.fromJson(Map<String, dynamic> j) {
    final qbeRaw = j['qbe_payload'];
    return ReportPlantilla(
      id: j['id'] as int,
      nombre: (j['nombre'] ?? j['name'] ?? 'Reporte').toString(),
      descripcion: () {
        final d = j['descripcion'] as String?;
        if (d == null || d.trim().isEmpty) return null;
        return d;
      }(),
      isSystemReport: j['is_system_report'] as bool? ?? false,
      qbePayload: qbeRaw is Map<String, dynamic> ? QbePayload.fromJson(qbeRaw) : null,
    );
  }
}

enum ReportExportFormat { excel, pdf, csv }

extension ReportExportFormatApi on ReportExportFormat {
  String get apiValue => name;

  String get fileExtension => switch (this) {
        ReportExportFormat.excel => 'xlsx',
        ReportExportFormat.pdf => 'pdf',
        ReportExportFormat.csv => 'csv',
      };
}

final class QbePayload {
  const QbePayload({
    required this.model,
    this.filters = const {},
    this.fields,
    this.orderBy = const [],
    this.aggregations = const [],
  });

  final String model;
  final Map<String, dynamic> filters;
  final List<String>? fields;
  final List<String> orderBy;
  final List<String> aggregations;

  factory QbePayload.fromJson(Map<String, dynamic> j) => QbePayload(
        model: (j['model'] ?? '').toString(),
        filters: Map<String, dynamic>.from(j['filters'] as Map? ?? const {}),
        fields: (j['fields'] as List<dynamic>?)?.map((e) => e.toString()).toList(),
        orderBy: (j['order_by'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? const [],
        aggregations:
            (j['aggregations'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? const [],
      );

  Map<String, dynamic> toJson() => {
        'model': model,
        'filters': filters,
        if (fields != null) 'fields': fields,
        'order_by': orderBy,
        if (aggregations.isNotEmpty) 'aggregations': aggregations,
      };
}

final class ReportMeta {
  const ReportMeta({
    required this.model,
    required this.totalRecords,
    required this.columns,
    this.truncated = false,
  });

  final String model;
  final int totalRecords;
  final List<String> columns;
  final bool truncated;

  factory ReportMeta.fromJson(Map<String, dynamic> j) => ReportMeta(
        model: (j['model'] ?? '').toString(),
        totalRecords: j['total_records'] as int? ?? 0,
        columns: (j['columns'] as List<dynamic>? ?? const []).map((c) => c.toString()).toList(),
        truncated: j['truncated'] as bool? ?? false,
      );
}

final class ReportExecuteResult {
  const ReportExecuteResult({
    required this.meta,
    required this.data,
  });

  final ReportMeta meta;
  final List<Map<String, dynamic>> data;

  int get totalRows => meta.totalRecords;
  List<String> get columns => meta.columns;

  factory ReportExecuteResult.fromJson(Map<String, dynamic> j) {
    final metaRaw = j['meta'];
    final meta = metaRaw is Map<String, dynamic>
        ? ReportMeta.fromJson(metaRaw)
        : ReportMeta(
            model: (j['model'] ?? '').toString(),
            totalRecords: j['total_rows'] as int? ?? 0,
            columns: (j['columns'] as List<dynamic>? ?? const []).map((c) => c.toString()).toList(),
          );
    final rowsRaw = j['data'] as List<dynamic>? ?? const [];
    final data = rowsRaw.whereType<Map>().map((r) => Map<String, dynamic>.from(r)).toList();
    return ReportExecuteResult(meta: meta, data: data);
  }
}

final class ReportRunResult {
  const ReportRunResult({required this.qbe, required this.report});

  final QbePayload qbe;
  final ReportExecuteResult report;

  factory ReportRunResult.fromJson(Map<String, dynamic> j) {
    final qbeRaw = j['qbe'];
    final reportRaw = j['report'];
    if (qbeRaw is! Map<String, dynamic> || reportRaw is! Map<String, dynamic>) {
      throw FormatException('Respuesta run inválida.');
    }
    return ReportRunResult(
      qbe: QbePayload.fromJson(qbeRaw),
      report: ReportExecuteResult.fromJson(reportRaw),
    );
  }
}

final class ReportNlQueryResult {
  const ReportNlQueryResult({
    required this.qbe,
    required this.interpretation,
    required this.exportFormats,
  });

  final QbePayload qbe;
  final String interpretation;
  final List<ReportExportFormat> exportFormats;

  factory ReportNlQueryResult.fromJson(Map<String, dynamic> j) {
    final formatsRaw = j['export_formats'] as List<dynamic>? ?? const [];
    final formats = <ReportExportFormat>[];
    for (final f in formatsRaw) {
      final fmt = switch (f.toString().toLowerCase()) {
        'excel' => ReportExportFormat.excel,
        'pdf' => ReportExportFormat.pdf,
        'csv' => ReportExportFormat.csv,
        _ => null,
      };
      if (fmt != null) formats.add(fmt);
    }
    final qbeRaw = j['qbe'];
    if (qbeRaw is! Map<String, dynamic>) throw FormatException('QBE inválido.');
    return ReportNlQueryResult(
      qbe: QbePayload.fromJson(qbeRaw),
      interpretation: (j['interpretation'] ?? '').toString(),
      exportFormats: formats,
    );
  }
}

final class ReportVoiceTranscribeResult {
  const ReportVoiceTranscribeResult({
    required this.transcripcion,
    required this.confianza,
    required this.provider,
  });

  final String transcripcion;
  final double confianza;
  final String provider;

  factory ReportVoiceTranscribeResult.fromJson(Map<String, dynamic> j) => ReportVoiceTranscribeResult(
        transcripcion: (j['transcripcion'] ?? '').toString(),
        confianza: (j['confianza'] as num?)?.toDouble() ?? 0,
        provider: (j['provider'] ?? 'whisper').toString(),
      );
}

final class TallerSuscripcionInfo {
  const TallerSuscripcionInfo({
    required this.tenantNombre,
    required this.planName,
    required this.subscriptionStatus,
    this.subscriptionEndsAt,
    required this.stripeEnabled,
  });

  final String tenantNombre;
  final String planName;
  final String subscriptionStatus;
  final DateTime? subscriptionEndsAt;
  final bool stripeEnabled;

  factory TallerSuscripcionInfo.fromJson(Map<String, dynamic> j) => TallerSuscripcionInfo(
        tenantNombre: (j['tenant_nombre'] ?? '').toString(),
        planName: (j['current_plan_name'] ?? j['current_plan_slug'] ?? '').toString(),
        subscriptionStatus: (j['subscription_status'] ?? '').toString(),
        subscriptionEndsAt: j['subscription_ends_at'] != null
            ? parseApiDateTime(j['subscription_ends_at'])
            : null,
        stripeEnabled: j['stripe_enabled'] as bool? ?? false,
      );
}

final class TallerBitacoraEntry {
  const TallerBitacoraEntry({
    required this.id,
    required this.modulo,
    required this.entidad,
    required this.accion,
    this.descripcion,
    this.usuarioNombre,
    required this.createdAt,
  });

  final int id;
  final String modulo;
  final String entidad;
  final String accion;
  final String? descripcion;
  final String? usuarioNombre;
  final DateTime createdAt;

  factory TallerBitacoraEntry.fromJson(Map<String, dynamic> j) => TallerBitacoraEntry(
        id: j['id'] as int,
        modulo: (j['modulo'] ?? '').toString(),
        entidad: (j['entidad'] ?? '').toString(),
        accion: (j['accion'] ?? '').toString(),
        descripcion: j['descripcion'] as String?,
        usuarioNombre: j['usuario_nombre'] as String?,
        createdAt: parseApiDateTime(j['created_at']),
      );
}

final class TallerBackupEntry {
  const TallerBackupEntry({
    required this.id,
    required this.archivo,
    required this.estado,
    required this.creadoEn,
    this.tamanoMb,
  });

  final int id;
  final String archivo;
  final String estado;
  final DateTime creadoEn;
  final double? tamanoMb;

  factory TallerBackupEntry.fromJson(Map<String, dynamic> j) => TallerBackupEntry(
        id: j['id'] as int,
        archivo: (j['archivo'] ?? '').toString(),
        estado: (j['estado'] ?? '').toString(),
        creadoEn: parseApiDateTime(j['creado_en']),
        tamanoMb: (j['tamano_mb'] as num?)?.toDouble(),
      );
}
