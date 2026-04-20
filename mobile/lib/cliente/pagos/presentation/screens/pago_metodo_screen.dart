import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

import '../../domain/pago_models.dart';
import '../widgets/metodo_pago_selector.dart';

/// Paso 2 — método de pago. Recibe [PagoDraft] en `extra` (monto ya definido).
class PagoMetodoScreen extends StatefulWidget {
  const PagoMetodoScreen({super.key, required this.solicitudId, required this.draft});

  final int solicitudId;
  final PagoDraft draft;

  @override
  State<PagoMetodoScreen> createState() => _PagoMetodoScreenState();
}

class _PagoMetodoScreenState extends State<PagoMetodoScreen> {
  MetodoPago? _metodo;

  @override
  Widget build(BuildContext context) {
    final theme = ShadTheme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Método de pago'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          Text('Monto: ${widget.draft.montoTexto} BOB', style: theme.textTheme.large),
          const SizedBox(height: 20),
          MetodoPagoSelector(
            valor: _metodo,
            onChanged: (m) => setState(() => _metodo = m),
          ),
          const SizedBox(height: 28),
          ShadButton(
            onPressed: _metodo == null
                ? null
                : () {
                    final next = widget.draft.copyWith(metodo: _metodo);
                    context.push(
                      '/cliente/app/emergencias/solicitudes/${widget.solicitudId}/pago/confirmar',
                      extra: next,
                    );
                  },
            child: const Text('Revisar y confirmar'),
          ),
        ],
      ),
    );
  }
}
