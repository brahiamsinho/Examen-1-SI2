import { Component, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

/** Datos de ejemplo alineados al mockData del prototipo Figma Make */
const MOCK_USERS = [
  { estado: 'Activo' },
  { estado: 'Activo' },
  { estado: 'Activo' },
  { estado: 'Inactivo' },
  { estado: 'Activo' },
  { estado: 'Activo' },
];
const MOCK_ROLES = [{}, {}, {}];
const MOCK_WORKSHOPS = [{ estado: 'Activo' }, { estado: 'Activo' }, { estado: 'Inactivo' }];
const MOCK_AUDIT = [
  { id: '1', usuario: 'admin@sistema.com', accion: 'Crear', modulo: 'Usuarios', descripcion: 'Creó usuario ana@example.com', fecha: '2026-04-08 09:15:23' },
  { id: '2', usuario: 'admin@sistema.com', accion: 'Editar', modulo: 'Talleres', descripcion: 'Editó taller AutoTec San José', fecha: '2026-04-08 08:42:10' },
  { id: '3', usuario: 'taller@autotec.com', accion: 'Crear', modulo: 'Técnicos', descripcion: 'Registró técnico Diego Campos', fecha: '2026-04-07 17:30:00' },
  { id: '4', usuario: 'admin@sistema.com', accion: 'Eliminar', modulo: 'Roles', descripcion: 'Eliminó rol "Supervisor"', fecha: '2026-04-07 14:22:15' },
  { id: '5', usuario: 'cliente@gmail.com', accion: 'Crear', modulo: 'Vehículos', descripcion: 'Registró vehículo placa ABC-123', fecha: '2026-04-07 11:05:44' },
  { id: '6', usuario: 'admin@sistema.com', accion: 'Editar', modulo: 'Permisos', descripcion: 'Asignó permiso ver_bitacora al rol Taller', fecha: '2026-04-06 16:00:00' },
  { id: '7', usuario: 'taller@autotec.com', accion: 'Editar', modulo: 'Técnicos', descripcion: 'Desactivó técnico Marco Herrera', fecha: '2026-04-06 10:30:22' },
  { id: '8', usuario: 'admin@sistema.com', accion: 'Crear', modulo: 'Talleres', descripcion: 'Registró taller TechCar CR', fecha: '2026-04-05 09:00:00' },
];

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  private readonly auth = inject(AuthService);

  readonly firstName = computed(() => {
    const u = this.auth.currentUser();
    const n = u?.nombres?.trim();
    return n || 'colega';
  });

  readonly statCards = [
    { label: 'Usuarios', value: MOCK_USERS.length, tone: 'blue', path: '/usuarios', icon: 'users' as const },
    { label: 'Roles', value: MOCK_ROLES.length, tone: 'purple', path: '/acceso/roles', icon: 'shield' as const },
    { label: 'Talleres', value: MOCK_WORKSHOPS.length, tone: 'teal', path: '/talleres', icon: 'wrench' as const },
    { label: 'Registros bitácora', value: MOCK_AUDIT.length, tone: 'orange', path: '/bitacora', icon: 'clipboard' as const },
  ];

  readonly totalUsers = MOCK_USERS.length;
  readonly activeUsers = MOCK_USERS.filter((u) => u.estado === 'Activo').length;
  readonly totalWorkshops = MOCK_WORKSHOPS.length;
  readonly activeWorkshops = MOCK_WORKSHOPS.filter((w) => w.estado === 'Activo').length;
  readonly totalPermissions = 12;
  readonly recentLogs = MOCK_AUDIT.slice(0, 5);

  get pctActiveUsers(): number {
    return this.totalUsers ? Math.round((this.activeUsers / this.totalUsers) * 100) : 0;
  }

  get pctActiveWorkshops(): number {
    return this.totalWorkshops ? Math.round((this.activeWorkshops / this.totalWorkshops) * 100) : 0;
  }

  badgeClass(status: string): Record<string, boolean> {
    const map: Record<string, string> = {
      Activo: 'b-emerald',
      Inactivo: 'b-red',
      Crear: 'b-emerald',
      Editar: 'b-blue',
      Eliminar: 'b-red',
      Usuarios: 'b-purple',
      Talleres: 'b-teal',
      Técnicos: 'b-amber',
      Roles: 'b-indigo',
      Permisos: 'b-pink',
      Bitácora: 'b-slate',
      Vehículos: 'b-cyan',
    };
    const key = map[status] || 'b-gray';
    return { [key]: true };
  }

  timeOnly(fecha: string): string {
    const parts = fecha.split(' ');
    return parts[1] ?? fecha;
  }
}
