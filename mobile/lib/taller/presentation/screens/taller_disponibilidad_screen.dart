import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../application/taller_injection.dart';
import '../../domain/models/taller_modulos_models.dart';
import 'taller_module_ui.dart';

class TallerDisponibilidadScreen extends ConsumerStatefulWidget {
  const TallerDisponibilidadScreen({super.key});

  @override
  ConsumerState<TallerDisponibilidadScreen> createState() => _TallerDisponibilidadScreenState();
}

class _TallerDisponibilidadScreenState extends ConsumerState<TallerDisponibilidadScreen> {
  bool _acepta = true;
  final _capacidad = TextEditingController(text: '10');
  final _obs = TextEditingController();
  bool _saving = false;
  bool _hydrated = false;
  String? _error;
  String? _ok;

  @override
  void dispose() {
    _capacidad.dispose();
    _obs.dispose();
    super.dispose();
  }

  void _syncFrom(TallerDisponibilidad d) {
    _acepta = d.aceptaNuevasSolicitudes;
    _capacidad.text = '${d.capacidadMaximaDiaria}';
    _obs.text = d.observacion ?? '';
  }

  Future<void> _guardar() async {
    final cap = int.tryParse(_capacidad.text.trim());
    if (cap == null || cap < 1 || cap > 500) {
      setState(() => _error = 'Capacidad diaria entre 1 y 500.');
      return;
    }
    setState(() {
      _saving = true;
      _error = null;
      _ok = null;
    });
    try {
      await ref.read(tallerRepositoryProvider).updateDisponibilidad(
            aceptaNuevasSolicitudes: _acepta,
            capacidadMaximaDiaria: cap,
            observacion: _obs.text,
          );
      ref.invalidate(tallerDisponibilidadProvider);
      if (mounted) setState(() => _ok = 'Disponibilidad actualizada.');
    } catch (e) {
      if (mounted) setState(() => _error = e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(tallerDisponibilidadProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Disponibilidad'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString(),
          onRetry: () => ref.invalidate(tallerDisponibilidadProvider),
        ),
        data: (d) {
          if (!_hydrated) {
            _syncFrom(d);
            _hydrated = true;
          }
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              TallerModuleCard(
                title: 'Aceptar nuevas solicitudes',
                child: SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text(_acepta ? 'Abierto a emergencias' : 'No acepta nuevas solicitudes'),
                  value: _acepta,
                  onChanged: _saving ? null : (v) => setState(() => _acepta = v),
                ),
              ),
              const SizedBox(height: 16),
              TallerModuleCard(
                title: 'Capacidad operativa',
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Servicios activos hoy: ${d.serviciosActivos}'),
                    const SizedBox(height: 12),
                    ShadInput(
                      controller: _capacidad,
                      keyboardType: TextInputType.number,
                      placeholder: const Text('Capacidad máxima diaria'),
                    ),
                    const SizedBox(height: 12),
                    ShadInput(
                      controller: _obs,
                      placeholder: const Text('Observación (opcional)'),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
              ],
              if (_ok != null) ...[
                const SizedBox(height: 12),
                Text(_ok!, style: TextStyle(color: Theme.of(context).colorScheme.primary)),
              ],
              const SizedBox(height: 20),
              ShadButton(
                width: double.infinity,
                onPressed: _saving ? null : _guardar,
                child: Text(_saving ? 'Guardando…' : 'Guardar cambios'),
              ),
            ],
          );
        },
      ),
    );
  }
}
