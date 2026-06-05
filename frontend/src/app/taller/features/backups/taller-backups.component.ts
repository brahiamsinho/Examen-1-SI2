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
import { TallerApiService } from '../../../core/services/taller-api.service';
import type { TallerBackupConfigDto, TallerBackupDto } from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-backups',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-backups.component.html',
  styleUrl: './taller-backups.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerBackupsComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  rows: TallerBackupDto[] = [];
  config: TallerBackupConfigDto | null = null;
  loading = true;
  savingConfig = false;
  creating = false;
  error: string | null = null;
  success: string | null = null;

  restoreTarget: TallerBackupDto | null = null;
  restoreConfirm = false;
  restoreMotivo = '';
  restoring = false;

  ngOnInit(): void {
    this.loadConfig();
    this.fetch();
  }

  loadConfig(): void {
    this.api
      .getBackupConfig()
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (c) => {
          this.config = c;
          this.cdr.markForCheck();
        },
        error: () => {
          this.error = 'No se pudo cargar la configuración de backup.';
          this.cdr.markForCheck();
        },
      });
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
          this.rows = r;
        },
        error: (err) => {
          this.error = err?.error?.detail ?? 'No se pudo cargar los backups de tu taller.';
        },
      });
  }

  saveConfig(): void {
    if (!this.config) return;
    this.savingConfig = true;
    this.error = null;
    this.success = null;
    this.api
      .updateBackupConfig({
        backup_automatico: this.config.backup_automatico,
        hora_backup: this.configHoraValue(),
        frecuencia: this.config.frecuencia,
        retencion_dias: this.config.retencion_dias,
      })
      .pipe(
        finalize(() => {
          this.savingConfig = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (c) => {
          this.config = c;
          this.success = 'Configuración guardada. El backup automático usa la hora local del servidor (TZ).';
        },
        error: (err) => {
          this.error = err?.error?.detail ?? 'No se pudo guardar la configuración.';
        },
      });
  }

  configHoraValue(): string {
    const h = this.config?.hora_backup ?? '03:00:00';
    return h.length >= 5 ? h.slice(0, 5) : '03:00';
  }

  onHoraChange(value: string): void {
    if (!this.config) return;
    this.config = { ...this.config, hora_backup: value.length === 5 ? `${value}:00` : value };
  }

  crear(): void {
    this.creating = true;
    this.error = null;
    this.success = null;
    this.api
      .createBackup()
      .pipe(
        finalize(() => {
          this.creating = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: () => {
          this.success = 'Backup creado correctamente.';
          this.fetch();
        },
        error: (err) => {
          this.error = err?.error?.detail ?? 'Error al crear backup.';
        },
      });
  }

  descargar(row: TallerBackupDto): void {
    this.api.downloadBackup(row.id).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = row.archivo.split('/').pop() ?? `backup-taller-${row.id}.tar.gz`;
        a.click();
        URL.revokeObjectURL(url);
      },
      error: () => {
        this.error = 'No se pudo descargar el archivo.';
        this.cdr.markForCheck();
      },
    });
  }

  openRestore(row: TallerBackupDto): void {
    this.restoreTarget = row;
    this.restoreConfirm = false;
    this.restoreMotivo = '';
    this.cdr.markForCheck();
  }

  closeRestore(): void {
    this.restoreTarget = null;
    this.cdr.markForCheck();
  }

  confirmRestore(): void {
    if (!this.restoreTarget || !this.restoreConfirm || this.restoreMotivo.trim().length < 3) {
      this.error = 'Confirmá la restauración e indicá un motivo (mín. 3 caracteres).';
      this.cdr.markForCheck();
      return;
    }
    this.restoring = true;
    this.error = null;
    this.api
      .restoreBackup(this.restoreTarget.id, {
        confirmar: true,
        motivo: this.restoreMotivo.trim(),
      })
      .pipe(
        finalize(() => {
          this.restoring = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: () => {
          this.success = 'Backup restaurado. Revisá tus datos operativos.';
          this.closeRestore();
          this.fetch();
        },
        error: (err) => {
          this.error = err?.error?.detail ?? 'Error al restaurar backup.';
        },
      });
  }

  eliminar(row: TallerBackupDto): void {
    if (!confirm(`¿Eliminar backup #${row.id}?`)) return;
    this.api.deleteBackup(row.id).subscribe({
      next: () => this.fetch(),
      error: () => {
        this.error = 'No se pudo eliminar el backup.';
        this.cdr.markForCheck();
      },
    });
  }
}
