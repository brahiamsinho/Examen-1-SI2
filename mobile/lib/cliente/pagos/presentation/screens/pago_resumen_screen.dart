import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../../emergencias/application/emergencias_providers.dart';
import '../../domain/pago_eligibility.dart';
import '../../domain/pago_models.dart';
import '../widgets/resumen_cobro_card.dart';

/// Paso 1 — monto a pagar + contexto de la solicitud.
class PagoResumenScreen extends ConsumerStatefulWidget {
  const PagoResumenScreen({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  ConsumerState<PagoResumenScreen> createState() => _PagoResumenScreenState();
}

class _PagoResumenScreenState extends ConsumerState<PagoResumenScreen> {
  final _montoCtrl = TextEditingController();

  @override
  void dispose() {
    _montoCtrl.dispose();
    super.dispose();
  }

  void _continuar() {
    final t = _montoCtrl.text.trim().replaceAll(',', '.');
    if (double.tryParse(t) == null || double.parse(t) <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ingresá un monto válido mayor a cero.')),
      );
      return;
    }
    final draft = PagoDraft(solicitudId: widget.solicitudId, montoTexto: t);
    context.push('/cliente/app/emergencias/solicitudes/${widget.solicitudId}/pago/metodo', extra: draft);
  }

  @override
  Widget build(BuildContext context) {
    final async = ref.watch(emergenciaDetailProvider(widget.solicitudId));
    final theme = ShadTheme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Pagar servicio'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.canPop() ? context.pop() : context.go('/cliente/app/emergencias/solicitudes/${widget.solicitudId}'),
        ),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Padding(padding: const EdgeInsets.all(24), child: Text(e.toString()))),
        data: (d) {
          if (!solicitudPermitePago(d.estado)) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'En este estado la solicitud no admite pago desde la app.',
                      textAlign: TextAlign.center,
                      style: theme.textTheme.large,
                    ),
                    const SizedBox(height: 16),
                    ShadButton.outline(
                      onPressed: () => context.pop(),
                      child: const Text('Volver'),
                    ),
                  ],
                ),
              ),
            );
          }

          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              ResumenCobroCard(
                solicitudId: widget.solicitudId,
                estado: d.estado,
              ),
              const SizedBox(height: 20),
              Text('Monto a pagar', style: theme.textTheme.large),
              const SizedBox(height: 8),
              ShadInput(
                controller: _montoCtrl,
                placeholder: const Text('Ej. 150.00'),
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
              ),
              const SizedBox(height: 8),
              Text('Moneda por defecto: BOB (según backend).', style: theme.textTheme.muted),
              const SizedBox(height: 28),
              ShadButton(
                onPressed: _continuar,
                child: const Text('Continuar'),
              ),
              const SizedBox(height: 12),
              ShadButton.outline(
                onPressed: () => context.push('/cliente/app/emergencias/solicitudes/${widget.solicitudId}/pagos'),
                child: const Text('Ver historial de pagos'),
              ),
            ],
          );
        },
      ),
    );
  }
}
