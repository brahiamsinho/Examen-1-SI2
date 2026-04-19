import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../application/client_auth_provider.dart';
import '../../application/client_auth_state.dart';
import '../screens/actor_select_screen.dart';
import '../screens/cliente_auth_screens.dart';
import '../screens/cliente_home_screen.dart';
import '../screens/cliente_perfil_screen.dart';
import '../screens/cliente_vehiculos_flow.dart';
import '../screens/onboarding_screen.dart';
import '../screens/splash_screen.dart';
import '../shell/cliente_app_shell.dart';
import '../../../tecnico/application/tecnico_auth_provider.dart';
import '../../../tecnico/application/tecnico_auth_state.dart';
import '../../../tecnico/presentation/screens/tecnico_home_screen.dart';
import '../../../tecnico/presentation/screens/tecnico_login_screen.dart';
import '../../../tecnico/presentation/screens/tecnico_placeholder_screen.dart';
import '../../../tecnico/presentation/screens/tecnico_perfil_screen.dart';
import '../../../tecnico/presentation/screens/tecnico_recover_screen.dart';
import '../../../tecnico/presentation/screens/tecnico_splash_screen.dart';
import '../../../tecnico/presentation/shell/tecnico_app_shell.dart';

/// Router principal: splash/onboarding/modo, **cliente** y **técnico** (módulos separados).
final goRouterProvider = Provider<GoRouter>((ref) {
  final refresh = ValueNotifier<int>(0);
  ref.listen<ClientAuthState>(clientAuthNotifierProvider, (_, __) {
    refresh.value++;
  });
  ref.listen<TecnicoAuthState>(tecnicoAuthNotifierProvider, (_, __) {
    refresh.value++;
  });
  ref.onDispose(refresh.dispose);

  return GoRouter(
    initialLocation: '/splash',
    refreshListenable: refresh,
    redirect: (context, state) {
      final loc = state.matchedLocation;

      if (loc.startsWith('/tecnico')) {
        final t = ref.read(tecnicoAuthNotifierProvider);
        if (t.status == TecnicoAuthStatus.checking) return null;
        final publicTecnico = loc.startsWith('/tecnico/login') ||
            loc.startsWith('/tecnico/recuperar') ||
            loc.startsWith('/tecnico/splash');
        if (t.isAuthenticated) {
          if (publicTecnico && !loc.startsWith('/tecnico/splash')) {
            return '/tecnico/app/inicio';
          }
          return null;
        }
        if (loc.startsWith('/tecnico/app')) return '/tecnico/login';
        return null;
      }

      final auth = ref.read(clientAuthNotifierProvider);
      if (auth.status == ClientAuthStatus.checking) return null;

      final publicAuth = loc.startsWith('/cliente/login') ||
          loc.startsWith('/cliente/registro') ||
          loc.startsWith('/cliente/recuperar');

      if (auth.isAuthenticated) {
        if (publicAuth) return '/cliente/app/home';
        return null;
      }

      if (loc.startsWith('/cliente/app')) return '/cliente/login';
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (context, state) => const SplashScreen(),
      ),
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(
        path: '/modo',
        builder: (context, state) => const ActorSelectScreen(),
      ),
      GoRoute(
        path: '/cliente/login',
        builder: (context, state) => const ClienteLoginScreen(),
      ),
      GoRoute(
        path: '/cliente/registro',
        builder: (context, state) => const ClienteRegisterScreen(),
      ),
      GoRoute(
        path: '/cliente/recuperar',
        builder: (context, state) => const ClienteRecoverScreen(),
      ),
      GoRoute(
        path: '/tecnico/splash',
        builder: (context, state) => const TecnicoSplashScreen(),
      ),
      GoRoute(
        path: '/tecnico/login',
        builder: (context, state) => const TecnicoLoginScreen(),
      ),
      GoRoute(
        path: '/tecnico/recuperar',
        builder: (context, state) => const TecnicoRecoverScreen(),
      ),
      ShellRoute(
        builder: (context, state, child) => TecnicoAppShell(child: child),
        routes: [
          GoRoute(
            path: '/tecnico/app/inicio',
            builder: (context, state) => const TecnicoHomeScreen(),
          ),
          GoRoute(
            path: '/tecnico/app/servicios',
            builder: (context, state) => Scaffold(
              appBar: AppBar(title: const Text('Servicios asignados')),
              body: const TecnicoPlaceholderScreen(
                title: '',
                message:
                    'Esta funcionalidad será habilitada en ciclos posteriores. '
                    'Aquí verás servicios asignados a tu cuenta.',
                icon: Icons.assignment_outlined,
              ),
            ),
          ),
          GoRoute(
            path: '/tecnico/app/historial',
            builder: (context, state) => Scaffold(
              appBar: AppBar(
                title: const Text('Historial'),
                leading: BackButton(onPressed: () => context.pop()),
              ),
              body: const TecnicoPlaceholderScreen(
                title: '',
                message:
                    'Próximamente podrás revisar el historial de atenciones desde esta pantalla.',
                icon: Icons.history_rounded,
              ),
            ),
          ),
          GoRoute(
            path: '/tecnico/app/perfil',
            builder: (context, state) => const TecnicoPerfilScreen(),
          ),
        ],
      ),
      ShellRoute(
        builder: (context, state, child) => ClienteAppShell(child: child),
        routes: [
          GoRoute(
            path: '/cliente/app/home',
            builder: (context, state) => const ClienteHomeScreen(),
          ),
          GoRoute(
            path: '/cliente/app/vehiculos/nuevo',
            builder: (context, state) => const ClienteVehiculoFormScreen(),
          ),
          GoRoute(
            path: '/cliente/app/vehiculos/:vid/editar',
            builder: (context, state) {
              final id = int.tryParse(state.pathParameters['vid'] ?? '');
              if (id == null) return const SizedBox.shrink();
              return ClienteVehiculoFormScreen(vehiculoId: id);
            },
          ),
          GoRoute(
            path: '/cliente/app/vehiculos/:vid',
            builder: (context, state) {
              final id = int.tryParse(state.pathParameters['vid'] ?? '');
              if (id == null) return const SizedBox.shrink();
              return ClienteVehiculoDetailScreen(vehiculoId: id);
            },
          ),
          GoRoute(
            path: '/cliente/app/vehiculos',
            builder: (context, state) => const ClienteVehiculosListScreen(),
          ),
          GoRoute(
            path: '/cliente/app/perfil',
            builder: (context, state) => const ClientePerfilScreen(),
          ),
        ],
      ),
    ],
    debugLogDiagnostics: kDebugMode,
  );
});
