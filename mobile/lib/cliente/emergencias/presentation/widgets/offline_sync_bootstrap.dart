import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../application/offline_sync_providers.dart';
import '../../../application/client_auth_provider.dart';

/// Inicia el orquestador CU43 al entrar al área autenticada del cliente.
class OfflineSyncBootstrap extends ConsumerStatefulWidget {
  const OfflineSyncBootstrap({super.key, required this.child});

  final Widget child;

  @override
  ConsumerState<OfflineSyncBootstrap> createState() => _OfflineSyncBootstrapState();
}

class _OfflineSyncBootstrapState extends ConsumerState<OfflineSyncBootstrap> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(syncOrquestadorProvider).start();
    });
  }

  @override
  Widget build(BuildContext context) {
    ref.listen(clientAuthNotifierProvider, (prev, next) {
      if (next.isAuthenticated && (prev == null || !prev.isAuthenticated)) {
        ref.read(syncOrquestadorProvider).resumeAfterLogin();
      }
    });
    return widget.child;
  }
}
