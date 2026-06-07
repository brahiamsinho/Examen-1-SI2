import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import 'taller_module_ui.dart';

class TallerHistorialScreen extends ConsumerWidget {
  const TallerHistorialScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerHistorialProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Historial'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(tallerHistorialProvider),
        ),
        data: (list) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(tallerHistorialProvider),
          child: list.isEmpty
              ? ListView(
                  children: const [
                    SizedBox(height: 80),
                    Center(child: Text('Sin atenciones registradas.')),
                  ],
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: list.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final h = list[i];
                    return Card(
                      child: ListTile(
                        title: Text('${h.placa} · #${h.solicitudId}'),
                        subtitle: Text('${h.clienteNombre}\nEstado: ${h.estado}'),
                        isThreeLine: true,
                        trailing: Text(
                          h.finalizadaAt != null
                              ? BoliviaTime.format(h.finalizadaAt!, pattern: 'dd/MM/yy')
                              : BoliviaTime.format(h.createdAt, pattern: 'dd/MM/yy'),
                        ),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
