import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

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
            'Módulos operativos del responsable de taller. '
            'Consumen la misma API que el portal web (/taller/panel).',
            style: TextStyle(height: 1.4),
          ),
          const SizedBox(height: 16),
          _tile(context, 'Comisiones', Icons.payments_outlined, '/taller/app/comisiones'),
          _tile(context, 'Disponibilidad', Icons.toggle_on_outlined, '/taller/app/disponibilidad'),
          _tile(context, 'Historial', Icons.history_rounded, '/taller/app/historial'),
          _tile(context, 'Reportes', Icons.analytics_outlined, '/taller/app/reportes'),
          _tile(context, 'Suscripción SaaS', Icons.workspace_premium_outlined, '/taller/app/suscripcion'),
          _tile(context, 'Bitácora', Icons.receipt_long_outlined, '/taller/app/bitacora'),
          _tile(context, 'Backups', Icons.backup_outlined, '/taller/app/backups'),
        ],
      ),
    );
  }

  Widget _tile(BuildContext context, String title, IconData icon, String route) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Material(
        color: Theme.of(context).colorScheme.surfaceContainerHighest.withValues(alpha: 0.45),
        borderRadius: BorderRadius.circular(12),
        child: ListTile(
          leading: Icon(icon),
          title: Text(title),
          trailing: const Icon(Icons.chevron_right_rounded),
          onTap: () => context.push(route),
        ),
      ),
    );
  }
}
