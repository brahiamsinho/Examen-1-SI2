import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:record/record.dart';
import 'package:share_plus/share_plus.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../application/taller_injection.dart';
import '../../domain/models/taller_modulos_models.dart';
import 'taller_module_ui.dart';

class TallerReportesScreen extends ConsumerStatefulWidget {
  const TallerReportesScreen({super.key});

  @override
  ConsumerState<TallerReportesScreen> createState() => _TallerReportesScreenState();
}

class _TallerReportesScreenState extends ConsumerState<TallerReportesScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  final _nlQuery = TextEditingController();
  final _saveName = TextEditingController();
  final _recorder = AudioRecorder();

  bool _loadingReport = false;
  bool _recording = false;
  ReportExportFormat? _exporting;
  int? _runningTemplateId;

  String? _error;
  String? _success;
  String _interpretation = '';
  QbePayload? _currentQbe;
  ReportExecuteResult? _report;
  List<ReportExportFormat> _pendingExports = const [];

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabs.dispose();
    _nlQuery.dispose();
    _saveName.dispose();
    _recorder.dispose();
    super.dispose();
  }

  void _setFeedback({String? error, String? success}) {
    setState(() {
      _error = error;
      _success = success;
    });
  }

  Future<void> _interpretAndRun({bool autoExport = false}) async {
    final q = _nlQuery.text.trim();
    if (q.isEmpty) {
      _setFeedback(error: 'Escribí o dictá qué reporte necesitás.');
      return;
    }
    setState(() {
      _loadingReport = true;
      _error = null;
      _success = null;
    });
    try {
      final nl = await ref.read(tallerRepositoryProvider).nlReportQuery(q);
      setState(() {
        _interpretation = nl.interpretation;
        _currentQbe = nl.qbe;
        _pendingExports = nl.exportFormats;
      });
      await _runQbe(nl.qbe, autoExport: autoExport || nl.exportFormats.isNotEmpty);
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loadingReport = false);
    }
  }

  Future<void> _runQbe(QbePayload qbe, {bool autoExport = false}) async {
    try {
      final report = await ref.read(tallerRepositoryProvider).executeReportQbe(qbe);
      if (!mounted) return;
      setState(() {
        _report = report;
        _currentQbe = qbe;
        _success =
            'Vista previa lista (${report.meta.totalRecords} registros${report.meta.truncated ? ', máx. 500' : ''}).';
      });
      if (autoExport && _pendingExports.isNotEmpty) {
        for (final fmt in _pendingExports) {
          await _export(fmt, qbe: qbe);
        }
      }
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _runTemplate(ReportPlantilla t) async {
    setState(() {
      _runningTemplateId = t.id;
      _loadingReport = true;
      _error = null;
      _success = null;
    });
    try {
      final result = await ref.read(tallerRepositoryProvider).runReportPlantilla(t.id);
      if (!mounted) return;
      setState(() {
        _currentQbe = result.qbe;
        _report = result.report;
        _interpretation = 'Plantilla: ${t.nombre}';
        _success = 'Reporte ejecutado (${result.report.meta.totalRecords} registros).';
        _tabs.index = 0;
      });
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) {
        setState(() {
          _loadingReport = false;
          _runningTemplateId = null;
        });
      }
    }
  }

  Future<void> _deleteTemplate(ReportPlantilla t) async {
    if (t.isSystemReport) return;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar plantilla'),
        content: Text('¿Eliminar "${t.nombre}"?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Eliminar')),
        ],
      ),
    );
    if (ok != true) return;
    try {
      await ref.read(tallerRepositoryProvider).deleteReportPlantilla(t.id);
      ref.invalidate(tallerReportPlantillasProvider);
      _setFeedback(success: 'Plantilla eliminada.');
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _saveTemplate() async {
    final qbe = _currentQbe;
    if (qbe == null) {
      _setFeedback(error: 'Ejecutá un reporte antes de guardarlo.');
      return;
    }
    final nombre = _saveName.text.trim().isNotEmpty ? _saveName.text.trim() : 'Reporte ${qbe.model}';
    try {
      await ref.read(tallerRepositoryProvider).createReportPlantilla(
            nombre: nombre,
            qbe: qbe,
            descripcion: _interpretation.isNotEmpty ? _interpretation : _nlQuery.text.trim(),
          );
      ref.invalidate(tallerReportPlantillasProvider);
      _saveName.clear();
      _setFeedback(success: 'Plantilla guardada.');
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    }
  }

  Future<void> _toggleVoice() async {
    if (_recording) {
      await _stopVoiceRecording();
      return;
    }
    final mic = await Permission.microphone.request();
    if (!mic.isGranted && mounted) {
      _setFeedback(error: 'Se necesita permiso de micrófono.');
      return;
    }
    if (!await _recorder.hasPermission()) {
      _setFeedback(error: 'No hay permiso para grabar audio.');
      return;
    }
    final dir = await getTemporaryDirectory();
    final path = '${dir.path}/reporte_voz_${DateTime.now().millisecondsSinceEpoch}.m4a';
    await _recorder.start(const RecordConfig(encoder: AudioEncoder.aacLc), path: path);
    setState(() {
      _recording = true;
      _error = null;
      _success = 'Grabando… tocá micrófono otra vez para transcribir.';
    });
  }

  Future<void> _stopVoiceRecording() async {
    final path = await _recorder.stop();
    setState(() => _recording = false);
    if (path == null || path.isEmpty) {
      _setFeedback(error: 'No se captó audio.');
      return;
    }
    setState(() {
      _loadingReport = true;
      _error = null;
      _success = null;
    });
    try {
      final voice = await ref.read(tallerRepositoryProvider).voiceReportQuery(filePath: path);
      if (!mounted) return;
      setState(() {
        _nlQuery.text = voice.transcripcion;
        _interpretation = '';
        _report = null;
        _currentQbe = null;
      });
      final via = voice.provider == 'gemini' ? 'Gemini' : 'Whisper';
      _setFeedback(success: 'Transcripción ($via): revisá el texto y tocá «Interpretar y ejecutar».');
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loadingReport = false);
    }
  }

  Future<void> _export(ReportExportFormat fmt, {QbePayload? qbe}) async {
    final payload = qbe ?? _currentQbe;
    if (payload == null) {
      _setFeedback(error: 'Primero ejecutá un reporte.');
      return;
    }
    setState(() => _exporting = fmt);
    try {
      final bytes = await ref.read(tallerRepositoryProvider).exportReportQbe(payload, fmt);
      final dir = await getTemporaryDirectory();
      final slug = payload.model.toLowerCase().replaceAll(RegExp(r'[^a-z0-9_-]+'), '-');
      final filename = 'reporte-${slug.isEmpty ? 'datos' : slug}.${fmt.fileExtension}';
      final saved = '${dir.path}/$filename';
      final mimeType = switch (fmt) {
        ReportExportFormat.excel =>
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        ReportExportFormat.pdf => 'application/pdf',
        ReportExportFormat.csv => 'text/csv',
      };
      await File(saved).writeAsBytes(bytes, flush: true);
      await Share.shareXFiles(
        [XFile(saved, mimeType: mimeType, name: filename)],
        text: 'Reporte ${fmt.name.toUpperCase()}',
      );
      _setFeedback(success: 'Export ${fmt.name.toUpperCase()} listo para compartir.');
    } catch (e) {
      _setFeedback(error: e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _exporting = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final dashAsync = ref.watch(tallerReporteDashboardProvider);
    final plantillasAsync = ref.watch(tallerReportPlantillasProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Reportes'),
        leading: BackButton(onPressed: () => context.pop()),
        bottom: TabBar(
          controller: _tabs,
          tabs: const [
            Tab(text: 'Consulta'),
            Tab(text: 'Plantillas'),
            Tab(text: 'Dashboard'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabs,
        children: [
          _ConsultaTab(
            nlQuery: _nlQuery,
            saveName: _saveName,
            loadingReport: _loadingReport,
            recording: _recording,
            exporting: _exporting,
            error: _error,
            success: _success,
            interpretation: _interpretation,
            report: _report,
            onInterpret: _interpretAndRun,
            onVoice: _toggleVoice,
            onExport: _export,
            onSaveTemplate: _saveTemplate,
          ),
          _PlantillasTab(
            async: plantillasAsync,
            runningId: _runningTemplateId,
            loading: _loadingReport,
            onRun: _runTemplate,
            onDelete: _deleteTemplate,
            onRefresh: () => ref.invalidate(tallerReportPlantillasProvider),
          ),
          _DashboardTab(
            async: dashAsync,
            onRefresh: () => ref.invalidate(tallerReporteDashboardProvider),
          ),
        ],
      ),
    );
  }
}

class _ConsultaTab extends StatelessWidget {
  const _ConsultaTab({
    required this.nlQuery,
    required this.saveName,
    required this.loadingReport,
    required this.recording,
    required this.exporting,
    required this.error,
    required this.success,
    required this.interpretation,
    required this.report,
    required this.onInterpret,
    required this.onVoice,
    required this.onExport,
    required this.onSaveTemplate,
  });

  final TextEditingController nlQuery;
  final TextEditingController saveName;
  final bool loadingReport;
  final bool recording;
  final ReportExportFormat? exporting;
  final String? error;
  final String? success;
  final String interpretation;
  final ReportExecuteResult? report;
  final VoidCallback onInterpret;
  final VoidCallback onVoice;
  final Future<void> Function(ReportExportFormat fmt) onExport;
  final VoidCallback onSaveTemplate;

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'Pedí un reporte por voz o texto. Ej.: «comisiones pendientes de este mes en excel».',
          style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant, height: 1.4),
        ),
        const SizedBox(height: 16),
        if (error != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        if (success != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(success!, style: TextStyle(color: Theme.of(context).colorScheme.primary)),
          ),
        TallerModuleCard(
          title: 'Consulta por voz o texto',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ShadInput(
                controller: nlQuery,
                placeholder: const Text('Ej.: solicitudes finalizadas de este mes en excel'),
                maxLines: 3,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: ShadButton(
                      onPressed: loadingReport ? null : onInterpret,
                      child: Text(loadingReport ? 'Procesando…' : 'Interpretar y ejecutar'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  ShadButton.outline(
                    onPressed: loadingReport ? null : onVoice,
                    child: Icon(recording ? Icons.stop_rounded : Icons.mic_rounded),
                  ),
                ],
              ),
              if (interpretation.isNotEmpty) ...[
                const SizedBox(height: 12),
                Text(interpretation, style: const TextStyle(fontSize: 13, height: 1.35)),
              ],
            ],
          ),
        ),
        if (report != null) ...[
          const SizedBox(height: 20),
          TallerModuleCard(
            title: 'Vista previa',
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  '${report!.meta.totalRecords} registros'
                  '${report!.meta.truncated ? ' (vista limitada a 500)' : ''}',
                ),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: ReportExportFormat.values
                      .map(
                        (fmt) => OutlinedButton(
                          onPressed: exporting == fmt ? null : () => onExport(fmt),
                          child: Text(
                            exporting == fmt ? '${fmt.name.toUpperCase()}…' : fmt.name.toUpperCase(),
                          ),
                        ),
                      )
                      .toList(),
                ),
                const SizedBox(height: 12),
                _ReportPreviewTable(report: report!),
                const SizedBox(height: 12),
                ShadInput(
                  controller: saveName,
                  placeholder: const Text('Nombre para guardar plantilla (opcional)'),
                ),
                const SizedBox(height: 8),
                ShadButton.outline(
                  width: double.infinity,
                  onPressed: onSaveTemplate,
                  child: const Text('Guardar plantilla'),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

class _ReportPreviewTable extends StatelessWidget {
  const _ReportPreviewTable({required this.report});

  final ReportExecuteResult report;

  @override
  Widget build(BuildContext context) {
    final cols = report.columns;
    if (cols.isEmpty) return const Text('Sin columnas.');
    if (report.data.isEmpty) return const Text('Sin registros.');

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        headingRowHeight: 36,
        dataRowMinHeight: 32,
        dataRowMaxHeight: 48,
        columns: cols.map((c) => DataColumn(label: Text(c, style: const TextStyle(fontSize: 12)))).toList(),
        rows: report.data
            .take(50)
            .map(
              (row) => DataRow(
                cells: cols
                    .map(
                      (c) => DataCell(
                        Text('${row[c] ?? '—'}', style: const TextStyle(fontSize: 12)),
                      ),
                    )
                    .toList(),
              ),
            )
            .toList(),
      ),
    );
  }
}

class _PlantillasTab extends StatelessWidget {
  const _PlantillasTab({
    required this.async,
    required this.runningId,
    required this.loading,
    required this.onRun,
    required this.onDelete,
    required this.onRefresh,
  });

  final AsyncValue<List<ReportPlantilla>> async;
  final int? runningId;
  final bool loading;
  final Future<void> Function(ReportPlantilla) onRun;
  final Future<void> Function(ReportPlantilla) onDelete;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => TallerModuleError(
        message: e.toString().replaceFirst('Exception: ', ''),
        onRetry: onRefresh,
      ),
      data: (list) => RefreshIndicator(
        onRefresh: () async => onRefresh(),
        child: list.isEmpty
            ? ListView(
                children: const [
                  SizedBox(height: 80),
                  Center(child: Text('Sin plantillas. Creá una desde la pestaña Consulta.')),
                ],
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: list.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, i) {
                  final t = list[i];
                  final busy = loading && runningId == t.id;
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Text(t.nombre, style: const TextStyle(fontWeight: FontWeight.w600)),
                              ),
                              if (t.isSystemReport)
                                Chip(
                                  label: const Text('Sistema', style: TextStyle(fontSize: 11)),
                                  visualDensity: VisualDensity.compact,
                                ),
                            ],
                          ),
                          if (t.descripcion != null) ...[
                            const SizedBox(height: 4),
                            Text(t.descripcion!, style: const TextStyle(fontSize: 13, height: 1.35)),
                          ],
                          const SizedBox(height: 10),
                          Row(
                            children: [
                              FilledButton.icon(
                                onPressed: busy ? null : () => onRun(t),
                                icon: busy
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.play_arrow_rounded, size: 18),
                                label: const Text('Ejecutar'),
                              ),
                              if (!t.isSystemReport) ...[
                                const SizedBox(width: 8),
                                OutlinedButton(
                                  onPressed: () => onDelete(t),
                                  child: const Text('Eliminar'),
                                ),
                              ],
                            ],
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
      ),
    );
  }
}

class _DashboardTab extends StatelessWidget {
  const _DashboardTab({required this.async, required this.onRefresh});

  final AsyncValue<ReporteTallerDashboard> async;
  final VoidCallback onRefresh;

  @override
  Widget build(BuildContext context) {
    return async.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (e, _) => TallerModuleError(
        message: e.toString(),
        onRetry: onRefresh,
      ),
      data: (d) => RefreshIndicator(
        onRefresh: () async => onRefresh(),
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TallerModuleCard(
              title: 'Dashboard operativo',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Bandeja pendiente: ${d.bandejaPendientes}'),
                  Text('Neto comisiones: ${tallerFormatBob(d.resumenComisiones.totalNeto)}'),
                  const SizedBox(height: 8),
                  ...d.solicitudesPorEstado.entries.map((e) => Text('${e.key}: ${e.value}')),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
