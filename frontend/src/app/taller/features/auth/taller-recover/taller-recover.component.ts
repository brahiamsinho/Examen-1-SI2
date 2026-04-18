import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-taller-recover',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink],
  templateUrl: './taller-recover.component.html',
  styleUrl: './taller-recover.component.scss',
})
export class TallerRecoverComponent {
  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  submitting = false;
  success = false;
  errorMsg: string | null = null;

  submit(): void {
    this.errorMsg = null;
    this.success = false;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.submitting = true;
    // Ciclo 1: backend sin flujo de correo; UX de prototipo (confirmación simulada).
    setTimeout(() => {
      this.submitting = false;
      this.success = true;
    }, 600);
  }
}
