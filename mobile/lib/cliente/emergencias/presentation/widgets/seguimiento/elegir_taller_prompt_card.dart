import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:shadcn_ui/shadcn_ui.dart';

/// Aviso + CTA cuando la solicitud aún no tiene taller (CU37).
class ElegirTallerPromptCard extends StatelessWidget {
  const ElegirTallerPromptCard({super.key, required this.solicitudId});

  final int solicitudId;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ShadCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Icon(Icons.store_outlined, color: scheme.primary),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Todavía no elegiste taller. Elegí uno para que reciba tu solicitud en su bandeja.',
                    style: TextStyle(color: scheme.onSurfaceVariant, height: 1.4),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ShadButton(
              onPressed: () =>
                  context.push('/cliente/app/emergencias/solicitudes/$solicitudId/seleccionar-taller'),
              leading: const Icon(Icons.search_rounded, size: 20),
              child: const Text('Elegir taller'),
            ),
          ],
        ),
      ),
    );
  }
}
