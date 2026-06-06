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
import { finalize } from 'rxjs/operators';
import { AdminApiService } from '../../../core/services/admin-api.service';
import type { BackupDto, BackupTipo, TenantDto } from '../../../core/models/admin-api.models';

@Component({
  selector: 'app-admin-backups',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-backups.component.html',
  styleUrl: './admin-backups.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminBackupsComponent implements OnInit {
  private readonly api = inject(AdminApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  rows: BackupDto[] = [];
  tenants: TenantDto[] = [];
  loading = true;
  error: string | null = null;
  success: string | null = null;

  createTipo: BackupTipo = 'PLATAFORMA';
  createTenantId = '';
  incluirEvidencias = true;

  ngOnInit(): void {
    this.api
      .listTenants()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (t) => {
          this.tenants = Array.isArray(t) ? t : [];
          this.cdr.markForCheck();
        },
      });
    this.fetch();
  }

  fetch(): void {
    this.loading = true;
    this.error = null;
    this.api
      .listBackups()
      .pipe(
        finalize(() => {
          this.loading = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (r) => {
          this.rows = Array.isArray(r) ? r : [];
        },
        error: () => {
          this.error = 'No se pudo cargar los backups (requiere superadmin plataforma).';
        },
      });
  }

  crear(): void {
    this.error = null;
    this.success = null;
    const tenantId = this.createTenantId.trim() ? Number(this.createTenantId) : undefined;
    if (this.createTipo === 'TENANT' && (!tenantId || Number.isNaN(tenantId))) {
      this.error = 'Selecciona una organización para backup TENANT.';
      this.cdr.markForCheck();
      return;
    }
    this.api
      .createBackup({
        tipo: this.createTipo,
        tenant_id: tenantId,
        incluir_evidencias: this.incluirEvidencias,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.success = 'Backup creado correctamente.';
          this.fetch();
        },
        error: (err) => {
          this.error = err?.error?.detail ?? 'Error al crear backup.';
          this.cdr.markForCheck();
        },
      });
  }

  descargar(row: BackupDto): void {
    this.api
      .downloadBackup(row.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = row.archivo.split('/').pop() ?? `backup-${row.id}`;
          a.click();
          URL.revokeObjectURL(url);
        },
        error: () => {
          this.error = 'No se pudo descargar el archivo.';
          this.cdr.markForCheck();
        },
      });
  }

  eliminar(row: BackupDto): void {
    if (!confirm(`¿Eliminar backup #${row.id}?`)) return;
    this.api
      .deleteBackup(row.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => this.fetch(),
        error: () => {
          this.error = 'No se pudo eliminar el backup.';
          this.cdr.markForCheck();
        },
      });
  }
}
