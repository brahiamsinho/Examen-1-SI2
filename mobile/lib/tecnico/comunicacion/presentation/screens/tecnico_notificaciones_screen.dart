import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../cliente/comunicacion/presentation/widgets/notificacion_list_item.dart';
import '../application/tecnico_comunicacion_providers.dart';

class TecnicoNotificacionesScreen extends ConsumerStatefulWidget {
  const TecnicoNotificacionesScreen({super.key});

  @override
  ConsumerState<TecnicoNotificacionesScreen> createState() => _TecnicoNotificacionesScreenState();
}

class _TecnicoNotificacionesScreenState extends ConsumerState<TecnicoNotificacionesScreen> {
  bool _soloNoLeidas = false;

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(notificacionesTecnicoProvider(_soloNoLeidas));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Notificaciones'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.canPop() ? context.pop() : context.go('/tecnico/app/inicio'),
        ),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
            child: Row(
              children: [
                FilterChip(
                  label: const Text('Todas'),
                  selected: !_soloNoLeidas,
                  onSelected: (_) => setState(() => _soloNoLeidas = false),
                ),
                const SizedBox(width: 8),
                FilterChip(
                  label: const Text('No leídas'),
                  selected: _soloNoLeidas,
                  onSelected: (_) => setState(() => _soloNoLeidas = true),
                ),
              ],
            ),
          ),
          Expanded(
            child: async.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Text(e.toString(), textAlign: TextAlign.center),
                ),
              ),
              data: (list) {
                if (list.isEmpty) {
                  return Center(
                    child: Text(
                      _soloNoLeidas
                          ? 'No tenés notificaciones sin leer.'
                          : 'Todavía no hay notificaciones.',
                    ),
                  );
                }
                return RefreshIndicator(
                  onRefresh: () => ref.refresh(notificacionesTecnicoProvider(_soloNoLeidas).future),
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    itemCount: list.length,
                    separatorBuilder: (_, __) => const Divider(height: 1),
                    itemBuilder: (context, i) {
                      final n = list[i];
                      return NotificacionListItem(
                        notificacion: n,
                        onTap: () async {
                          if (!n.leida) {
                            final repo = ref.read(tecnicoComunicacionRepositoryProvider);
                            await repo.marcarNotificacionLeida(n.id);
                            ref.invalidate(notificacionesTecnicoProvider(_soloNoLeidas));
                          }
                          if (n.solicitudId != null && context.mounted) {
                            context.push('/tecnico/app/servicios/${n.solicitudId}');
                          }
                        },
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
