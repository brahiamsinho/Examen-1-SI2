import 'package:connectivity_plus/connectivity_plus.dart';

/// Indica si hay interfaz de red activa (no garantiza que el API responda).
final class NetworkReachability {
  NetworkReachability({Connectivity? connectivity})
      : _connectivity = connectivity ?? Connectivity();

  final Connectivity _connectivity;

  Future<bool> hasConnectivity() async {
    final results = await _connectivity.checkConnectivity();
    return results.any((r) => r != ConnectivityResult.none);
  }

  Stream<List<ConnectivityResult>> get onConnectivityChanged =>
      _connectivity.onConnectivityChanged;
}
