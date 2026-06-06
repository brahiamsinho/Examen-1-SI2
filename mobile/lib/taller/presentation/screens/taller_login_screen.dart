import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/config/app_env.dart';
import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/auth/auth_screen_widgets.dart';
import '../../../core/widgets/auth/org_slug_selector.dart';
import '../../application/taller_auth_provider.dart';
import '../../application/taller_auth_state.dart';

class TallerLoginScreen extends ConsumerStatefulWidget {
  const TallerLoginScreen({super.key});

  @override
  ConsumerState<TallerLoginScreen> createState() => _TallerLoginScreenState();
}

class _TallerLoginScreenState extends ConsumerState<TallerLoginScreen> {
  String _tenantSlug = AppEnv.tenantSlugDefault;
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscurePassword = true;

  @override
  void initState() {
    super.initState();
    _loadTenantSlug();
  }

  Future<void> _loadTenantSlug() async {
    final slug = await resolveInitialTenantSlug();
    if (mounted) setState(() => _tenantSlug = slug);
  }

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  void _goBack() {
    if (context.canPop()) {
      context.pop();
    } else {
      context.go('/modo');
    }
  }

  Future<void> _onTenantSlugChanged(String slug) async {
    setState(() => _tenantSlug = slug);
    await persistTenantSlug(slug);
  }

  void _submit() {
    FocusScope.of(context).unfocus();
    ref.read(tallerAuthNotifierProvider.notifier).clearError();
    ref.read(tallerAuthNotifierProvider.notifier).login(
          email: _email.text,
          password: _password.text,
          tenantSlug: _tenantSlug,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(tallerAuthNotifierProvider);
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final bottomInset = MediaQuery.viewInsetsOf(context).bottom;

    ref.listen<TallerAuthState>(tallerAuthNotifierProvider, (p, n) {
      if (n.isAuthenticated) context.go('/taller/app/inicio');
    });

    return AuthScreenScaffold(
      child: Column(
        children: [
          AuthBackButton(onPressed: _goBack),
          Expanded(
            child: ListView(
              padding: EdgeInsets.fromLTRB(24, 8, 24, 24 + bottomInset),
              children: [
                AuthBrandHeader(
                  icon: Icons.storefront_rounded,
                  tagline: 'Bandeja, técnicos y operaciones.',
                  gradientColors: [
                    const Color(0xFF1A237E).withValues(alpha: 0.95),
                    MobileAuthTheme.accentCyan,
                  ],
                ),
                const SizedBox(height: 28),
                AuthFormCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'Responsable de taller',
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Gestiona la bandeja y el equipo de tu organización.',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: cs.onSurface.withValues(alpha: 0.72),
                        ),
                      ),
                      const SizedBox(height: 22),
                      OrgSlugSelector(
                        value: _tenantSlug,
                        onChanged: _onTenantSlugChanged,
                      ),
                      const SizedBox(height: 18),
                      const AuthFieldLabel('Correo'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _email,
                        keyboardType: TextInputType.emailAddress,
                        placeholder: const Text('responsable@org-pro-anillo.demo.test'),
                        leading: Icon(
                          Icons.alternate_email_rounded,
                          size: 20,
                          color: cs.onSurface.withValues(alpha: 0.55),
                        ),
                      ),
                      const SizedBox(height: 18),
                      const AuthFieldLabel('Contraseña'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _password,
                        obscureText: _obscurePassword,
                        placeholder: const Text('Tu contraseña'),
                        leading: Icon(
                          Icons.lock_outline_rounded,
                          size: 20,
                          color: cs.onSurface.withValues(alpha: 0.55),
                        ),
                        trailing: IconButton(
                          onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                          icon: Icon(
                            _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                          ),
                        ),
                        onSubmitted: (_) => _submit(),
                      ),
                      if (auth.authError != null) ...[
                        const SizedBox(height: 14),
                        AuthErrorBanner(message: auth.authError!),
                      ],
                      const SizedBox(height: 22),
                      ShadButton(
                        width: double.infinity,
                        size: ShadButtonSize.lg,
                        onPressed: auth.isLoggingIn ? null : _submit,
                        child: auth.isLoggingIn
                            ? const SizedBox(
                                width: 22,
                                height: 22,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Ingresar al panel'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
