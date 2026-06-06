import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../core/theme/mobile_auth_theme.dart';
import '../../../core/widgets/auth/auth_screen_widgets.dart';
import '../../application/cliente_injection.dart';
import '../../application/vehiculos_providers.dart';
import '../../data/repositories/vehiculo_repository.dart';
import '../../domain/models/vehiculo_display.dart';
import '../widgets/cliente_panel_ui.dart';

class ClienteVehiculosListScreen extends ConsumerWidget {
  const ClienteVehiculosListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(vehiculosMineProvider);

    return ClientePanelBackground(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: ClientePanelUi.pagePadding.copyWith(bottom: 8),
            child: ClienteTabHeader(
              title: 'Mis vehículos',
              subtitle: 'Administra tu flota registrada',
              trailing: IconButton.filledTonal(
                onPressed: () => context.push('/cliente/app/vehiculos/nuevo'),
                icon: const Icon(Icons.add_rounded),
                tooltip: 'Registrar vehículo',
              ),
            ),
          ),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async => ref.invalidate(vehiculosMineProvider),
              child: async.when(
                loading: () => ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  children: const [
                    SizedBox(height: 120),
                    Center(child: CircularProgressIndicator()),
                  ],
                ),
                error: (e, _) => ListView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  padding: const EdgeInsets.all(24),
                  children: [
                    ClienteInfoBanner(
                      message: e.toString().replaceFirst('Exception: ', ''),
                      icon: Icons.error_outline_rounded,
                      tone: ClienteBannerTone.warning,
                    ),
                    const SizedBox(height: 16),
                    ShadButton(
                      onPressed: () => ref.invalidate(vehiculosMineProvider),
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
                data: (items) {
                  if (items.isEmpty) {
                    return ListView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      children: [
                        ClienteEmptyState(
                          icon: Icons.directions_car_outlined,
                          title: 'Aún no tienes vehículos',
                          message: 'Registra tu primer vehículo con placa, marca y modelo.',
                          actionLabel: 'Registrar vehículo',
                          onAction: () => context.push('/cliente/app/vehiculos/nuevo'),
                        ),
                      ],
                    );
                  }
                  return ListView.separated(
                    physics: const AlwaysScrollableScrollPhysics(),
                    padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (context, i) => _VehiculoCard(vehiculo: items[i]),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _VehiculoCard extends StatelessWidget {
  const _VehiculoCard({required this.vehiculo});

  final VehiculoDisplay vehiculo;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return DecoratedBox(
      decoration: MobileAuthTheme.cardDecoration(),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                DecoratedBox(
                  decoration: BoxDecoration(
                    color: MobileAuthTheme.accentIndigo.withValues(alpha: 0.18),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Padding(
                    padding: EdgeInsets.all(8),
                    child: Icon(Icons.directions_car_rounded, color: MobileAuthTheme.accentIndigo),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        vehiculo.placa,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w800,
                              letterSpacing: 1.1,
                            ),
                      ),
                      Text(
                        '${vehiculo.marcaNombre} · ${vehiculo.modeloNombre}',
                        style: TextStyle(color: cs.onSurface.withValues(alpha: 0.7)),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: cs.primary.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(vehiculo.tipoNombre, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
                ),
              ],
            ),
            if (vehiculo.anio != null || (vehiculo.color != null && vehiculo.color!.isNotEmpty)) ...[
              const SizedBox(height: 8),
              Text(
                [
                  if (vehiculo.anio != null) 'Año ${vehiculo.anio}',
                  if (vehiculo.color != null && vehiculo.color!.isNotEmpty) vehiculo.color!,
                ].join(' · '),
                style: TextStyle(color: cs.onSurface.withValues(alpha: 0.55), fontSize: 12),
              ),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                TextButton(onPressed: () => context.push('/cliente/app/vehiculos/${vehiculo.id}'), child: const Text('Ver')),
                TextButton(
                  onPressed: () => context.push('/cliente/app/vehiculos/${vehiculo.id}/editar'),
                  child: const Text('Editar'),
                ),
                TextButton(
                  onPressed: () => _confirmDeletePlaceholder(context),
                  child: Text('Eliminar', style: TextStyle(color: cs.error.withValues(alpha: 0.85))),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _confirmDeletePlaceholder(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: MobileAuthTheme.cardColor,
        title: const Text('Eliminar vehículo'),
        content: const Text(
          'La eliminación desde la app se habilitará cuando el backend exponga el endpoint. '
          'Por ahora puedes editar los datos del vehículo.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cerrar')),
        ],
      ),
    );
  }
}

class ClienteVehiculoDetailScreen extends ConsumerStatefulWidget {
  const ClienteVehiculoDetailScreen({super.key, required this.vehiculoId});

  final int vehiculoId;

  @override
  ConsumerState<ClienteVehiculoDetailScreen> createState() => _ClienteVehiculoDetailScreenState();
}

class _ClienteVehiculoDetailScreenState extends ConsumerState<ClienteVehiculoDetailScreen> {
  late Future<VehiculoDisplay> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _future = ref.read(vehiculoRepositoryProvider).fetchDisplay(widget.vehiculoId);
  }

  @override
  Widget build(BuildContext context) {
    return ClienteSubpageScaffold(
      title: 'Detalle vehículo',
      actions: [
        IconButton(
          icon: const Icon(Icons.edit_rounded),
          onPressed: () => context.push('/cliente/app/vehiculos/${widget.vehiculoId}/editar'),
        ),
      ],
      body: FutureBuilder<VehiculoDisplay>(
        future: _future,
        builder: (context, snap) {
          if (snap.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snap.hasError) {
            return ClienteEmptyState(
              icon: Icons.error_outline,
              title: 'No se pudo cargar',
              message: snap.error.toString(),
            );
          }
          final v = snap.data!;
          return ListView(
            padding: ClientePanelUi.pagePadding,
            children: [
              AuthFormCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      v.placa,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 16),
                    _DetailRow('Marca', v.marcaNombre),
                    _DetailRow('Modelo', v.modeloNombre),
                    _DetailRow('Tipo', v.tipoNombre),
                    if (v.anio != null) _DetailRow('Año', '${v.anio}'),
                    if (v.color != null && v.color!.isNotEmpty) _DetailRow('Color', v.color!),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              ShadButton(
                onPressed: () => context.push('/cliente/app/vehiculos/${widget.vehiculoId}/editar'),
                child: const Text('Editar vehículo'),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow(this.label, this.value);

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 88,
            child: Text(label, style: TextStyle(fontWeight: FontWeight.w600, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.65))),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

class ClienteVehiculoFormScreen extends ConsumerStatefulWidget {
  const ClienteVehiculoFormScreen({super.key, this.vehiculoId});

  final int? vehiculoId;

  @override
  ConsumerState<ClienteVehiculoFormScreen> createState() => _ClienteVehiculoFormScreenState();
}

class _ClienteVehiculoFormScreenState extends ConsumerState<ClienteVehiculoFormScreen> {
  final _placa = TextEditingController();
  final _anio = TextEditingController();
  final _color = TextEditingController();

  List<CatalogItem> _marcas = [];
  List<ModeloRow> _modelos = [];
  List<CatalogItem> _tipos = [];

  int? _marcaId;
  int? _modeloId;
  int? _tipoId;
  bool _loading = true;
  String? _error;

  bool get _isEdit => widget.vehiculoId != null;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    final repo = ref.read(vehiculoRepositoryProvider);
    try {
      final marcas = await repo.fetchMarcas();
      final tipos = await repo.fetchTipos();
      _marcas = marcas;
      _tipos = tipos;

      if (_isEdit) {
        final v = await repo.fetchDisplay(widget.vehiculoId!);
        _placa.text = v.placa;
        if (v.anio != null) _anio.text = '${v.anio}';
        _color.text = v.color ?? '';

        final marcaMatch = marcas.where((m) => m.nombre == v.marcaNombre).toList();
        if (marcaMatch.isNotEmpty) {
          _marcaId = marcaMatch.first.id;
          _modelos = await repo.fetchModelos(marcaId: _marcaId);
          final modeloMatch = _modelos.where((m) => m.nombre == v.modeloNombre).toList();
          if (modeloMatch.isNotEmpty) _modeloId = modeloMatch.first.id;
        }
        final tipoMatch = tipos.where((t) => t.nombre == v.tipoNombre).toList();
        if (tipoMatch.isNotEmpty) _tipoId = tipoMatch.first.id;
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _placa.dispose();
    _anio.dispose();
    _color.dispose();
    super.dispose();
  }

  Future<void> _onMarcaChanged(int? id) async {
    setState(() {
      _marcaId = id;
      _modeloId = null;
      _modelos = [];
    });
    if (id == null) return;
    final repo = ref.read(vehiculoRepositoryProvider);
    final m = await repo.fetchModelos(marcaId: id);
    setState(() => _modelos = m);
  }

  Future<void> _save() async {
    setState(() => _error = null);
    if (_marcaId == null || _modeloId == null || _tipoId == null || _placa.text.trim().isEmpty) {
      setState(() => _error = 'Completa placa, marca, modelo y tipo.');
      return;
    }
    int? anio;
    if (_anio.text.trim().isNotEmpty) {
      anio = int.tryParse(_anio.text.trim());
      if (anio == null) {
        setState(() => _error = 'Año inválido.');
        return;
      }
    }
    final repo = ref.read(vehiculoRepositoryProvider);
    try {
      if (_isEdit) {
        await repo.update(
          widget.vehiculoId!,
          placa: _placa.text,
          marcaId: _marcaId,
          modeloId: _modeloId,
          tipoVehiculoId: _tipoId,
          anio: anio,
          color: _color.text.trim().isEmpty ? null : _color.text.trim(),
        );
      } else {
        await repo.create(
          placa: _placa.text,
          marcaId: _marcaId!,
          modeloId: _modeloId!,
          tipoVehiculoId: _tipoId!,
          anio: anio,
          color: _color.text.trim().isEmpty ? null : _color.text.trim(),
        );
      }
      ref.invalidate(vehiculosMineProvider);
      if (mounted) context.pop();
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const ClienteSubpageScaffold(
        title: 'Cargando…',
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return ClienteSubpageScaffold(
      title: _isEdit ? 'Editar vehículo' : 'Registrar vehículo',
      body: ListView(
        padding: ClientePanelUi.pagePadding,
        children: [
          AuthFormCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const AuthFieldLabel('Placa'),
                ShadInput(controller: _placa, placeholder: const Text('ABC1234')),
                const SizedBox(height: 14),
                const AuthFieldLabel('Marca'),
                DropdownButtonFormField<int>(
                  // ignore: deprecated_member_use
                  value: _marcaId,
                  items: [
                    for (final m in _marcas) DropdownMenuItem(value: m.id, child: Text(m.nombre)),
                  ],
                  onChanged: _onMarcaChanged,
                  decoration: const InputDecoration(),
                ),
                const SizedBox(height: 14),
                const AuthFieldLabel('Modelo'),
                DropdownButtonFormField<int>(
                  // ignore: deprecated_member_use
                  value: _modeloId,
                  items: [
                    for (final m in _modelos) DropdownMenuItem(value: m.id, child: Text(m.nombre)),
                  ],
                  onChanged: (v) => setState(() => _modeloId = v),
                  decoration: const InputDecoration(),
                ),
                const SizedBox(height: 14),
                const AuthFieldLabel('Tipo de vehículo'),
                DropdownButtonFormField<int>(
                  // ignore: deprecated_member_use
                  value: _tipoId,
                  items: [
                    for (final t in _tipos) DropdownMenuItem(value: t.id, child: Text(t.nombre)),
                  ],
                  onChanged: (v) => setState(() => _tipoId = v),
                  decoration: const InputDecoration(),
                ),
                const SizedBox(height: 14),
                const AuthFieldLabel('Año (opcional)'),
                ShadInput(controller: _anio, placeholder: const Text('2020'), keyboardType: TextInputType.number),
                const SizedBox(height: 14),
                const AuthFieldLabel('Color (opcional)'),
                ShadInput(controller: _color, placeholder: const Text('Blanco')),
                if (_error != null) ...[
                  const SizedBox(height: 14),
                  AuthErrorBanner(message: _error!),
                ],
              ],
            ),
          ),
          const SizedBox(height: 20),
          ShadButton(onPressed: _save, child: Text(_isEdit ? 'Guardar cambios' : 'Guardar')),
        ],
      ),
    );
  }
}
