// CU11 — elegir vehículo antes del asistente de reporte.
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../application/vehiculos_providers.dart';
import '../../../presentation/widgets/cliente_panel_ui.dart';
class EmergenciaSeleccionVehiculoScreen extends ConsumerWidget {
  const EmergenciaSeleccionVehiculoScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(vehiculosMineProvider);
    return ClienteSubpageScaffold(
      title: 'Reportar emergencia',
      onBack: () => context.canPop() ? context.pop() : context.go('/cliente/app/home'),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(vehiculosMineProvider),
        child: async.when(
          loading: () => const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator())),
          error: (e, _) => ListView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(24),
            children: [
              ClienteInfoBanner(
                message: e.toString().replaceFirst('Exception: ', ''),
                icon: Icons.error_outline_rounded,
                tone: ClienteBannerTone.warning,
              ),
              const SizedBox(height: 16),
              ShadButton(onPressed: () => ref.invalidate(vehiculosMineProvider), child: const Text('Reintentar')),
            ],
          ),
          data: (items) {
            if (items.isEmpty) {
              return ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                children: [
                  ClienteEmptyState(
                    icon: Icons.car_crash_outlined,
                    title: 'Necesitás un vehículo registrado',
                    message: 'Registrá tu vehículo y volvé para poder reportar una emergencia.',
                    actionLabel: 'Registrar vehículo',
                    onAction: () => context.push('/cliente/app/vehiculos/nuevo'),
                  ),
                ],
              );
            }
            return ListView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: ClientePanelUi.pagePadding,
              children: [
                const ClienteSectionLabel('Elige el vehículo afectado'),
                for (var i = 0; i < items.length; i++) ...[
                  if (i > 0) const SizedBox(height: 12),
                  ClienteActionTile(
                    icon: Icons.emergency_share_rounded,
                    title: items[i].placa,
                    subtitle: '${items[i].marcaNombre} ${items[i].modeloNombre} · ${items[i].tipoNombre}',
                    accent: Theme.of(context).colorScheme.error.withValues(alpha: 0.85),
                    emphasis: true,
                    onTap: () => context.push('/cliente/app/emergencias/crear/${items[i].id}'),
                  ),
                ],
                const SizedBox(height: 20),
                Center(
                  child: ShadButton.outline(
                    onPressed: () => context.push('/cliente/app/emergencias/solicitudes'),
                    child: const Text('Ver mis solicitudes'),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
