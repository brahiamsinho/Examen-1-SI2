import 'package:flutter/foundation.dart';

import '../domain/models/cliente_mi_perfil.dart';

/// Estado de sesión del **cliente móvil** (ciclo 1).
enum ClientAuthStatus {
  /// Restaurando token / perfil al arranque.
  checking,

  /// Sin sesión válida.
  guest,

  /// Token válido y perfil cliente cargado.
  authenticated,
}

@immutable
final class ClientAuthState {
  const ClientAuthState({
    required this.status,
    this.profile,
    this.authError,
    this.isLoggingIn = false,
  });

  const ClientAuthState.checking()
      : status = ClientAuthStatus.checking,
        profile = null,
        authError = null,
        isLoggingIn = false;

  final ClientAuthStatus status;
  final ClienteMiPerfil? profile;
  final String? authError;
  final bool isLoggingIn;

  bool get isAuthenticated => status == ClientAuthStatus.authenticated && profile != null;

  ClientAuthState copyWith({
    ClientAuthStatus? status,
    ClienteMiPerfil? profile,
    String? authError,
    bool clearError = false,
    bool? isLoggingIn,
  }) {
    return ClientAuthState(
      status: status ?? this.status,
      profile: profile ?? this.profile,
      authError: clearError ? null : (authError ?? this.authError),
      isLoggingIn: isLoggingIn ?? this.isLoggingIn,
    );
  }
}
