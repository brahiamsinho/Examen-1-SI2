import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { fromEvent, of } from 'rxjs';
import { catchError, throttleTime } from 'rxjs/operators';
import { PublicApiService } from '../../../core/services/public-api.service';

export interface LandingModuleCard {
  title: string;
  desc: string;
  badge: string;
  accent: 'cyan' | 'blue' | 'indigo' | 'violet' | 'red' | 'emerald' | 'yellow' | 'orange' | 'teal';
}

export interface LandingPricingPlan {
  id: string;
  slug: string;
  name: string;
  priceMonthly: number;
  description: string;
  benefits: string[];
  ctaLabel: string;
  ctaRouterLink?: string | null;
  ctaHref?: string | null;
  featured?: boolean;
  badge?: string | null;
  stripeCheckout?: boolean;
}

export interface LandingBentoCell {
  title: string;
  desc: string;
  size: 'wide' | 'tall' | 'normal';
  icon: 'map' | 'tenant' | 'roles' | 'api';
}

export interface HeroPreviewRow {
  label: string;
  sub: string;
  status: string;
  tone: 'warn' | 'ok' | 'info';
}

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LandingPageComponent implements OnInit {
  private readonly publicApi = inject(PublicApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  navScrolled = false;
  menuOpen = false;
  pricingLoading = true;
  stripeEnabled = false;
  checkoutModalOpen = false;
  checkoutEmail = '';
  checkoutBusy = false;
  checkoutError: string | null = null;
  checkoutPlan: LandingPricingPlan | null = null;

  pricingPlans: LandingPricingPlan[] = [];

  readonly heroImage =
    'https://images.unsplash.com/photo-1449965408869-eaa3f725e40f?auto=format&fit=crop&w=1200&q=80';

  readonly navLinks: { label: string; href: string }[] = [
    { label: 'Inicio', href: '#inicio' },
    { label: 'Producto', href: '#producto' },
    { label: 'Precios', href: '#precios' },
    { label: 'Accesos', href: '#portales' },
    { label: 'Contacto', href: '#contacto' },
  ];

  readonly stats = [
    { val: '4', label: 'Roles integrados' },
    { val: '9+', label: 'Módulos activos' },
    { val: '100%', label: 'Trazabilidad' },
  ];

  readonly stackPills = ['Angular', 'FastAPI', 'Flutter', 'PostgreSQL', 'Docker'];

  readonly heroPreviewRows: HeroPreviewRow[] = [
    { label: 'Emergencia #0842', sub: 'Cliente · Av. Banzer Km 8', status: 'EN RUTA', tone: 'info' },
    { label: 'Taller asignado', sub: 'Mecánica Express · ETA 8 min', status: 'ACTIVO', tone: 'ok' },
    { label: 'Caso cerrado', sub: 'Valoración 5★ · Bitácora OK', status: 'LISTO', tone: 'ok' },
  ];

  readonly bentoCells: LandingBentoCell[] = [
    {
      title: 'Seguimiento en mapa',
      desc: 'ETA, técnico en ruta y visibilidad para cliente y taller en un solo flujo.',
      size: 'wide',
      icon: 'map',
    },
    {
      title: 'Multi-tenant SaaS',
      desc: 'Cada organización con slug propio; clientes móviles usan X-Tenant-Slug.',
      size: 'normal',
      icon: 'tenant',
    },
    {
      title: 'Roles y permisos',
      desc: 'Cliente, técnico, responsable de taller y admin de plataforma.',
      size: 'normal',
      icon: 'roles',
    },
    {
      title: 'API unificada',
      desc: 'Angular para taller/admin y Flutter para campo — misma API REST.',
      size: 'tall',
      icon: 'api',
    },
  ];

  private readonly fallbackPricingPlans: LandingPricingPlan[] = [
    {
      id: 'free',
      slug: 'free',
      name: 'Free',
      priceMonthly: 0,
      description: 'Prueba el flujo completo con un taller en entorno de desarrollo.',
      benefits: [
        '1 organización / slug',
        'Hasta 2 técnicos activos',
        'Emergencias y bandeja',
        'App móvil cliente y técnico',
        'Documentación',
      ],
      ctaLabel: 'Empezar gratis',
      ctaRouterLink: '/taller/registro',
    },
    {
      id: 'pro',
      slug: 'pro',
      name: 'Pro',
      priceMonthly: 299,
      description: 'Operación real con finanzas, admin y multi-tenant.',
      benefits: [
        'Slug y organización propia',
        'Técnicos y talleres ilimitados',
        'Panel admin + portal taller',
        'Finanzas y comisiones',
        'Bitácora y roles avanzados',
      ],
      ctaLabel: 'Contratar Pro',
      ctaRouterLink: '/taller/registro',
      featured: true,
      badge: 'Recomendado',
    },
    {
      id: 'max',
      slug: 'max',
      name: 'Max',
      priceMonthly: 599,
      description: 'Escala regional, B2B y facturación avanzada.',
      benefits: [
        'Todo lo de Pro',
        'Múltiples organizaciones',
        'KPIs y reportes extendidos',
        'Stripe / billing SaaS',
        'Soporte prioritario',
      ],
      ctaLabel: 'Contactar',
      ctaHref: '#contacto',
    },
  ];

  readonly modules: LandingModuleCard[] = [
    {
      title: 'Acceso y Seguridad',
      desc: 'Autenticación, sesiones y permisos granulares.',
      badge: 'Core',
      accent: 'cyan',
    },
    {
      title: 'Usuarios y Roles',
      desc: 'Perfiles de cliente, técnico, taller y admin.',
      badge: 'IAM',
      accent: 'blue',
    },
    {
      title: 'Talleres y Técnicos',
      desc: 'Alta de talleres, cobertura y asignación.',
      badge: 'Ops',
      accent: 'indigo',
    },
    {
      title: 'Vehículos',
      desc: 'Fichas técnicas e historial por cliente.',
      badge: 'Registro',
      accent: 'violet',
    },
    {
      title: 'Incidentes',
      desc: 'Emergencias, prioridad y estados.',
      badge: 'Core',
      accent: 'red',
    },
    {
      title: 'Atención al Servicio',
      desc: 'Asignación, desplazamiento y cierre.',
      badge: 'Workflow',
      accent: 'emerald',
    },
    {
      title: 'Notificaciones',
      desc: 'Alertas push, email e in-app.',
      badge: 'Realtime',
      accent: 'yellow',
    },
    {
      title: 'Finanzas',
      desc: 'Comisiones, reportes e ingresos.',
      badge: 'Finance',
      accent: 'orange',
    },
    {
      title: 'Historial y Trazabilidad',
      desc: 'Bitácora y auditoría completa.',
      badge: 'Audit',
      accent: 'teal',
    },
  ];

  readonly footerSections: { title: string; links: { label: string; href: string }[] }[] = [
    {
      title: 'Plataforma',
      links: [
        { label: 'Producto', href: '#producto' },
        { label: 'Precios', href: '#precios' },
        { label: 'Cómo funciona', href: '#como-funciona' },
        { label: 'Módulos', href: '#modulos' },
      ],
    },
    {
      title: 'Accesos',
      links: [
        { label: 'Registro taller', href: '/taller/registro' },
        { label: 'Portal taller', href: '/taller' },
        { label: 'Administración', href: '/admin' },
      ],
    },
    {
      title: 'Proyecto',
      links: [
        { label: 'Stack técnico', href: '#stack' },
        { label: 'Contacto', href: '#contacto' },
      ],
    },
  ];

  ngOnInit(): void {
    fromEvent(window, 'scroll', { passive: true })
      .pipe(throttleTime(100), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        const scrolled = window.scrollY > 24;
        if (scrolled === this.navScrolled) return;
        this.navScrolled = scrolled;
        this.cdr.markForCheck();
      });

    this.publicApi
      .getPricingBootstrap()
      .pipe(
        catchError(() =>
          of({ plans: null, stripe: { enabled: false, publishable_key: null } }),
        ),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((bootstrap) => {
        this.stripeEnabled = bootstrap.stripe.enabled;
        this.pricingPlans =
          bootstrap.plans?.map((p) => this.mapApiPlan(p)) ?? this.fallbackPricingPlans;
        this.pricingLoading = false;
        this.cdr.markForCheck();
      });
  }

  scrollTo(selector: string): void {
    const el = document.querySelector(selector);
    el?.scrollIntoView({ behavior: 'smooth' });
    this.menuOpen = false;
    this.cdr.markForCheck();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
    this.cdr.markForCheck();
  }

  closeMenu(): void {
    this.menuOpen = false;
    this.cdr.markForCheck();
  }

  onPlanCta(plan: LandingPricingPlan): void {
    if (plan.stripeCheckout && this.stripeEnabled) {
      this.checkoutPlan = plan;
      this.checkoutEmail = '';
      this.checkoutError = null;
      this.checkoutModalOpen = true;
      this.cdr.markForCheck();
      return;
    }
    if (plan.ctaHref) {
      this.scrollTo(plan.ctaHref);
    }
  }

  closeCheckoutModal(): void {
    if (this.checkoutBusy) return;
    this.checkoutModalOpen = false;
    this.checkoutPlan = null;
    this.checkoutError = null;
    this.cdr.markForCheck();
  }

  submitCheckout(): void {
    if (!this.checkoutPlan || this.checkoutBusy) return;
    const email = this.checkoutEmail.trim();
    if (!email || !email.includes('@')) {
      this.checkoutError = 'Ingresa un correo válido para la facturación.';
      return;
    }

    const origin = window.location.origin;
    this.checkoutBusy = true;
    this.checkoutError = null;
    this.cdr.markForCheck();

    this.publicApi
      .createCheckout({
        plan_slug: this.checkoutPlan.slug,
        email,
        success_url: `${origin}/?checkout=success`,
        cancel_url: `${origin}/#precios`,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          window.location.href = res.checkout_url;
        },
        error: (err: HttpErrorResponse) => {
          this.checkoutBusy = false;
          const detail = err.error?.detail;
          this.checkoutError =
            typeof detail === 'string'
              ? detail
              : 'No se pudo iniciar el pago con Stripe. Revisa la configuración del plan.';
          this.cdr.markForCheck();
        },
      });
  }

  private mapApiPlan(p: {
    slug: string;
    name: string;
    description: string | null;
    price_monthly_bob: number;
    benefits: string[];
    featured: boolean;
    badge: string | null;
    cta_label: string;
    cta_router_link: string | null;
    cta_href: string | null;
    stripe_price_id: string | null;
  }): LandingPricingPlan {
    const paid = Number(p.price_monthly_bob) > 0;
    const hasStripe = Boolean(p.stripe_price_id?.trim());
    const stripeCheckout = paid && hasStripe;

    return {
      id: p.slug,
      slug: p.slug,
      name: p.name,
      priceMonthly: Number(p.price_monthly_bob),
      description: p.description ?? '',
      benefits: p.benefits ?? [],
      ctaLabel: p.cta_label,
      ctaRouterLink: stripeCheckout ? null : p.cta_router_link,
      ctaHref: stripeCheckout ? null : p.cta_href,
      featured: p.featured,
      badge: p.badge,
      stripeCheckout,
    };
  }
}
