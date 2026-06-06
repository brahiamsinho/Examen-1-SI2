import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/utils/bolivia_time.dart';
import '../../../presentation/widgets/cliente_panel_ui.dart';
import '../../application/emergencias_providers.dart';
import '../../domain/solicitud_emergencia_models.dart';

/// Lista de solicitudes del cliente — entrada CU16–CU18 vía detalle / seguimiento.
class EmergenciasMisSolicitudesScreen extends ConsumerWidget {
  const EmergenciasMisSolicitudesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(misSolicitudesEmergenciasProvider);

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
          if (list.isEmpty) {
            return _EmptyBody(onNueva: () => context.push('/cliente/app/emergencias'));
          }
          return RefreshIndicator(
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
        if (solicitud.tiempoEstimadoMin != null) 'ETA: ${solicitud.tiempoEstimadoMin} min',
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
