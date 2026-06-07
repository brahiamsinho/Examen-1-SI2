import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import 'taller_module_ui.dart';

class TallerBackupsScreen extends ConsumerStatefulWidget {
  const TallerBackupsScreen({super.key});

  @override
  ConsumerState<TallerBackupsScreen> createState() => _TallerBackupsScreenState();
}

class _TallerBackupsScreenState extends ConsumerState<TallerBackupsScreen> {
  bool _creating = false;

  Future<void> _crear() async {
    setState(() => _creating = true);
    try {
      await ref.read(tallerRepositoryProvider).createBackup();
      ref.invalidate(tallerBackupsProvider);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Backup iniciado. Actualizá la lista en unos segundos.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
        );
      }
    } finally {
      if (mounted) setState(() => _creating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(tallerBackupsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Backups'),
        leading: BackButton(onPressed: () => context.pop()),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(tallerBackupsProvider),
          ),
        ],
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(tallerBackupsProvider),
        ),
        data: (rows) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            ShadButton(
              width: double.infinity,
              onPressed: _creating ? null : _crear,
              child: Text(_creating ? 'Creando backup…' : 'Crear backup del taller'),
            ),
            const SizedBox(height: 8),
            const Text(
              'Descarga y restore completos están en el portal web. Aquí podés listar y generar respaldos.',
              style: TextStyle(fontSize: 13, height: 1.35),
            ),
            const SizedBox(height: 16),
            if (rows.isEmpty)
              const Text('Sin backups todavía.')
            else
              ...rows.map(
                (b) => Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: ListTile(
                    title: Text(b.archivo),
                    subtitle: Text('Estado: ${b.estado}'),
                    trailing: Text(BoliviaTime.format(b.creadoEn, pattern: 'dd/MM/yy')),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
