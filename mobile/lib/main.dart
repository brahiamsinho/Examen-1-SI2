// lib/main.dart
// =========================================================
// Punto de entrada de la app Flutter
// =========================================================
import 'package:flutter/material.dart';
import 'core/theme/app_theme.dart';

void main() {
  runApp(const EmergenciasApp());
}

class EmergenciasApp extends StatelessWidget {
  const EmergenciasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Emergencias Vehiculares',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      // TODO: Agregar go_router para navegación declarativa
      home: const Scaffold(
        body: Center(
          child: Text(
            '🚗 Plataforma Emergencias Vehiculares',
            style: TextStyle(fontSize: 20),
          ),
        ),
      ),
    );
  }
}
