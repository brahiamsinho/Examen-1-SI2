import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminApiService } from '../../../../core/services/admin-api.service';
import type { ClienteListDto, EstadoUsuario } from '../../../../core/models/admin-api.models';

@Component({
  selector: 'app-taller-clientes',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './taller-clientes.component.html',
  styleUrl: './taller-clientes.component.scss',
})
export class TallerClientesComponent implements OnInit {
  private readonly api = inject(AdminApiService);

  clientes: ClienteListDto[] = [];
  search = '';
  estado: EstadoUsuario | '' = '';
  loading = true;
  error: string | null = null;

  readonly estados: EstadoUsuario[] = ['ACTIVO', 'INACTIVO', 'BLOQUEADO', 'PENDIENTE'];

  ngOnInit(): void {
    this.reload();
  }

  reload(): void {
    this.loading = true;
    this.api.listClientes().subscribe({
      next: (rows) => {
        this.clientes = rows;
        this.loading = false;
        this.error = null;
      },
      error: () => {
        this.loading = false;
        this.error = 'No se pudieron cargar las cuentas de clientes.';
      },
    });
  }

  get filtered(): ClienteListDto[] {
    let rows = this.clientes;
    if (this.estado) rows = rows.filter((c) => c.estado === this.estado);
    const q = this.search.trim().toLowerCase();
    if (q) {
      rows = rows.filter(
        (c) =>
          c.email.toLowerCase().includes(q) ||
          c.nombres.toLowerCase().includes(q) ||
          c.apellidos.toLowerCase().includes(q) ||
          (c.telefono && c.telefono.includes(q)),
      );
    }
    return rows;
  }
}
