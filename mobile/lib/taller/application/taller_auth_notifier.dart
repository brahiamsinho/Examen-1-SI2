import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/taller_auth_repository.dart';
import '../domain/models/taller_perfil.dart';
import 'taller_auth_state.dart';
import 'taller_injection.dart';

final class TallerAuthNotifier extends Notifier<TallerAuthState> {
  @override
  TallerAuthState build() {
    Future.microtask(_bootstrap);
    return const TallerAuthState.checking();
  }

  Future<void> _bootstrap() async {
    final repo = ref.read(tallerAuthRepositoryProvider);
    final token = await repo.readAccessToken();
    if (token == null || token.isEmpty) {
      state = const TallerAuthState(status: TallerAuthStatus.guest);
      return;
    }
    try {
      final me = await repo.fetchMe();
      if (!TallerAuthRepository.rolesPermitidosTallerApp(me.roles)) {
        await repo.logoutLocal();
        state = const TallerAuthState(status: TallerAuthStatus.guest);
        return;
      }
      final perfil = await repo.fetchPerfilCompleto(me);
      state = TallerAuthState(status: TallerAuthStatus.authenticated, perfil: perfil);
    } catch (_) {
      await repo.logoutLocal();
      state = const TallerAuthState(status: TallerAuthStatus.guest);
    }
  }

  Future<void> login({
    required String email,
    required String password,
    String? tenantSlug,
  }) async {
    state = state.copyWith(isLoggingIn: true, clearError: true);
    final repo = ref.read(tallerAuthRepositoryProvider);
    try {
      final me = await repo.login(
        email: email,
        password: password,
        tenantSlug: tenantSlug,
      );
      final perfil = await repo.fetchPerfilCompleto(me);
      state = TallerAuthState(
        status: TallerAuthStatus.authenticated,
        perfil: perfil,
      );
    } catch (e) {
      state = TallerAuthState(
        status: TallerAuthStatus.guest,
        authError: e.toString().replaceFirst('Exception: ', ''),
        isLoggingIn: false,
      );
    }
  }

  Future<void> logout() async {
    final repo = ref.read(tallerAuthRepositoryProvider);
    await repo.logout();
    state = const TallerAuthState(status: TallerAuthStatus.guest);
  }

  void clearError() {
    state = state.copyWith(clearError: true);
  }

  void replacePerfil(TallerPerfil perfil) {
    if (!state.isAuthenticated) return;
    state = TallerAuthState(status: TallerAuthStatus.authenticated, perfil: perfil);
  }
}
