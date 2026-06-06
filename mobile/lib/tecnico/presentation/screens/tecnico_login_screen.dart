import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/config/app_env.dart';
import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/theme/app_theme.dart';
import '../../../core/widgets/auth/auth_screen_widgets.dart';
import '../../../core/widgets/auth/org_slug_selector.dart';
import '../../application/tecnico_auth_provider.dart';
import '../../application/tecnico_auth_state.dart';

/// CU2 — Iniciar sesión móvil (técnico).
class TecnicoLoginScreen extends ConsumerStatefulWidget {
  const TecnicoLoginScreen({super.key});

  @override
  ConsumerState<TecnicoLoginScreen> createState() => _TecnicoLoginScreenState();
}

class _TecnicoLoginScreenState extends ConsumerState<TecnicoLoginScreen> {
  String _tenantSlug = AppEnv.tenantSlugDefault;
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _emailFocus = FocusNode();
  final _passwordFocus = FocusNode();
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
    _emailFocus.dispose();
    _passwordFocus.dispose();
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
    ref.read(tecnicoAuthNotifierProvider.notifier).clearError();
    ref.read(tecnicoAuthNotifierProvider.notifier).login(
          email: _email.text,
          password: _password.text,
          tenantSlug: _tenantSlug,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(tecnicoAuthNotifierProvider);
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final bottomInset = MediaQuery.viewInsetsOf(context).bottom;

    ref.listen<TecnicoAuthState>(tecnicoAuthNotifierProvider, (p, n) {
      if (n.isAuthenticated) context.go('/tecnico/app/inicio');
    });

    return AuthScreenScaffold(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthBackButton(onPressed: _goBack),
          Expanded(
            child: GestureDetector(
              onTap: () => FocusScope.of(context).unfocus(),
              behavior: HitTestBehavior.opaque,
              child: ListView(
                keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
                padding: EdgeInsets.fromLTRB(24, 8, 24, 24 + bottomInset),
                children: [
                  const AuthBrandHeader(
                    icon: Icons.build_circle_rounded,
                    iconColor: AppTheme.secondaryColor,
                    tagline: 'Operaciones de taller y campo.',
                  ),
                  const SizedBox(height: 28),
                  AuthFormCard(
                    child: AutofillGroup(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Acceso técnico',
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w600,
                              letterSpacing: -0.3,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Correo y contraseña de tu cuenta institucional.',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: cs.onSurface.withValues(alpha: 0.72),
                              height: 1.35,
                            ),
                          ),
                          const SizedBox(height: 22),
                          OrgSlugSelector(
                            value: _tenantSlug,
                            onChanged: _onTenantSlugChanged,
                          ),
                          const SizedBox(height: 18),
                          const AuthFieldLabel('Correo electrónico'),
                          const SizedBox(height: 8),
                          ShadInput(
                            controller: _email,
                            focusNode: _emailFocus,
                            placeholder: const Text('marco.salas@sc-demo.test'),
                            keyboardType: TextInputType.emailAddress,
                            textInputAction: TextInputAction.next,
                            autofillHints: const [AutofillHints.username, AutofillHints.email],
                            autocorrect: false,
                            leading: Icon(
                              Icons.alternate_email_rounded,
                              size: 20,
                              color: cs.onSurface.withValues(alpha: 0.55),
                            ),
                            onSubmitted: (_) => _passwordFocus.requestFocus(),
                          ),
                          const SizedBox(height: 18),
                          const AuthFieldLabel('Contraseña'),
                          const SizedBox(height: 8),
                          ShadInput(
                            controller: _password,
                            focusNode: _passwordFocus,
                            placeholder: const Text('Tu contraseña'),
                            obscureText: _obscurePassword,
                            textInputAction: TextInputAction.done,
                            autofillHints: const [AutofillHints.password],
                            autocorrect: false,
                            enableSuggestions: false,
                            leading: Icon(
                              Icons.lock_outline_rounded,
                              size: 20,
                              color: cs.onSurface.withValues(alpha: 0.55),
                            ),
                            trailing: IconButton(
                              onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                              tooltip: _obscurePassword ? 'Mostrar contraseña' : 'Ocultar contraseña',
                              icon: Icon(
                                _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                                size: 22,
                                color: cs.onSurface.withValues(alpha: 0.65),
                              ),
                            ),
                            onSubmitted: (_) => _submit(),
                          ),
                          if (auth.authError != null) ...[
                            const SizedBox(height: 16),
                            AuthErrorBanner(message: auth.authError!),
                          ],
                          const SizedBox(height: 22),
                          ShadButton(
                            width: double.infinity,
                            size: ShadButtonSize.lg,
                            onPressed: auth.isLoggingIn ? null : _submit,
                            child: auth.isLoggingIn
                                ? SizedBox(
                                    height: 22,
                                    width: 22,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2.5,
                                      color: cs.onPrimary,
                                    ),
                                  )
                                : const Text('Ingresar'),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Align(
                    alignment: Alignment.centerRight,
                    child: ShadButton.link(
                      onPressed: () => context.go('/tecnico/recuperar'),
                      child: const Text('¿Olvidaste tu contraseña?'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
