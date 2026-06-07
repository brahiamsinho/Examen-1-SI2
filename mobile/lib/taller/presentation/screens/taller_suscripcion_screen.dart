import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/bolivia_time.dart';
import '../../application/taller_injection.dart';
import 'taller_module_ui.dart';

class TallerSuscripcionScreen extends ConsumerWidget {
  const TallerSuscripcionScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(tallerSuscripcionProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Suscripción SaaS'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: async.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => TallerModuleError(
          message: e.toString().replaceFirst('Exception: ', ''),
          onRetry: () => ref.invalidate(tallerSuscripcionProvider),
        ),
        data: (s) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            TallerModuleCard(
              title: 'Organización',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(s.tenantNombre, style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text('Plan: ${s.planName}'),
                  Text('Estado: ${s.subscriptionStatus}'),
                  if (s.subscriptionEndsAt != null)
                    Text('Vence: ${BoliviaTime.formatWithZone(s.subscriptionEndsAt!)}'),
                ],
              ),
            ),
            const SizedBox(height: 16),
            TallerModuleCard(
              title: 'Upgrade con Stripe',
              child: Text(
                s.stripeEnabled
                    ? 'Para cambiar de plan o pagar con tarjeta, usá el portal web (/taller/panel/suscripcion) donde está el checkout Stripe completo.'
                    : 'Stripe no está habilitado en este entorno. El plan se gestiona desde administración de la plataforma.',
              ),
            ),
          ],
        ),
      ),
    );
  }
}
