import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'taller_auth_notifier.dart';
import 'taller_auth_state.dart';

final tallerAuthNotifierProvider =
    NotifierProvider<TallerAuthNotifier, TallerAuthState>(TallerAuthNotifier.new);
