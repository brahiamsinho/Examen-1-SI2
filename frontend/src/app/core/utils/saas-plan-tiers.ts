import type { PlanTenant } from '../models/admin-api.models';

/** Slugs comerciales (pricing_plans + portal taller). */
export type CommercialPlanSlug = 'free' | 'pro' | 'max';

export interface CommercialPlanOption {
  slug: CommercialPlanSlug;
  name: string;
  priceLabel: string;
  description: string;
}

/** Fallback si no carga el catálogo admin. */
export const DEFAULT_COMMERCIAL_PLANS: CommercialPlanOption[] = [
  {
    slug: 'free',
    name: 'Free',
    priceLabel: 'Gratis',
    description: 'Prueba y desarrollo — 1 organización.',
  },
  {
    slug: 'pro',
    name: 'Pro',
    priceLabel: 'BOB 299 / mes',
    description: 'Operación real con finanzas y multi-tenant.',
  },
  {
    slug: 'max',
    name: 'Max',
    priceLabel: 'BOB 599 / mes',
    description: 'Escala regional y facturación avanzada.',
  },
];

const PLAN_TO_SLUG: Record<PlanTenant, CommercialPlanSlug> = {
  FREE: 'free',
  STARTER: 'free',
  PRO: 'pro',
  ENTERPRISE: 'max',
};

const SLUG_TO_PLAN: Record<CommercialPlanSlug, PlanTenant> = {
  free: 'FREE',
  pro: 'PRO',
  max: 'ENTERPRISE',
};

export function planTenantToCommercialSlug(plan: PlanTenant): CommercialPlanSlug {
  return PLAN_TO_SLUG[plan] ?? 'free';
}

export function commercialSlugToPlanTenant(slug: CommercialPlanSlug): PlanTenant {
  return SLUG_TO_PLAN[slug] ?? 'FREE';
}

export function commercialPlanDisplayName(plan: PlanTenant): string {
  const slug = planTenantToCommercialSlug(plan);
  return DEFAULT_COMMERCIAL_PLANS.find((p) => p.slug === slug)?.name ?? slug;
}

export function formatPlanPrice(priceBob: number, currency = 'BOB'): string {
  if (!priceBob || priceBob <= 0) return 'Gratis';
  return `${currency} ${priceBob} / mes`;
}
