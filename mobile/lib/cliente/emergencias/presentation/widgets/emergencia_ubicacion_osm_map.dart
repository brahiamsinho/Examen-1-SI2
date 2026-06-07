import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

/// Vista de mapa con tiles de [OpenStreetMap](https://www.openstreetmap.org/) vía [flutter_map](https://pub.dev/packages/flutter_map).
///
/// Soporta polyline de ruta VRT (OSRM) o segmento recto entre dos puntos.
class EmergenciaUbicacionOsmMap extends StatelessWidget {
  const EmergenciaUbicacionOsmMap({
    super.key,
    required this.latitude,
    required this.longitude,
    this.routeToLatitude,
    this.routeToLongitude,
    this.routePoints,
    this.height = 220,
    this.initialZoom = 15,
    this.routeLabel,
  });

  final double latitude;
  final double longitude;
  /// Segundo extremo del segmento si no hay [routePoints].
  final double? routeToLatitude;
  final double? routeToLongitude;
  /// Polyline completa [[lat, lon], ...] desde backend (OSRM o fallback).
  final List<List<double>>? routePoints;
  final double height;
  final double initialZoom;
  final String? routeLabel;

  static const _osmTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  static const _routeColor = Color(0xFF1565C0);

  List<LatLng> get _polylinePoints {
    if (routePoints != null && routePoints!.length >= 2) {
      return routePoints!.map((p) => LatLng(p[0], p[1])).toList(growable: false);
    }
    if (routeToLatitude != null && routeToLongitude != null) {
      return [
        LatLng(latitude, longitude),
        LatLng(routeToLatitude!, routeToLongitude!),
      ];
    }
    return const [];
  }

  LatLng? get _destino =>
      routePoints != null && routePoints!.length >= 2
          ? LatLng(routePoints!.last[0], routePoints!.last[1])
          : (routeToLatitude != null && routeToLongitude != null
              ? LatLng(routeToLatitude!, routeToLongitude!)
              : null);

  @override
  Widget build(BuildContext context) {
    final origen = LatLng(latitude, longitude);
    final polyline = _polylinePoints;
    final destino = _destino;
    final tieneRuta = polyline.length >= 2;

    final MapOptions mapOptions;
    if (tieneRuta) {
      final bounds = LatLngBounds.fromPoints(polyline);
      mapOptions = MapOptions(
        initialCameraFit: CameraFit.bounds(
          bounds: bounds,
          padding: const EdgeInsets.fromLTRB(24, 24, 24, 48),
        ),
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
        ),
      );
    } else {
      mapOptions = MapOptions(
        initialCenter: origen,
        initialZoom: initialZoom,
        interactionOptions: const InteractionOptions(
          flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
        ),
      );
    }

    final markers = <Marker>[
      Marker(
        point: origen,
        width: 48,
        height: 48,
        alignment: Alignment.center,
        child: Icon(
          destino != null ? Icons.engineering : Icons.location_on,
          color: destino != null ? _routeColor : const Color(0xFFE53935),
          size: 44,
        ),
      ),
    ];
    if (destino != null) {
      markers.add(
        Marker(
          point: destino,
          width: 48,
          height: 48,
          alignment: Alignment.center,
          child: const Icon(Icons.location_on, color: Color(0xFFE53935), size: 44),
        ),
      );
    }

    final caption = routeLabel ??
        (tieneRuta
            ? 'Ruta técnico → cliente. Mapa © OpenStreetMap'
            : 'Mapa © colaboradores de OpenStreetMap');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          height: height,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: FlutterMap(
              options: mapOptions,
              children: [
                TileLayer(
                  urlTemplate: _osmTemplate,
                  userAgentPackageName: 'mobile_emergencias',
                ),
                if (tieneRuta)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: polyline,
                        strokeWidth: 5,
                        color: _routeColor.withValues(alpha: 0.9),
                      ),
                    ],
                  ),
                MarkerLayer(markers: markers),
              ],
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          caption,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
