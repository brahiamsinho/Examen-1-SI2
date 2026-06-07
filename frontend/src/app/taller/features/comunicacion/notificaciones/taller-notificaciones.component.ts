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
import { Router } from '@angular/router';
import { Subject, catchError, interval, map, of, startWith, switchMap } from 'rxjs';
import { NotificacionesApiService } from '../../../../core/services/notificaciones-api.service';
import { FcmService } from '../../../../core/services/fcm.service';
import { TallerEmergenciasApiService } from '../../../../core/services/taller-emergencias-api.service';
import type { NotificacionDto, TipoNotificacion } from '../../../../core/models/notificacion.models';

@Component({
  selector: 'app-taller-notificaciones',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './taller-notificaciones.component.html',
  styleUrl: './taller-notificaciones.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerNotificacionesComponent implements OnInit {
  private readonly api = inject(NotificacionesApiService);
  private readonly fcm = inject(FcmService);
  private readonly emergenciasApi = inject(TallerEmergenciasApiService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);
  private readonly reloadTrigger = new Subject<{ silent: boolean }>();

  items: NotificacionDto[] = [];
  soloNoLeidas = false;
  readonly loading = signal(true);
  error: string | null = null;

  ngOnInit(): void {
    this.reloadTrigger
      .pipe(
        switchMap(({ silent }) => {
          if (!silent) {
            this.loading.set(true);
            this.error = null;
            this.cdr.markForCheck();
          }
          return this.api.listar('taller', this.soloNoLeidas, 100).pipe(
            catchError((err) => {
              this.error = err?.error?.detail ?? 'No se pudieron cargar las notificaciones.';
              return of([] as NotificacionDto[]);
            }),
            map((list) => ({ list, silent })),
          );
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe(({ list }) => {
        this.items = list;
        this.loading.set(false);
        this.cdr.markForCheck();
      });

    interval(60_000)
      .pipe(startWith(0), takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.reloadTrigger.next({ silent: true }));

    this.fcm.foregroundMessage$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.reloadTrigger.next({ silent: true }));

    this.reloadTrigger.next({ silent: false });
  }

  toggleFiltro(soloNoLeidas: boolean): void {
    this.soloNoLeidas = soloNoLeidas;
    this.reloadTrigger.next({ silent: false });
  }

  reload(): void {
    this.reloadTrigger.next({ silent: false });
  }

  abrir(notif: NotificacionDto): void {
    if (!notif.leida) {
      this.api.marcarLeida('taller', notif.id).subscribe({
        next: (updated) => {
          this.items = this.items.map((n) => (n.id === updated.id ? updated : n));
          this.cdr.markForCheck();
        },
      });
    }
    this.navigate(notif);
  }

  private navigate(notif: NotificacionDto): void {
    if (notif.solicitud_id == null) {
      void this.router.navigate(['/taller/panel/emergencias/solicitudes']);
      return;
    }
    this.emergenciasApi.resolveBandejaId(notif.solicitud_id).subscribe({
      next: ({ bandeja_id: bandejaId }) => {
        if (bandejaId != null) {
          void this.router.navigate(['/taller/panel/emergencias/solicitudes', bandejaId]);
          return;
        }
        void this.router.navigate(['/taller/panel/emergencias/solicitudes'], {
          queryParams: { q: String(notif.solicitud_id) },
        });
      },
      error: () => {
        void this.router.navigate(['/taller/panel/emergencias/solicitudes'], {
          queryParams: { q: String(notif.solicitud_id) },
        });
      },
    });
  }

  tipoLabel(tipo: TipoNotificacion): string {
    const labels: Record<TipoNotificacion, string> = {
      SOLICITUD_CREADA: 'Emergencia registrada',
      ESTADO_ACTUALIZADO: 'Estado / pago',
      TALLER_ASIGNADO: 'Taller asignado',
      TECNICO_ASIGNADO: 'Técnico asignado',
      MENSAJE_NUEVO: 'Mensaje del cliente',
      SOLICITUD_PENDIENTE_TALLER: 'Nueva solicitud',
    };
    return labels[tipo] ?? tipo;
  }

  trackById(_index: number, item: NotificacionDto): number {
    return item.id;
  }
}
