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
import type {
  QbePayload,
  ReportExecuteResultDto,
  ReportExportFormat,
  ReportTemplateDto,
} from '../../../core/models/taller-api.models';

type SpeechRecognitionLike = {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((ev: { results: { 0: { 0: { transcript: string } } } }) => void) | null;
  onerror: ((ev: { error: string }) => void) | null;
  onend: (() => void) | null;
};

@Component({
  selector: 'app-taller-reportes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-reportes.component.html',
  styleUrl: './taller-reportes.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TallerReportesComponent implements OnInit {
  private readonly api = inject(TallerApiService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly cdr = inject(ChangeDetectorRef);

  templates: ReportTemplateDto[] = [];
  loadingTemplates = true;
  loadingReport = false;
  exporting: ReportExportFormat | null = null;
  error: string | null = null;
  success: string | null = null;

  nlQuery = '';
  interpretation = '';
  currentQbe: QbePayload | null = null;
  report: ReportExecuteResultDto | null = null;
  pendingExportFormats: ReportExportFormat[] = [];

  listening = false;
  speechSupported = false;
  private recognition: SpeechRecognitionLike | null = null;

  saveName = '';

  ngOnInit(): void {
    this.initSpeech();
    this.loadTemplates();
  }

  private initSpeech(): void {
    const w = window as unknown as {
      SpeechRecognition?: new () => SpeechRecognitionLike;
      webkitSpeechRecognition?: new () => SpeechRecognitionLike;
    };
    const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!Ctor) return;
    this.speechSupported = true;
    this.recognition = new Ctor();
    this.recognition.lang = 'es-BO';
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.onresult = (ev) => {
      const text = ev.results[0][0].transcript?.trim();
      if (text) {
        this.nlQuery = text;
        this.cdr.markForCheck();
        this.interpretAndRun(true);
      }
    };
    this.recognition.onerror = () => {
      this.listening = false;
      this.error = 'No se pudo capturar voz. Escribe la consulta o revisa permisos del micrófono.';
      this.cdr.markForCheck();
    };
    this.recognition.onend = () => {
      this.listening = false;
      this.cdr.markForCheck();
    };
  }

  loadTemplates(): void {
    this.loadingTemplates = true;
    this.api
      .listReportTemplates()
      .pipe(
        finalize(() => {
          this.loadingTemplates = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (rows) => {
          this.templates = rows;
        },
        error: () => {
          this.error = 'No se pudieron cargar las plantillas de reporte.';
        },
      });
  }

  toggleVoice(): void {
    if (!this.recognition) {
      this.error = 'Tu navegador no soporta reconocimiento de voz. Escribe la consulta manualmente.';
      this.cdr.markForCheck();
      return;
    }
    if (this.listening) {
      this.recognition.stop();
      return;
    }
    this.error = null;
    this.listening = true;
    this.recognition.start();
    this.cdr.markForCheck();
  }

  interpretAndRun(autoExport = false): void {
    const q = this.nlQuery.trim();
    if (!q) {
      this.error = 'Escribe o dicta qué reporte necesitas.';
      this.cdr.markForCheck();
      return;
    }
    this.loadingReport = true;
    this.error = null;
    this.success = null;
    this.api
      .nlReportQuery(q)
      .pipe(
        finalize(() => {
          this.loadingReport = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (nl) => {
          this.interpretation = nl.interpretation;
          this.currentQbe = nl.qbe;
          this.pendingExportFormats = nl.export_formats ?? [];
          this.runQbe(nl.qbe, autoExport || this.pendingExportFormats.length > 0);
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.error = typeof detail === 'string' ? detail : 'No se pudo interpretar la consulta.';
        },
      });
  }

  runTemplate(t: ReportTemplateDto): void {
    this.loadingReport = true;
    this.error = null;
    this.success = null;
    this.api
      .runReportTemplate(t.id)
      .pipe(
        finalize(() => {
          this.loadingReport = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (res) => {
          this.currentQbe = res.qbe;
          this.report = res.report;
          this.interpretation = `Plantilla: ${t.nombre}`;
          this.success = `Reporte ejecutado (${res.report.meta.total_records} registros).`;
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.error = typeof detail === 'string' ? detail : 'No se pudo ejecutar la plantilla.';
        },
      });
  }

  private runQbe(qbe: QbePayload, autoExport: boolean): void {
    this.api
      .executeReport(qbe)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (res) => {
          this.report = res;
          this.success = `Vista previa lista (${res.meta.total_records} registros${
            res.meta.truncated ? ', mostrando máximo 500' : ''
          }).`;
          if (autoExport && this.pendingExportFormats.length) {
            for (const fmt of this.pendingExportFormats) {
              this.export(fmt, qbe);
            }
          }
          this.cdr.markForCheck();
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.error = typeof detail === 'string' ? detail : 'No se pudo ejecutar el reporte.';
          this.cdr.markForCheck();
        },
      });
  }

  export(fmt: ReportExportFormat, qbe: QbePayload | null = this.currentQbe): void {
    if (!qbe) {
      this.error = 'Primero ejecuta un reporte.';
      this.cdr.markForCheck();
      return;
    }
    this.exporting = fmt;
    this.api
      .exportReport(fmt, qbe)
      .pipe(
        finalize(() => {
          this.exporting = null;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (blob) => {
          const model = (qbe.model || 'reporte').toLowerCase().replace(/[^a-z0-9_-]+/g, '-');
          const ext = fmt === 'excel' ? 'xlsx' : fmt;
          this.downloadBlob(blob, `reporte-${model}.${ext}`);
          this.success = `Descarga ${fmt.toUpperCase()} iniciada.`;
        },
        error: () => {
          this.error = `No se pudo exportar a ${fmt.toUpperCase()}.`;
        },
      });
  }

  saveTemplate(): void {
    if (!this.currentQbe) {
      this.error = 'Ejecuta un reporte antes de guardarlo.';
      this.cdr.markForCheck();
      return;
    }
    const nombre = this.saveName.trim() || `Reporte ${this.currentQbe.model}`;
    this.api
      .createReportTemplate({
        nombre,
        descripcion: this.interpretation || this.nlQuery.trim(),
        qbe_payload: this.currentQbe,
      })
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.success = 'Plantilla guardada.';
          this.saveName = '';
          this.loadTemplates();
        },
        error: (err) => {
          const detail = err?.error?.detail;
          this.error = typeof detail === 'string' ? detail : 'No se pudo guardar la plantilla.';
          this.cdr.markForCheck();
        },
      });
  }

  deleteTemplate(t: ReportTemplateDto): void {
    if (t.is_system_report) return;
    if (!confirm(`¿Eliminar plantilla "${t.nombre}"?`)) return;
    this.api
      .deleteReportTemplate(t.id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.success = 'Plantilla eliminada.';
          this.loadTemplates();
        },
        error: () => {
          this.error = 'No se pudo eliminar la plantilla.';
          this.cdr.markForCheck();
        },
      });
  }

  private downloadBlob(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
}
