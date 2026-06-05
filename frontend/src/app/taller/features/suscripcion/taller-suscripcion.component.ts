import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { finalize } from 'rxjs/operators';
import { TallerApiService } from '../../../core/services/taller-api.service';
import type { TallerPlanOptionDto, TallerSuscripcionDto } from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-suscripcion',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './taller-suscripcion.component.html',
  styleUrl: './taller-suscripcion.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerSuscripcionComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  data: TallerSuscripcionDto | null = null;
  readonly loading = signal(true);
  error: string | null = null;
  success: string | null = null;
  upgradingSlug: string | null = null;

  ngOnInit(): void {
    this.route.queryParamMap.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((q) => {
      const checkout = q.get('checkout');
      const sessionId = q.get('session_id');
      if (checkout === 'ok') {
        void this.router.navigate([], { relativeTo: this.route, queryParams: {}, replaceUrl: true });
        if (sessionId) {
          this.confirmCheckout(sessionId);
        } else {
          this.success = 'Pago recibido. Si el plan no cambia, recargá en unos segundos.';
          this.reload();
        }
      } else if (checkout === 'cancel') {
        this.error = 'Checkout cancelado. No se realizó ningún cargo.';
        void this.router.navigate([], { relativeTo: this.route, queryParams: {}, replaceUrl: true });
        this.cdr.markForCheck();
      } else {
        this.reload();
      }
    });
  }

  private confirmCheckout(sessionId: string): void {
    this.loading.set(true);
    this.error = null;
    this.api
      .confirmSuscripcionCheckout({ session_id: sessionId })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (d) => {
          this.data = d;
          this.success = `Plan actualizado a ${d.current_plan_name}.`;
          this.cdr.markForCheck();
        },
        error: (err) => {
          const d = err?.error?.detail;
          this.error =
            typeof d === 'string'
              ? d
              : 'No se pudo confirmar el pago. Recargá la página en unos segundos.';
          this.reload();
        },
      });
  }

  reload(): void {
    this.loading.set(true);
    this.error = null;
    this.api
      .getSuscripcion()
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.loading.set(false);
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (d) => {
          this.data = d;
          const upgrade = this.route.snapshot.queryParamMap.get('upgrade');
          if (upgrade) {
            const plan = d.plans.find((p) => p.slug === upgrade && p.can_upgrade);
            if (plan) this.startUpgrade(plan);
          }
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudo cargar la información de suscripción.';
          this.cdr.markForCheck();
        },
      });
  }

  statusLabel(status: string): string {
    const m: Record<string, string> = {
      TRIAL: 'Prueba',
      ACTIVA: 'Activa',
      PAST_DUE: 'Pago pendiente',
      CANCELADA: 'Cancelada',
      SUSPENDIDA: 'Suspendida',
    };
    return m[status] ?? status;
  }

  priceLabel(plan: TallerPlanOptionDto): string {
    if (!plan.price_monthly_bob) return 'Gratis';
    return `${plan.currency} ${plan.price_monthly_bob.toLocaleString('es-BO')} / mes`;
  }

  startUpgrade(plan: TallerPlanOptionDto): void {
    if (!plan.can_upgrade || this.upgradingSlug) return;
    if (!this.data?.stripe_enabled) {
      this.error = 'Stripe no está configurado en el servidor (STRIPE_SECRET_KEY).';
      this.cdr.markForCheck();
      return;
    }

    this.upgradingSlug = plan.slug;
    this.error = null;
    const origin = window.location.origin;
    this.api
      .createSuscripcionCheckout({
        plan_slug: plan.slug,
        success_url: `${origin}/taller/panel/suscripcion?checkout=ok&session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origin}/taller/panel/suscripcion?checkout=cancel`,
      })
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => {
          this.upgradingSlug = null;
          this.cdr.markForCheck();
        }),
      )
      .subscribe({
        next: (res) => {
          window.location.href = res.checkout_url;
        },
        error: (err) => {
          const d = err?.error?.detail;
          this.error = typeof d === 'string' ? d : 'No se pudo iniciar el checkout con Stripe.';
          this.cdr.markForCheck();
        },
      });
  }
}
