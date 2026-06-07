import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/utils/bolivia_time.dart';
import '../../../../core/network/solicitud_realtime_listener.dart';
import '../../../../core/network/solicitud_realtime_providers.dart';
import '../../../../core/network/solicitud_realtime_ws_client.dart';
import '../../../presentation/widgets/cliente_panel_ui.dart';
import '../../application/emergencias_providers.dart';
import '../../application/offline_sync_providers.dart';
import '../../domain/solicitud_draft.dart';
import '../../domain/solicitud_emergencia_models.dart';

/// Lista de solicitudes del cliente + borradores offline (CU43/CU45).
class EmergenciasMisSolicitudesScreen extends ConsumerStatefulWidget {
  const EmergenciasMisSolicitudesScreen({super.key});

  @override
  ConsumerState<EmergenciasMisSolicitudesScreen> createState() =>
      _EmergenciasMisSolicitudesScreenState();
}

class _EmergenciasMisSolicitudesScreenState extends ConsumerState<EmergenciasMisSolicitudesScreen> {
  bool _syncing = false;

  Future<void> _syncManual() async {
    setState(() => _syncing = true);
    try {
      final result = await ref.read(offlineSyncManualProvider)();
      if (!mounted) return;
      final msg = result.lastMessage ??
          (result.sent > 0
              ? '${result.sent} borrador(es) sincronizado(s)'
              : 'No había borradores listos o falta conexión');
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
    } finally {
      if (mounted) setState(() => _syncing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(misSolicitudesEmergenciasProvider);
    final draftsAsync = ref.watch(solicitudDraftsProvider);
    final pendingAsync = ref.watch(pendingDraftsCountProvider);
    final lastSync = ref.watch(lastSyncResultProvider);

    final pendingCount = pendingAsync.maybeWhen(data: (c) => c, orElse: () => 0);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis solicitudes'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.canPop() ? context.pop() : context.go('/cliente/app/home'),
        ),
        actions: [
          if (pendingCount > 0)
            Padding(
              padding: const EdgeInsets.only(right: 8),
              child: Center(
                child: Chip(
                  avatar: const Icon(Icons.cloud_upload_outlined, size: 18),
                  label: Text('$pendingCount pendiente${pendingCount == 1 ? '' : 's'}'),
                ),
              ),
            ),
        ],
      ),
    return ClienteSubpageScaffold(
      title: 'Mis solicitudes',
      onBack: () => context.canPop() ? context.pop() : context.go('/cliente/app/home'),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => _ErrorBody(
          message: e.toString(),
          onRetry: () => ref.invalidate(misSolicitudesEmergenciasProvider),
        ),
        data: (list) {
          final drafts = draftsAsync.maybeWhen(
            data: (d) => d.where((x) => x.isPendingSync || x.status == SolicitudDraftStatus.building).toList(),
            orElse: () => <SolicitudDraft>[],
          );
          final hasAnything = list.isNotEmpty || drafts.isNotEmpty;

          if (!hasAnything) {
            return _EmptyBody(
              onNueva: () => context.push('/cliente/app/emergencias'),
            );
          if (list.isEmpty) {
            return _EmptyBody(onNueva: () => context.push('/cliente/app/emergencias'));
          }
          final activas = list.where((s) => !s.estado.esTerminal).map((s) => s.id).toList();
          return ClienteMultiSolicitudRealtimeListener(
            solicitudIds: activas,
            onEvent: (RealtimeWsEvent ev) {
              if (realtimeEventAffectsSeguimiento(ev.tipo)) {
                ref.invalidate(misSolicitudesEmergenciasProvider);
              }
            },
            child: RefreshIndicator(
              onRefresh: () async => ref.invalidate(misSolicitudesEmergenciasProvider),
              child: ListView.separated(
                padding: ClientePanelUi.pagePadding,
                itemCount: list.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, i) => _SolicitudTile(solicitud: list[i]),
              ),

          return RefreshIndicator(
            onRefresh: () async {
              ref.invalidate(misSolicitudesEmergenciasProvider);
              ref.invalidate(solicitudDraftsProvider);
              ref.read(offlineSyncTickProvider.notifier).bump();
            },
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (drafts.isNotEmpty) ...[
                  _SyncPanel(
                    syncing: _syncing,
                    pendingCount: drafts.length,
                    lastMessage: lastSync?.lastMessage,
                    onSync: _syncManual,
                  ),
                  const SizedBox(height: 12),
                  Text('Pendientes en el dispositivo', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                  for (final d in drafts) ...[
                    _DraftTile(draft: d),
                    const SizedBox(height: 10),
                  ],
                  const SizedBox(height: 8),
                  Text('En el servidor', style: Theme.of(context).textTheme.titleSmall),
                  const SizedBox(height: 8),
                ],
                if (list.isEmpty && drafts.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    child: Text(
                      'Aún no hay solicitudes en el servidor. Sincronizá los borradores cuando tengas red.',
                      style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant),
                    ),
                  ),
                for (var i = 0; i < list.length; i++) ...[
                  _SolicitudTile(solicitud: list[i]),
                  if (i < list.length - 1) const SizedBox(height: 10),
                ],
              ],
            onRefresh: () async => ref.invalidate(misSolicitudesEmergenciasProvider),
            child: ListView.separated(
              padding: ClientePanelUi.pagePadding,
              itemCount: list.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, i) => _SolicitudTile(solicitud: list[i]),
            ),
          );
        },
      ),
    );
  }
}

class _SyncPanel extends StatelessWidget {
  const _SyncPanel({
    required this.syncing,
    required this.pendingCount,
    required this.onSync,
    this.lastMessage,
  });

  final bool syncing;
  final int pendingCount;
  final VoidCallback onSync;
  final String? lastMessage;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.sync, color: scheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '$pendingCount borrador(es) por enviar',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
            if (lastMessage != null) ...[
              const SizedBox(height: 8),
              Text(lastMessage!, style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant)),
            ],
            const SizedBox(height: 12),
            ShadButton(
              onPressed: syncing ? null : onSync,
              child: syncing
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Sincronizar ahora'),
            ),
          ],
        ),
      ),
    );
  }
}

class _DraftTile extends StatelessWidget {
  const _DraftTile({required this.draft});

  final SolicitudDraft draft;

  String _fecha(DateTime d) => BoliviaTime.format(d, pattern: 'dd/MM/yyyy HH:mm');

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: scheme.secondaryContainer.withValues(alpha: 0.35),
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.cloud_off, color: scheme.secondary, size: 28),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Borrador offline',
                    style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
                  ),
                  const SizedBox(height: 6),
                  Chip(
                    label: Text(draft.status.label, style: const TextStyle(fontSize: 12)),
                    visualDensity: VisualDensity.compact,
                    padding: EdgeInsets.zero,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Vehículo #${draft.vehiculoId} · ${_fecha(draft.updatedAt)}',
                    style: TextStyle(fontSize: 12, color: scheme.onSurfaceVariant),
                  ),
                  if (draft.lastError != null) ...[
                    const SizedBox(height: 6),
                    Text(
                      draft.lastError!,
                      style: TextStyle(fontSize: 12, color: scheme.error),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SolicitudTile extends StatelessWidget {
  const _SolicitudTile({required this.solicitud});

  final SolicitudEmergenciaListItem solicitud;

  String _fecha(DateTime d) => BoliviaTime.format(d, pattern: 'dd/MM/yyyy');

  @override
  Widget build(BuildContext context) {
    return ClienteActionTile(
      icon: Icons.emergency_outlined,
      title: 'Solicitud #${solicitud.id}',
      subtitle: [
        'Vehículo #${solicitud.vehiculoId} · ${_fecha(solicitud.createdAt)}',
        if (solicitud.tallerId == null && solicitud.estado.puedeElegirTaller)
          'Pendiente: elegir taller'
        else if (solicitud.tiempoEstimadoMin != null)
          'ETA: ${solicitud.tiempoEstimadoMin} min',
      ].join('\n'),
      accent: Theme.of(context).colorScheme.error.withValues(alpha: 0.85),
      onTap: () => context.push('/cliente/app/emergencias/solicitudes/${solicitud.id}'),
    );
  }
}

class _EmptyBody extends StatelessWidget {
  const _EmptyBody({required this.onNueva});

  final VoidCallback onNueva;

  @override
  Widget build(BuildContext context) {
    return ClienteEmptyState(
      icon: Icons.inbox_outlined,
      title: 'No tenés solicitudes aún',
      message: 'Cuando reportes una emergencia, aparecerá acá para seguimiento.',
      actionLabel: 'Reportar emergencia',
      onAction: onNueva,
    );
  }
}

class _ErrorBody extends StatelessWidget {
  const _ErrorBody({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ClienteEmptyState(
      icon: Icons.error_outline,
      title: 'Error al cargar',
      message: message,
      actionLabel: 'Reintentar',
      onAction: onRetry,
    );
  }
}
