import 'package:flutter/material.dart';

import '../../tenant/demo_tenant_options.dart';
import '../../theme/mobile_auth_theme.dart';

/// Selector de organización (bottom sheet) — reemplaza campo texto libre en login.
class OrgSlugSelector extends StatelessWidget {
  const OrgSlugSelector({
    super.key,
    required this.value,
    required this.onChanged,
    this.label = 'Código de organización',
    this.hint = 'Elige la organización a la que perteneces',
  });

  final String value;
  final ValueChanged<String> onChanged;
  final String label;
  final String hint;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final cs = theme.colorScheme;
    final selected = findDemoTenant(value);
    final displayTitle = selected?.label ?? value;
    final displaySubtitle = selected?.subtitle ?? 'Código: $value';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          label,
          style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 8),
        Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => _openPicker(context),
            borderRadius: BorderRadius.circular(12),
            child: Ink(
              decoration: MobileAuthTheme.selectorFieldDecoration(),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                child: Row(
                  children: [
                    Icon(
                      Icons.apartment_rounded,
                      size: 22,
                      color: cs.onSurface.withValues(alpha: 0.55),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            displayTitle,
                            style: theme.textTheme.bodyLarge?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            displaySubtitle,
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: cs.onSurface.withValues(alpha: 0.62),
                              height: 1.3,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Icon(
                      Icons.expand_more_rounded,
                      color: cs.onSurface.withValues(alpha: 0.55),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        const SizedBox(height: 6),
        Text(
          hint,
          style: theme.textTheme.bodySmall?.copyWith(
            color: cs.onSurface.withValues(alpha: 0.5),
            height: 1.35,
          ),
        ),
      ],
    );
  }

  Future<void> _openPicker(BuildContext context) async {
    final picked = await showOrgSlugPicker(context, current: value);
    if (picked != null && picked != value) {
      onChanged(picked);
    }
  }

  /// Bottom sheet reutilizable (panel cliente, login, etc.).
  static Future<String?> showPicker(BuildContext context, {required String current}) {
    return showOrgSlugPicker(context, current: current);
  }
}

Future<String?> showOrgSlugPicker(BuildContext context, {required String current}) async {
  return showModalBottomSheet<String>(
    context: context,
    isScrollControlled: true,
    backgroundColor: MobileAuthTheme.cardColor,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) {
      final bottom = MediaQuery.viewInsetsOf(ctx).bottom;
      return Padding(
        padding: EdgeInsets.fromLTRB(20, 12, 20, 20 + bottom),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.white24,
                  borderRadius: BorderRadius.circular(99),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Selecciona tu organización',
              style: Theme.of(ctx).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
            ),
            const SizedBox(height: 4),
            Text(
              'El código se envía al iniciar sesión (multi-tenant SaaS).',
              style: Theme.of(ctx).textTheme.bodySmall?.copyWith(
                    color: Theme.of(ctx).colorScheme.onSurface.withValues(alpha: 0.65),
                  ),
            ),
            const SizedBox(height: 16),
            Flexible(
              child: ListView.separated(
                shrinkWrap: true,
                itemCount: demoTenantOptions.length,
                separatorBuilder: (_, __) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final opt = demoTenantOptions[index];
                  final isSelected = opt.slug == current.trim().toLowerCase();
                  return _OrgOptionTile(
                    option: opt,
                    selected: isSelected,
                    onTap: () => Navigator.of(context).pop(opt.slug),
                  );
                },
              ),
            ),
          ],
        ),
      );
    },
  );
}

class _OrgOptionTile extends StatelessWidget {
  const _OrgOptionTile({
    required this.option,
    required this.selected,
    required this.onTap,
  });

  final DemoTenantOption option;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return Material(
      color: selected
          ? MobileAuthTheme.accentIndigo.withValues(alpha: 0.18)
          : MobileAuthTheme.inputFill,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      option.label,
                      style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      option.subtitle,
                      style: TextStyle(
                        fontSize: 12,
                        color: cs.onSurface.withValues(alpha: 0.65),
                        height: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      option.slug,
                      style: TextStyle(
                        fontSize: 11,
                        fontFamily: 'monospace',
                        color: cs.onSurface.withValues(alpha: 0.45),
                      ),
                    ),
                  ],
                ),
              ),
              if (option.plan != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: cs.primary.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    option.plan!,
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                  ),
                ),
              if (selected) ...[
                const SizedBox(width: 8),
                Icon(Icons.check_circle_rounded, color: cs.primary, size: 22),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
