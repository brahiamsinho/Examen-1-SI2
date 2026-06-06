import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/config/app_env.dart';
import '../../../core/tenant/tenant_slug_resolver.dart';
import '../../../core/widgets/auth/auth_screen_widgets.dart';
import '../../../core/widgets/auth/org_slug_selector.dart';
import '../../application/client_auth_provider.dart';
import '../../application/client_auth_state.dart';
import '../../application/cliente_injection.dart';

class ClienteLoginScreen extends ConsumerStatefulWidget {
  const ClienteLoginScreen({super.key});

  @override
  ConsumerState<ClienteLoginScreen> createState() => _ClienteLoginScreenState();
}

class _ClienteLoginScreenState extends ConsumerState<ClienteLoginScreen> {
  String _tenantSlug = AppEnv.tenantSlugDefault;
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _emailFocus = FocusNode();
  final _passwordFocus = FocusNode();
  bool _obscurePassword = true;
  String? _postRegisterHint;

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
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_postRegisterHint != null) return;
    final extra = GoRouterState.of(context).extra;
    if (extra is String && extra.trim().isNotEmpty) {
      _postRegisterHint = extra.trim();
    }
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

  void _submit() {
    FocusScope.of(context).unfocus();
    ref.read(clientAuthNotifierProvider.notifier).clearError();
    ref.read(clientAuthNotifierProvider.notifier).login(
          email: _email.text,
          password: _password.text,
          tenantSlug: _tenantSlug,
        );
  }

  Future<void> _onTenantSlugChanged(String slug) async {
    setState(() => _tenantSlug = slug);
    await persistTenantSlug(slug);
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(clientAuthNotifierProvider);
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final bottomInset = MediaQuery.viewInsetsOf(context).bottom;

    ref.listen<ClientAuthState>(clientAuthNotifierProvider, (p, n) {
      if (n.isAuthenticated) context.go('/cliente/app/home');
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
                    icon: Icons.directions_car_filled_rounded,
                  ),
                  const SizedBox(height: 28),
                  AuthFormCard(
                    child: AutofillGroup(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            'Acceso cliente',
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w600,
                              letterSpacing: -0.3,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Usa el correo y la contraseña de tu cuenta.',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: cs.onSurface.withValues(alpha: 0.72),
                              height: 1.35,
                            ),
                          ),
                          if (_postRegisterHint != null) ...[
                            const SizedBox(height: 16),
                            DecoratedBox(
                              decoration: BoxDecoration(
                                color: Colors.teal.withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.teal.withValues(alpha: 0.45)),
                              ),
                              child: Padding(
                                padding: const EdgeInsets.all(12),
                                child: Text(
                                  _postRegisterHint!,
                                  style: theme.textTheme.bodyMedium?.copyWith(height: 1.35),
                                ),
                              ),
                            ),
                          ],
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
                            placeholder: const Text('correo@ejemplo.com'),
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
                      onPressed: () => context.go('/cliente/recuperar'),
                      child: const Text('¿Olvidaste tu contraseña?'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.center,
                    alignment: WrapAlignment.center,
                    spacing: 4,
                    runSpacing: 4,
                    children: [
                      Text(
                        '¿No tienes cuenta?',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: cs.onSurface.withValues(alpha: 0.75),
                        ),
                      ),
                      ShadButton.link(
                        onPressed: () => context.go('/cliente/registro'),
                        child: const Text(
                          'Crear cuenta',
                          style: TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
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

// Legacy private widgets removed — use core/widgets/auth/auth_screen_widgets.dart

class ClienteRegisterScreen extends ConsumerStatefulWidget {
  const ClienteRegisterScreen({super.key});

  @override
  ConsumerState<ClienteRegisterScreen> createState() => _ClienteRegisterScreenState();
}

class _ClienteRegisterScreenState extends ConsumerState<ClienteRegisterScreen> {
  String _tenantSlug = AppEnv.tenantSlugDefault;
  final _nombres = TextEditingController();
  final _apellidos = TextEditingController();
  final _email = TextEditingController();
  final _telefono = TextEditingController();
  final _pass = TextEditingController();
  final _pass2 = TextEditingController();

  String? _localError;

  @override
  void initState() {
    super.initState();
    _loadTenantSlug();
  }

  Future<void> _loadTenantSlug() async {
    final slug = await resolveInitialTenantSlug();
    if (mounted) setState(() => _tenantSlug = slug);
  }

  Future<void> _onTenantSlugChanged(String slug) async {
    setState(() => _tenantSlug = slug);
    await persistTenantSlug(slug);
  }

  @override
  void dispose() {
    _nombres.dispose();
    _apellidos.dispose();
    _email.dispose();
    _telefono.dispose();
    _pass.dispose();
    _pass2.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(clientAuthNotifierProvider);
    ref.listen<ClientAuthState>(clientAuthNotifierProvider, (p, n) {
      if (n.isAuthenticated) {
        context.go('/cliente/app/home');
        return;
      }
      // Tras registro con verificación por correo: llevar al login con el mismo aviso.
      if (n.infoMessage != null &&
          !n.isLoggingIn &&
          p != null &&
          p.isLoggingIn &&
          !p.isAuthenticated) {
        final msg = n.infoMessage!;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (!context.mounted) return;
          ref.read(clientAuthNotifierProvider.notifier).clearInfoMessage();
          context.go('/cliente/login', extra: msg);
        });
      }
    });

    return AuthScreenScaffold(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          AuthBackButton(onPressed: () => context.go('/cliente/login')),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              children: [
                const AuthBrandHeader(
                  icon: Icons.person_add_rounded,
                  tagline: 'Crea tu cuenta de cliente en minutos.',
                ),
                const SizedBox(height: 24),
                AuthFormCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        'Registro cliente',
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Completa tus datos. Te enviaremos verificación por correo si aplica.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.72),
                            ),
                      ),
                      const SizedBox(height: 20),
                      OrgSlugSelector(
                        value: _tenantSlug,
                        onChanged: _onTenantSlugChanged,
                      ),
                      const SizedBox(height: 16),
                      const AuthFieldLabel('Nombres'),
                      const SizedBox(height: 8),
                      ShadInput(controller: _nombres, placeholder: const Text('Nombres')),
                      const SizedBox(height: 14),
                      const AuthFieldLabel('Apellidos'),
                      const SizedBox(height: 8),
                      ShadInput(controller: _apellidos, placeholder: const Text('Apellidos')),
                      const SizedBox(height: 14),
                      const AuthFieldLabel('Correo'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _email,
                        placeholder: const Text('correo@ejemplo.com'),
                        keyboardType: TextInputType.emailAddress,
                      ),
                      const SizedBox(height: 14),
                      const AuthFieldLabel('Teléfono'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _telefono,
                        placeholder: const Text('+591...'),
                        keyboardType: TextInputType.phone,
                      ),
                      const SizedBox(height: 14),
                      const AuthFieldLabel('Contraseña'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _pass,
                        obscureText: true,
                        placeholder: const Text('Mínimo 6 caracteres'),
                      ),
                      const SizedBox(height: 14),
                      const AuthFieldLabel('Confirmar contraseña'),
                      const SizedBox(height: 8),
                      ShadInput(
                        controller: _pass2,
                        obscureText: true,
                        placeholder: const Text('Repite la contraseña'),
                      ),
                      if (_localError != null) ...[
                        const SizedBox(height: 14),
                        AuthErrorBanner(message: _localError!),
                      ],
                      if (auth.infoMessage != null) ...[
                        const SizedBox(height: 14),
                        DecoratedBox(
                          decoration: BoxDecoration(
                            color: Colors.teal.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.teal.withValues(alpha: 0.45)),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Text(
                              auth.infoMessage!,
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(height: 1.35),
                            ),
                          ),
                        ),
                      ],
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
                                height: 18,
                                width: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('Registrarse'),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Center(
                  child: ShadButton.link(
                    onPressed: () => context.go('/cliente/login'),
                    child: const Text('Ya tengo cuenta'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _submit() {
    setState(() => _localError = null);
    persistTenantSlug(_tenantSlug);
    if (_nombres.text.trim().isEmpty || _apellidos.text.trim().isEmpty) {
      setState(() => _localError = 'Indica nombres y apellidos.');
      return;
    }
    if (_email.text.trim().isEmpty) {
      setState(() => _localError = 'Indica un correo válido.');
      return;
    }
    if (_telefono.text.trim().length < 5) {
      setState(() => _localError = 'Indica un teléfono válido.');
      return;
    }
    if (_pass.text.length < 6) {
      setState(() => _localError = 'La contraseña debe tener al menos 6 caracteres.');
      return;
    }
    if (_pass.text != _pass2.text) {
      setState(() => _localError = 'Las contraseñas no coinciden.');
      return;
    }
    ref.read(clientAuthNotifierProvider.notifier).clearError();
    ref.read(clientAuthNotifierProvider.notifier).registerAndLogin(
          nombres: _nombres.text,
          apellidos: _apellidos.text,
          email: _email.text,
          telefono: _telefono.text,
          password: _pass.text,
        );
  }
}

class ClienteRecoverScreen extends ConsumerStatefulWidget {
  const ClienteRecoverScreen({super.key});

  @override
  ConsumerState<ClienteRecoverScreen> createState() => _ClienteRecoverScreenState();
}

class _ClienteRecoverScreenState extends ConsumerState<ClienteRecoverScreen> {
  final _email = TextEditingController();
  bool _sent = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _email.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_email.text.trim().isEmpty) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await ref.read(authRepositoryProvider).solicitarRecuperacionContrasena(email: _email.text);
      setState(() {
        _sent = true;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Restablecer contraseña')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: _sent
            ? Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.mark_email_read_outlined, size: 48),
                  const SizedBox(height: 16),
                  Text(
                    'Si el correo existe en el sistema, recibirás un enlace para restablecer la contraseña. '
                    'En desarrollo revisa MailHog (puerto 8025) si usas Docker.',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 24),
                  ShadButton(
                    onPressed: () => context.go('/cliente/login'),
                    child: const Text('Volver al inicio de sesión'),
                  ),
                ],
              )
            : ListView(
                children: [
                  Text(
                    'Ingresa el correo de tu cuenta. Te enviaremos un enlace (válido 2 horas).',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 20),
                  Text('Correo', style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 6),
                  ShadInput(
                    controller: _email,
                    placeholder: const Text('correo@ejemplo.com'),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
                  ],
                  const SizedBox(height: 24),
                  ShadButton(
                    onPressed: _loading ? null : _submit,
                    child: _loading
                        ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                        : const Text('Enviar solicitud'),
                  ),
                  TextButton(onPressed: () => context.go('/cliente/login'), child: const Text('Volver')),
                ],
              ),
      ),
    );
  }
}
