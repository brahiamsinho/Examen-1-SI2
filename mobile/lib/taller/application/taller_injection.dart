import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/network/taller_api_client.dart';
import '../data/taller_auth_repository.dart';
import '../data/taller_repository.dart';
import '../domain/models/bandeja_models.dart';
import '../domain/models/tecnico_portal_models.dart';
import '../domain/models/taller_dashboard.dart';

final tallerDioProvider = Provider<Dio>((ref) {
  return TallerApiClient().dio;
});

final tallerAuthRepositoryProvider = Provider<TallerAuthRepository>((ref) {
  return TallerAuthRepository(ref.watch(tallerDioProvider));
});

final tallerRepositoryProvider = Provider<TallerRepository>((ref) {
  return TallerRepository(ref.watch(tallerDioProvider));
});

final tallerDashboardProvider = FutureProvider<TallerDashboard>((ref) async {
  return ref.watch(tallerRepositoryProvider).fetchDashboard();
});

final tallerBandejaProvider = FutureProvider<List<BandejaIncidente>>((ref) async {
  return ref.watch(tallerRepositoryProvider).listBandejaDisponibles();
});

final tallerTecnicosProvider = FutureProvider<List<TecnicoPortal>>((ref) async {
  return ref.watch(tallerRepositoryProvider).listTecnicos();
});

final tallerBandejaDetalleProvider = FutureProvider.family<BandejaIncidente, int>((ref, bandejaId) async {
  return ref.watch(tallerRepositoryProvider).fetchBandejaDetalle(bandejaId);
});

final tallerAsignacionesProvider = FutureProvider.family<List<AsignacionTecnico>, int>((ref, solicitudId) async {
  return ref.watch(tallerRepositoryProvider).listAsignaciones(solicitudId);
});
