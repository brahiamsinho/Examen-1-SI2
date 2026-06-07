import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/auth/cliente_org_chip.dart';
import '../../application/client_auth_provider.dart';
import '../../application/vehiculos_providers.dart';
import '../widgets/cliente_panel_ui.dart';

class ClienteHomeScreen extends ConsumerStatefulWidget {
  const ClienteHomeScreen({super.key});

  @override
  ConsumerState<ClienteHomeScreen> createState() => _ClienteHomeScreenState();
}

class _ClienteHomeScreenState extends ConsumerState<ClienteHomeScreen> {
  String _tenantSlug = '';

  @override
  void initState() {
    super.initState();
    _loadSlug();
  }

  Future<void> _loadSlug() async {
    final slug = await resolveInitialTenantSlug();
    if (mounted) setState(() => _tenantSlug = slug);
  }

  Future<void> _onOrgChanged(String slug) async {
    await persistTenantSlug(slug);
    if (mounted) {
      setState(() => _tenantSlug = slug);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Organización actualizada. Los próximos requests usarán este código.'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(clientAuthNotifierProvider).profile;
    final vehiculos = ref.watch(vehiculosMineProvider);
    final nombre = profile?.nombres ?? 'cliente';

    return ClientePanelBackground(
      child: ListView(
        padding: ClientePanelUi.pagePadding,
        children: [
          ClienteTabHeader(
            title: 'Inicio',
            subtitle: 'Hola, $nombre',
            trailing: _tenantSlug.isEmpty
                ? null
                : ClienteOrgChip(slug: _tenantSlug, onChanged: _onOrgChanged),
          ),
          const SizedBox(height: 8),
          Text(
            'Resumen de tu cuenta',
            style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.62),
                  letterSpacing: 0.3,
                ),
          ),
          if (profile != null) ...[
            const SizedBox(height: 4),
            Text(
              profile.email,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.78),
                  ),
            ),
          ],
          const SizedBox(height: 20),
          vehiculos.when(
            loading: () => const Padding(
              padding: EdgeInsets.symmetric(vertical: 32),
              child: Center(child: CircularProgressIndicator()),
            ),
            error: (e, _) => ClienteInfoBanner(
              message: e.toString().replaceFirst('Exception: ', ''),
              icon: Icons.error_outline_rounded,
              tone: ClienteBannerTone.warning,
            ),
            data: (list) {
              if (list.isEmpty) {
                return const ClienteInfoBanner(
                  message: 'Sin vehículos aún. Registra al menos uno para reportar emergencias.',
                  icon: Icons.directions_car_outlined,
                  tone: ClienteBannerTone.warning,
                );
              }
              return ClienteInfoBanner(
                message: 'Tienes ${list.length} vehículo(s) registrados.',
              );
            },
          ),
          const SizedBox(height: 24),
          const ClienteSectionLabel('Acciones rápidas'),
          ClienteActionTile(
            icon: Icons.emergency_share_rounded,
            title: 'Reportar emergencia',
            subtitle: 'Ubicación, fotos, audio y detalle',
            accent: MobileAuthTheme.accentCyan,
            emphasis: true,
            onTap: () => context.push('/cliente/app/emergencias'),
          ),
          const SizedBox(height: 12),
          ClienteActionTile(
            icon: Icons.timeline_rounded,
            title: 'Mis solicitudes',
            subtitle: 'Estado, taller, técnico y ETA',
            onTap: () => context.push('/cliente/app/emergencias/solicitudes'),
          ),
          const SizedBox(height: 12),
          ClienteActionTile(
            icon: Icons.notifications_none_rounded,
            title: 'Notificaciones',
            subtitle: 'Novedades de tus solicitudes y mensajes',
            onTap: () => context.push('/cliente/app/notificaciones'),
          ),
          const SizedBox(height: 12),
          ClienteActionTile(
            icon: Icons.directions_car_rounded,
            title: 'Mis vehículos',
            subtitle: 'Ver y administrar tu flota',
            onTap: () => context.go('/cliente/app/vehiculos'),
          ),
          if (vehiculos.asData?.value.isEmpty ?? false) ...[
            const SizedBox(height: 12),
            ClienteActionTile(
              icon: Icons.add_road_rounded,
              title: 'Registrar vehículo',
              subtitle: 'Añade placa, marca y modelo',
              accent: Colors.tealAccent,
              onTap: () => context.push('/cliente/app/vehiculos/nuevo'),
            ),
          ],
        ],
      ),
    );
  }
}
