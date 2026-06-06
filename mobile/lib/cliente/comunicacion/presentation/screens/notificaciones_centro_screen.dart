import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../presentation/widgets/cliente_panel_ui.dart';
import '../../application/comunicacion_providers.dart';
import '../widgets/notificacion_list_item.dart';

/// CU19 — centro de notificaciones.
class NotificacionesCentroScreen extends ConsumerStatefulWidget {
  const NotificacionesCentroScreen({super.key});

  @override
  ConsumerState<NotificacionesCentroScreen> createState() => _NotificacionesCentroScreenState();
}

class _NotificacionesCentroScreenState extends ConsumerState<NotificacionesCentroScreen> {
  bool _soloNoLeidas = false;

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(notificacionesClienteProvider(_soloNoLeidas));

    return ClienteSubpageScaffold(
      title: 'Notificaciones',
      onBack: () => context.canPop() ? context.pop() : context.go('/cliente/app/home'),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 8),
          ClienteFilterChips(
            options: const ['Todas', 'No leídas'],
            selectedIndex: _soloNoLeidas ? 1 : 0,
            onSelected: (i) => setState(() => _soloNoLeidas = i == 1),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: async.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => _ErrorCentro(
                message: e.toString(),
                onRetry: () => ref.invalidate(notificacionesClienteProvider(_soloNoLeidas)),
              ),
              data: (list) {
                if (list.isEmpty) {
                  return _EmptyCentro(soloNoLeidas: _soloNoLeidas);
                }
                return RefreshIndicator(
                  onRefresh: () => ref.refresh(notificacionesClienteProvider(_soloNoLeidas).future),
                  child: ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: list.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, i) {
                      final n = list[i];
                      return NotificacionListItem(
                        notificacion: n,
                        onTap: () => context.push('/cliente/app/notificaciones/${n.id}', extra: n),
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyCentro extends StatelessWidget {
  const _EmptyCentro({required this.soloNoLeidas});

  final bool soloNoLeidas;

  @override
  Widget build(BuildContext context) {
    return ClienteEmptyState(
      icon: Icons.notifications_none_rounded,
      title: soloNoLeidas ? 'No tenés notificaciones sin leer' : 'Todavía no hay notificaciones',
      message: 'Cuando haya novedades en tus solicitudes, las verás acá.',
    );
  }
}

class _ErrorCentro extends StatelessWidget {
  const _ErrorCentro({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return ClienteEmptyState(
      icon: Icons.error_outline,
      title: 'Error al cargar',
      message: message,
      actionLabel: 'Reintentar',
      onAction: onRetry,
    );
  }
}
