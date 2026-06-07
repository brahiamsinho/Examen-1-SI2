import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/app_env.dart';
import '../../../core/theme/app_theme.dart';
import '../../application/taller_auth_provider.dart';
import '../../application/taller_auth_state.dart';

class TallerSplashScreen extends ConsumerStatefulWidget {
  const TallerSplashScreen({super.key});

  @override
  ConsumerState<TallerSplashScreen> createState() => _TallerSplashScreenState();
}

class _TallerSplashScreenState extends ConsumerState<TallerSplashScreen> {
  bool _routed = false;

  void _route(TallerAuthState auth) {
    if (_routed || !mounted) return;
    if (auth.status == TallerAuthStatus.checking) return;
    _routed = true;
    if (auth.isAuthenticated) {
      context.go('/taller/app/inicio');
    } else {
      context.go('/taller/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    ref.watch(tallerAuthNotifierProvider);
    ref.listen<TallerAuthState>(tallerAuthNotifierProvider, (p, n) {
      _route(n);
    });

    Future<void>.delayed(const Duration(milliseconds: 900), () {
      if (mounted) _route(ref.read(tallerAuthNotifierProvider));
    });

    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0B1020), Color(0xFF121A30), Color(0xFF0B1020)],
          ),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              DecoratedBox(
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primaryColor.withValues(alpha: 0.35),
                      blurRadius: 28,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: CircleAvatar(
                  radius: 40,
                  backgroundColor: scheme.surfaceContainerHighest,
                  child: const Icon(Icons.storefront_rounded, size: 48, color: AppTheme.primaryColor),
                ),
              ),
              const SizedBox(height: 24),
              Text(
                AppEnv.appName,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
              ),
              const SizedBox(height: 8),
              Text(
                'Panel responsable de taller',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: scheme.onSurface.withValues(alpha: 0.72),
                    ),
              ),
              const SizedBox(height: 40),
              const SizedBox(
                width: 32,
                height: 32,
                child: CircularProgressIndicator(strokeWidth: 3),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
