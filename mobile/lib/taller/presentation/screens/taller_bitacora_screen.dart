import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import 'taller_module_ui.dart';

class TallerBitacoraScreen extends ConsumerWidget {
  const TallerBitacoraScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerBitacoraProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Bitácora'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(tallerBitacoraProvider),
        ),
        data: (rows) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(tallerBitacoraProvider),
          child: rows.isEmpty
              ? ListView(
                  children: const [
                    SizedBox(height: 80),
                    Center(child: Text('Sin registros de auditoría.')),
                  ],
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: rows.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final b = rows[i];
                    return Card(
                      child: ListTile(
                        title: Text('${b.accion} · ${b.modulo}'),
                        subtitle: Text(
                          '${b.usuarioNombre ?? 'Sistema'} — ${b.descripcion ?? b.entidad}',
                        ),
                        trailing: Text(BoliviaTime.format(b.createdAt, pattern: 'dd/MM HH:mm')),
                      ),
                    );
                  },
                ),
        ),
      ),
    );
  }
}
