import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  DestroyRef,
  HostListener,
  Input,
  inject,
  OnInit,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { interval, switchMap, catchError, of, startWith } from 'rxjs';
import { NotificacionesApiService } from '../../core/services/notificaciones-api.service';
import { FcmService } from '../../core/services/fcm.service';
import { TallerEmergenciasApiService } from '../../core/services/taller-emergencias-api.service';
import type { NotificacionDto, NotificacionPortal } from '../../core/models/notificacion.models';

@Component({
  selector: 'app-notification-bell',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './notification-bell.component.html',
  styleUrl: './notification-bell.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class NotificationBellComponent implements OnInit {
  @Input({ required: true }) portal!: NotificacionPortal;

  private readonly api = inject(NotificacionesApiService);
  private readonly fcm = inject(FcmService);
  private readonly emergenciasApi = inject(TallerEmergenciasApiService);
  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly destroyRef = inject(DestroyRef);

  open = false;
  loading = false;
  error: string | null = null;
  items: NotificacionDto[] = [];

  get unreadCount(): number {
    return this.items.filter((n) => !n.leida).length;
  }

  ngOnInit(): void {
    interval(60_000)
      .pipe(
        startWith(0),
        switchMap(() =>
          this.api.listar(this.portal, false, 30).pipe(catchError(() => of([] as NotificacionDto[]))),
        ),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe((rows) => {
        this.items = rows;
        this.cdr.markForCheck();
      });

    this.fcm.foregroundMessage$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => this.load());
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.open = false;
    this.cdr.markForCheck();
  }

  togglePanel(event: Event): void {
    event.stopPropagation();
    this.open = !this.open;
    if (this.open) {
      this.load();
    }
    this.cdr.markForCheck();
  }

  @HostListener('document:click')
  closePanel(): void {
    if (!this.open) return;
    this.open = false;
    this.cdr.markForCheck();
  }

  load(): void {
    this.loading = true;
    this.error = null;
    this.api.listar(this.portal, false, 30).subscribe({
      next: (rows) => {
        this.items = rows;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudieron cargar las notificaciones.';
        this.cdr.markForCheck();
      },
    });
  }

  markRead(item: NotificacionDto, event: Event): void {
    event.stopPropagation();
    if (item.leida) {
      this.navigate(item);
      return;
    }
    this.api.marcarLeida(this.portal, item.id).subscribe({
      next: (updated) => {
        this.items = this.items.map((n) => (n.id === updated.id ? updated : n));
        this.cdr.markForCheck();
        this.navigate(updated);
      },
      error: () => {
        this.navigate(item);
      },
    });
  }

  private navigate(item: NotificacionDto): void {
    this.open = false;
    if (this.portal === 'taller') {
      if (item.solicitud_id != null) {
        this.emergenciasApi.resolveBandejaId(item.solicitud_id).subscribe({
          next: ({ bandeja_id: bandejaId }) => {
            if (bandejaId != null) {
              void this.router.navigate(['/taller/panel/emergencias/solicitudes', bandejaId]);
              return;
            }
            void this.router.navigate(['/taller/panel/emergencias/solicitudes']);
          },
          error: () => {
            void this.router.navigate(['/taller/panel/emergencias/solicitudes']);
          },
        });
        return;
      }
      void this.router.navigate(['/taller/panel/emergencias/solicitudes']);
      return;
    }
    void this.router.navigate(['/admin/panel']);
  }

  trackById(_index: number, item: NotificacionDto): number {
    return item.id;
  }

  formatWhen(iso: string): string {
    try {
      return new Intl.DateTimeFormat('es-BO', {
        dateStyle: 'short',
        timeStyle: 'short',
      }).format(new Date(iso));
    } catch {
      return iso;
    }
  }
}
