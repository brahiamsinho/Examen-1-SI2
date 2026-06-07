import 'dart:io';

import 'package:path_provider/path_provider.dart';

/// Copia evidencia temporal a almacenamiento persistente del borrador offline.
Future<String> persistOfflineEvidenceFile(String sourcePath, {required String prefix}) async {
  final src = File(sourcePath);
  if (!await src.exists()) return sourcePath;

  final docs = await getApplicationDocumentsDirectory();
  final dir = Directory('${docs.path}/offline_drafts');
  if (!await dir.exists()) {
    await dir.create(recursive: true);
  }

  final dot = sourcePath.lastIndexOf('.');
  final ext = dot >= 0 ? sourcePath.substring(dot) : '';
  final name = '${prefix}_${DateTime.now().millisecondsSinceEpoch}$ext';
  final dest = File('${dir.path}/$name');
  await src.copy(dest.path);
  return dest.path;
}
