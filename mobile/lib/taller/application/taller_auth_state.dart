import 'package:flutter/foundation.dart';

import '../domain/models/taller_perfil.dart';

enum TallerAuthStatus {
  checking,
  guest,
  authenticated,
}

@immutable
final class TallerAuthState {
  const TallerAuthState({
    required this.status,
    this.perfil,
    this.authError,
    this.isLoggingIn = false,
  });

  const TallerAuthState.checking()
      : status = TallerAuthStatus.checking,
        perfil = null,
        authError = null,
        isLoggingIn = false;

  final TallerAuthStatus status;
  final TallerPerfil? perfil;
  final String? authError;
  final bool isLoggingIn;

  bool get isAuthenticated => status == TallerAuthStatus.authenticated && perfil != null;

  TallerAuthState copyWith({
    TallerAuthStatus? status,
    TallerPerfil? perfil,
    String? authError,
    bool clearError = false,
    bool? isLoggingIn,
  }) {
    return TallerAuthState(
      status: status ?? this.status,
      perfil: perfil ?? this.perfil,
      authError: clearError ? null : (authError ?? this.authError),
      isLoggingIn: isLoggingIn ?? this.isLoggingIn,
    );
  }
}
