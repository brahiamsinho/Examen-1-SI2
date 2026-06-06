import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/auth/auth_screen_widgets.dart';
import '../../../core/widgets/auth/cliente_org_chip.dart';
import '../../application/client_auth_provider.dart';
import '../../application/cliente_injection.dart';
import '../widgets/cliente_panel_ui.dart';

class ClientePerfilScreen extends ConsumerStatefulWidget {
  const ClientePerfilScreen({super.key});

  @override
  ConsumerState<ClientePerfilScreen> createState() => _ClientePerfilScreenState();
}

class _ClientePerfilScreenState extends ConsumerState<ClientePerfilScreen> {
  final _nombres = TextEditingController();
  final _apellidos = TextEditingController();
  final _telefono = TextEditingController();
  final _ciudad = TextEditingController();
  final _direccion = TextEditingController();

  bool _saving = false;
  String? _error;
  String? _ok;
  String _tenantSlug = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _syncFromProfile());
    _loadSlug();
  }

  Future<void> _loadSlug() async {
    final slug = await resolveInitialTenantSlug();
    if (mounted) setState(() => _tenantSlug = slug);
  }

  void _syncFromProfile() {
    final p = ref.read(clientAuthNotifierProvider).profile;
    if (p == null) return;
    _nombres.text = p.nombres;
    _apellidos.text = p.apellidos;
    _telefono.text = p.telefono;
    _ciudad.text = p.ciudad ?? '';
    _direccion.text = p.direccion ?? '';
    setState(() {});
  }

  @override
  void dispose() {
    _nombres.dispose();
    _apellidos.dispose();
    _telefono.dispose();
    _ciudad.dispose();
    _direccion.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() {
      _saving = true;
      _error = null;
      _ok = null;
    });
    final authRepo = ref.read(authRepositoryProvider);
    try {
      final updated = await authRepo.updateMiPerfil(
        nombres: _nombres.text.trim(),
        apellidos: _apellidos.text.trim(),
        telefono: _telefono.text.trim(),
        ciudad: _ciudad.text.trim(),
        direccion: _direccion.text.trim(),
      );
      ref.read(clientAuthNotifierProvider.notifier).replaceProfileAfterUpdate(updated);
      setState(() => _ok = 'Cambios guardados.');
    } catch (e) {
      setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _confirmLogout() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: MobileAuthTheme.cardColor,
        title: const Text('Cerrar sesión'),
        content: const Text('¿Seguro que deseas salir de la aplicación?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Cerrar sesión')),
        ],
      ),
    );
    if (ok == true && mounted) {
      await ref.read(clientAuthNotifierProvider.notifier).logout();
      if (mounted) context.go('/cliente/login');
    }
  }

  Future<void> _onOrgChanged(String slug) async {
    await persistTenantSlug(slug);
    if (mounted) setState(() => _tenantSlug = slug);
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(clientAuthNotifierProvider).profile;

    return ClientePanelBackground(
      child: ListView(
        padding: ClientePanelUi.pagePadding,
        children: [
          ClienteTabHeader(
            title: 'Perfil',
            subtitle: profile?.email,
            trailing: _tenantSlug.isEmpty
                ? null
                : ClienteOrgChip(slug: _tenantSlug, onChanged: _onOrgChanged),
          ),
          const SizedBox(height: 20),
          AuthFormCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const AuthFieldLabel('Nombres'),
                ShadInput(controller: _nombres),
                const SizedBox(height: 14),
                const AuthFieldLabel('Apellidos'),
                ShadInput(controller: _apellidos),
                const SizedBox(height: 14),
                const AuthFieldLabel('Teléfono'),
                ShadInput(controller: _telefono, keyboardType: TextInputType.phone),
                const SizedBox(height: 14),
                const AuthFieldLabel('Ciudad'),
                ShadInput(controller: _ciudad, placeholder: const Text('Opcional')),
                const SizedBox(height: 14),
                const AuthFieldLabel('Dirección'),
                ShadInput(controller: _direccion, placeholder: const Text('Opcional'), maxLines: 3),
                if (_error != null) ...[
                  const SizedBox(height: 14),
                  AuthErrorBanner(message: _error!),
                ],
                if (_ok != null) ...[
                  const SizedBox(height: 14),
                  ClienteInfoBanner(message: _ok!, tone: ClienteBannerTone.success),
                ],
                const SizedBox(height: 20),
                ShadButton(
                  onPressed: _saving ? null : _save,
                  child: _saving
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Guardar cambios'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: _confirmLogout,
            style: OutlinedButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
              side: BorderSide(color: Theme.of(context).colorScheme.error.withValues(alpha: 0.5)),
            ),
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }
}
