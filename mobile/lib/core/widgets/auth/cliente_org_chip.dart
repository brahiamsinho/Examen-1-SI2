import 'package:flutter/material.dart';

import '../../tenant/demo_tenant_options.dart';
import '../../theme/mobile_auth_theme.dart';
import 'org_slug_selector.dart';

/// Chip compacto de org activa (panel cliente).
class ClienteOrgChip extends StatelessWidget {
  const ClienteOrgChip({
    super.key,
    required this.slug,
    required this.onChanged,
  });

  final String slug;
  final ValueChanged<String> onChanged;

  @override
  Widget build(BuildContext context) {
    final opt = findDemoTenant(slug);
    final label = opt?.label ?? slug;
    final cs = Theme.of(context).colorScheme;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _openPicker(context),
        borderRadius: BorderRadius.circular(999),
        child: Ink(
          decoration: BoxDecoration(
            color: MobileAuthTheme.inputFill,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: MobileAuthTheme.borderColor),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.apartment_rounded, size: 16, color: cs.primary),
                const SizedBox(width: 6),
                Flexible(
                  child: Text(
                    label,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  ),
                ),
                const SizedBox(width: 4),
                Icon(Icons.expand_more_rounded, size: 18, color: cs.onSurface.withValues(alpha: 0.55)),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _openPicker(BuildContext context) async {
    final picked = await showOrgSlugPicker(context, current: slug);
    if (picked != null && picked != slug) onChanged(picked);
  }
}
