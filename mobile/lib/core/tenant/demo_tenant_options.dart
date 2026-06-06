/// Organizaciones demo disponibles en desarrollo (alineado con seeds backend).
class DemoTenantOption {
  const DemoTenantOption({
    required this.slug,
    required this.label,
    required this.subtitle,
    this.plan,
  });

  final String slug;
  final String label;
  final String subtitle;
  final String? plan;
}

const demoTenantOptions = <DemoTenantOption>[
  DemoTenantOption(
    slug: 'demo-sc',
    label: 'Santa Cruz demo',
    subtitle: 'Organización principal · clientes y talleres SC',
    plan: 'Legacy',
  ),
  DemoTenantOption(
    slug: 'org-free-equipetrol',
    label: 'Equipetrol Express',
    subtitle: 'Plan Free · zona Equipetrol',
    plan: 'Free',
  ),
  DemoTenantOption(
    slug: 'org-free-urbari',
    label: 'Urbari Mecánica',
    subtitle: 'Plan Free · zona norte',
    plan: 'Free',
  ),
  DemoTenantOption(
    slug: 'org-pro-anillo',
    label: '4to Anillo Pro',
    subtitle: 'Plan Pro · auxilio vial',
    plan: 'Pro',
  ),
  DemoTenantOption(
    slug: 'org-pro-plan3000',
    label: 'Plan 3000 Pro',
    subtitle: 'Plan Pro · mecánica general',
    plan: 'Pro',
  ),
  DemoTenantOption(
    slug: 'org-max-centro',
    label: 'Centro Max SC',
    subtitle: 'Plan Max · centro ciudad',
    plan: 'Max',
  ),
  DemoTenantOption(
    slug: 'org-max-el-torno',
    label: 'El Torno Max',
    subtitle: 'Plan Max · cobertura extendida',
    plan: 'Max',
  ),
];

DemoTenantOption? findDemoTenant(String slug) {
  final s = slug.trim().toLowerCase();
  for (final o in demoTenantOptions) {
    if (o.slug == s) return o;
  }
  return null;
}
