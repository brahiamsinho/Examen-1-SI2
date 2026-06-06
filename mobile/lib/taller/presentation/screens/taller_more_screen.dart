import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'taller_placeholder_screen.dart';

/// Módulos avanzados del portal web (referencia en mobile).
class TallerMoreScreen extends StatelessWidget {
  const TallerMoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Más módulos'),
        leading: BackButton(onPressed: () => context.pop()),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Estas funciones están completas en el portal web (/taller). '
            'En mobile priorizamos bandeja y equipo.',
            style: TextStyle(height: 1.4),
          ),
          const SizedBox(height: 16),
          _tile(context, 'Comisiones', Icons.payments_outlined, 'Liquidaciones y resumen financiero'),
          _tile(context, 'Disponibilidad', Icons.toggle_on_outlined, 'Capacidad y aceptación de nuevas solicitudes'),
          _tile(context, 'Historial', Icons.history_rounded, 'Atenciones cerradas del taller'),
          _tile(context, 'Reportes', Icons.analytics_outlined, 'Consultas QBE, voz y export Excel/PDF'),
          _tile(context, 'Suscripción SaaS', Icons.workspace_premium_outlined, 'Plan y upgrade Stripe'),
          _tile(context, 'Bitácora', Icons.receipt_long_outlined, 'Auditoría del equipo'),
          _tile(context, 'Backups', Icons.backup_outlined, 'Respaldo y restore del taller'),
        ],
      ),
    );
  }

  Widget _tile(BuildContext context, String title, IconData icon, String msg) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute<void>(
                builder: (_) => TallerPlaceholderScreen(
                  title: title,
                  message: '$msg\n\nAbrí http://localhost/taller/panel en el navegador para gestionarlo.',
                  icon: icon,
                ),
              ),
            );
          },
          child: ListTile(
            leading: Icon(icon),
            title: Text(title),
            trailing: const Icon(Icons.open_in_new_rounded, size: 18),
          ),
        ),
      ),
    );
  }
}
