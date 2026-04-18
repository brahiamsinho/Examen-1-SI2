import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TallerApiService } from '../../../core/services/taller-api.service';
import type { TallerDashboardDto } from '../../../core/models/taller-api.models';

@Component({
  selector: 'app-taller-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './taller-dashboard.component.html',
  styleUrl: './taller-dashboard.component.scss',
})
export class TallerDashboardComponent implements OnInit {
  private readonly api = inject(TallerApiService);

  data: TallerDashboardDto | null = null;
  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.api.getDashboard().subscribe({
      next: (d) => {
        this.data = d;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudo cargar el resumen del taller.';
      },
    });
  }
}
