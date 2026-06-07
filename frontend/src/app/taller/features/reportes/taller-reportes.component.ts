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
  ReportVoiceTranscribeResultDto,
} from '../../../core/models/taller-api.models';

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
  voiceSupported = false;
  private mediaRecorder: MediaRecorder | null = null;
  private mediaStream: MediaStream | null = null;
  private audioChunks: Blob[] = [];
  private listenWatchdogId: ReturnType<typeof setTimeout> | null = null;
  private readonly maxRecordMs = 15000;

  saveName = '';

  ngOnInit(): void {
    this.voiceSupported = !!(
      typeof navigator !== 'undefined' &&
      typeof navigator.mediaDevices?.getUserMedia === 'function' &&
      typeof MediaRecorder !== 'undefined'
    );
    this.destroyRef.onDestroy(() => this.cleanupVoice());
    this.loadTemplates();
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
    if (!this.voiceSupported) {
      this.error =
        'Tu navegador no permite grabar audio. Escribe la consulta manualmente o usa Chrome/Edge actualizado.';
      this.cdr.markForCheck();
      return;
    }
    if (this.listening) {
      this.stopRecording(false);
      return;
    }
    void this.startRecording();
  }

  private async startRecording(): Promise<void> {
    this.error = null;
    this.success = null;
    this.audioChunks = [];
    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      this.error = 'Permiso de micrófono denegado. Actívalo en el navegador e inténtalo de nuevo.';
      this.cdr.markForCheck();
      return;
    }

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : '';

    try {
      this.mediaRecorder = mimeType
        ? new MediaRecorder(this.mediaStream, { mimeType })
        : new MediaRecorder(this.mediaStream);
    } catch {
      this.cleanupVoice();
      this.error = 'No se pudo iniciar la grabación de voz en este navegador.';
      this.cdr.markForCheck();
      return;
    }

    this.mediaRecorder.ondataavailable = (ev) => {
      if (ev.data.size > 0) this.audioChunks.push(ev.data);
    };
    this.mediaRecorder.onerror = () => {
      this.error = 'Error al grabar audio. Intenta de nuevo o escribe la consulta.';
      this.cleanupVoice();
      this.cdr.markForCheck();
    };
    this.mediaRecorder.onstop = () => {
      const chunks = [...this.audioChunks];
      const type = this.mediaRecorder?.mimeType || chunks[0]?.type || 'audio/webm';
      this.cleanupVoice();
      if (!chunks.length) {
        this.error = 'No se captó audio. Habla cerca del micrófono e inténtalo otra vez.';
        this.cdr.markForCheck();
        return;
      }
      this.sendVoiceRecording(new Blob(chunks, { type }));
    };

    this.listening = true;
    this.armListenWatchdog();
    this.mediaRecorder.start();
    this.cdr.markForCheck();

    setTimeout(() => {
      if (this.listening) this.stopRecording(false);
    }, this.maxRecordMs);
  }

  private stopRecording(fromWatchdog: boolean): void {
    if (this.mediaRecorder?.state === 'recording') {
      this.mediaRecorder.stop();
    } else if (fromWatchdog) {
      this.cleanupVoice();
      this.error = 'Tiempo de escucha agotado. Intenta una frase más corta.';
      this.cdr.markForCheck();
    }
  }

  private armListenWatchdog(): void {
    this.clearListenWatchdog();
    this.listenWatchdogId = setTimeout(() => {
      if (this.listening) this.stopRecording(true);
    }, this.maxRecordMs + 5000);
  }

  private clearListenWatchdog(): void {
    if (this.listenWatchdogId != null) {
      clearTimeout(this.listenWatchdogId);
      this.listenWatchdogId = null;
    }
  }

  private cleanupVoice(resetListening = true): void {
    this.clearListenWatchdog();
    if (this.mediaRecorder) {
      this.mediaRecorder.ondataavailable = null;
      this.mediaRecorder.onerror = null;
      this.mediaRecorder.onstop = null;
      this.mediaRecorder = null;
    }
    if (this.mediaStream) {
      for (const track of this.mediaStream.getTracks()) track.stop();
      this.mediaStream = null;
    }
    if (resetListening) {
      this.listening = false;
    }
  }

  private sendVoiceRecording(blob: Blob): void {
    this.loadingReport = true;
    this.error = null;
    this.success = null;
    const ext = blob.type.includes('webm') ? 'webm' : 'bin';
    this.api
      .voiceReportQuery(blob, `consulta-reporte.${ext}`)
      .pipe(
        finalize(() => {
          this.loadingReport = false;
          this.cdr.markForCheck();
        }),
        takeUntilDestroyed(this.destroyRef),
      )
      .subscribe({
        next: (voice) => this.applyVoiceTranscription(voice),
        error: (err) => {
          const detail = err?.error?.detail;
          this.error =
            typeof detail === 'string'
              ? detail
              : 'No se pudo transcribir el audio. Escribe la consulta o revisa que IA esté habilitada.';
        },
      });
  }

  private applyVoiceTranscription(voice: ReportVoiceTranscribeResultDto): void {
    this.nlQuery = voice.transcripcion;
    this.interpretation = '';
    this.report = null;
    this.currentQbe = null;
    const via = voice.provider === 'gemini' ? 'Gemini' : 'Whisper';
    this.success = `Transcripción (${via}): revisa el texto y pulsa «Interpretar y ejecutar».`;
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
