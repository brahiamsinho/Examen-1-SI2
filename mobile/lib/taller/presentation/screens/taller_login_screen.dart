import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/config/app_env.dart';
import '../../../core/theme/app_theme.dart';
import '../../application/taller_auth_provider.dart';
import '../../application/taller_auth_state.dart';

class TallerLoginScreen extends ConsumerStatefulWidget {
  const TallerLoginScreen({super.key});

  @override
  ConsumerState<TallerLoginScreen> createState() => _TallerLoginScreenState();
}

class _TallerLoginScreenState extends ConsumerState<TallerLoginScreen> {
  final _orgSlug = TextEditingController(text: AppEnv.tenantSlugDefault);
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _orgSlug.dispose();
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

  void _submit() {
    FocusScope.of(context).unfocus();
    ref.read(tallerAuthNotifierProvider.notifier).clearError();
    ref.read(tallerAuthNotifierProvider.notifier).login(
          email: _email.text,
          password: _password.text,
          tenantSlug: _orgSlug.text,
        );
  }

  @override
  Widget build(BuildContext context) {
    final auth = ref.watch(tallerAuthNotifierProvider);
    final theme = Theme.of(context);
    final cs = theme.colorScheme;

    ref.listen<TallerAuthState>(tallerAuthNotifierProvider, (p, n) {
      if (n.isAuthenticated) context.go('/taller/app/inicio');
    });

    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0B1020), Color(0xFF121A30), Color(0xFF0B1020)],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Align(
                alignment: Alignment.centerLeft,
                child: IconButton(
                  onPressed: _goBack,
                  icon: const Icon(Icons.arrow_back_rounded),
                ),
              ),
              Expanded(
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
                  children: [
                    Row(
                      children: [
                        DecoratedBox(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(16),
                            gradient: LinearGradient(
                              colors: [
                                AppTheme.primaryColor.withValues(alpha: 0.95),
                                const Color(0xFF0EA5E9),
                              ],
                            ),
                          ),
                          child: const Padding(
                            padding: EdgeInsets.all(14),
                            child: Icon(Icons.storefront_rounded, size: 32, color: Colors.white),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'Responsable de taller',
                                style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                              ),
                              Text(
                                'Bandeja, técnicos y operaciones.',
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: cs.onSurface.withValues(alpha: 0.68),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 28),
                    DecoratedBox(
                      decoration: BoxDecoration(
                        color: const Color(0xFF141B2E),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: const Color(0xFF2A3658)),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            Text('Organización', style: theme.textTheme.labelLarge),
                            const SizedBox(height: 8),
                            ShadInput(controller: _orgSlug, placeholder: const Text('demo-sc')),
                            const SizedBox(height: 16),
                            Text('Correo', style: theme.textTheme.labelLarge),
                            const SizedBox(height: 8),
                            ShadInput(
                              controller: _email,
                              keyboardType: TextInputType.emailAddress,
                              placeholder: const Text('luis.rivera@sc-demo.test'),
                            ),
                            const SizedBox(height: 16),
                            Text('Contraseña', style: theme.textTheme.labelLarge),
                            const SizedBox(height: 8),
                            ShadInput(
                              controller: _password,
                              obscureText: _obscurePassword,
                              placeholder: const Text('Tu contraseña'),
                              trailing: IconButton(
                                onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                                icon: Icon(
                                  _obscurePassword ? Icons.visibility_outlined : Icons.visibility_off_outlined,
                                ),
                              ),
                              onSubmitted: (_) => _submit(),
                            ),
                            if (auth.authError != null) ...[
                              const SizedBox(height: 12),
                              Text(auth.authError!, style: TextStyle(color: cs.error)),
                            ],
                            const SizedBox(height: 20),
                            ShadButton(
                              width: double.infinity,
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
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
