import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import 'taller_module_ui.dart';

class TallerComisionesScreen extends ConsumerWidget {
  const TallerComisionesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerComisionesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Comisiones'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(tallerComisionesProvider),
        ),
        data: (data) {
          final (resumen, rows) = data;
          return RefreshIndicator(
            onRefresh: () async => ref.invalidate(tallerComisionesProvider),
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                TallerModuleCard(
                  title: 'Resumen',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Registros: ${resumen.totalRegistros}'),
                      Text('Total servicios: ${tallerFormatBob(resumen.totalServicios)}'),
                      Text('Comisión plataforma: ${tallerFormatBob(resumen.totalComision)}'),
                      Text('Neto taller: ${tallerFormatBob(resumen.totalNeto)}',
                          style: const TextStyle(fontWeight: FontWeight.w700)),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
                Text('Detalle', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                if (rows.isEmpty)
                  const Text('Sin comisiones registradas aún.')
                else
                  ...rows.map(
                    (c) => Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        title: Text('Solicitud #${c.solicitudId} · ${c.estado}'),
                        subtitle: Text(
                          'Servicio ${tallerFormatBob(c.montoServicio)} · Neto ${tallerFormatBob(c.montoTallerNeto)}',
                        ),
                        trailing: Text(BoliviaTime.format(c.calculadoAt, pattern: 'dd/MM/yy')),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
