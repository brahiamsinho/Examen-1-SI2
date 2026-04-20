import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

/// Vista de mapa con tiles de [OpenStreetMap](https://www.openstreetmap.org/) vía [flutter_map](https://pub.dev/packages/flutter_map).
class EmergenciaUbicacionOsmMap extends StatelessWidget {
  const EmergenciaUbicacionOsmMap({
    super.key,
    required this.latitude,
    required this.longitude,
    this.height = 220,
    this.initialZoom = 15,
  });

  final double latitude;
  final double longitude;
  final double height;
  final double initialZoom;

  static const _osmTemplate = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

  @override
  Widget build(BuildContext context) {
    final point = LatLng(latitude, longitude);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        SizedBox(
          height: height,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: FlutterMap(
              options: MapOptions(
                initialCenter: point,
                initialZoom: initialZoom,
                interactionOptions: const InteractionOptions(
                  flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
                ),
              ),
              children: [
                TileLayer(
                  urlTemplate: _osmTemplate,
                  userAgentPackageName: 'mobile_emergencias',
                ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: point,
                      width: 48,
                      height: 48,
                      alignment: Alignment.center,
                      child: const Icon(Icons.location_on, color: Color(0xFFE53935), size: 44),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Mapa © colaboradores de OpenStreetMap',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
