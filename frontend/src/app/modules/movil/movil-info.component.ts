import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Alcance Ciclo 1: el cliente móvil es un módulo aparte (Figma Make /client/*).
 * Esta pantalla sustituye la navegación a /client/splash en la app web Angular.
 */
@Component({
  selector: 'app-movil-info',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="wrap">
      <a routerLink="/" class="back">← Volver al inicio</a>
      <h1>App móvil — Cliente</h1>
      <p class="lead">
        En el prototipo Figma Make, este flujo vive en rutas tipo <code>/client/splash</code>,
        <code>/client/login</code> y vehículos. En este proyecto Angular (Ciclo 1) el alcance web
        es el panel administrativo; la app móvil se documenta aquí como referencia de casos de uso.
      </p>
      <ul>
        <li>CU1 Registrarse</li>
        <li>CU2 / CU3 / CU4 Sesión</li>
        <li>CU10 Gestionar vehículo</li>
      </ul>
      <p>
        <a routerLink="/auth/login" class="link">Ir al login web</a>
        (misma API backend cuando integres el cliente móvil).
      </p>
    </div>
  `,
  styles: [
    `
      .wrap {
        min-height: 100vh;
        background: linear-gradient(135deg, #0f172a 0%, #172554 50%, #0f172a 100%);
        color: #e2e8f0;
        padding: 2rem;
        max-width: 40rem;
        margin: 0 auto;
        box-sizing: border-box;
      }
      .back {
        color: #93c5fd;
        text-decoration: none;
        font-size: 0.875rem;
      }
      .back:hover {
        text-decoration: underline;
      }
      h1 {
        margin-top: 1.5rem;
        font-size: 1.5rem;
      }
      .lead {
        color: #94a3b8;
        line-height: 1.6;
        font-size: 0.9375rem;
      }
      code {
        background: rgba(255, 255, 255, 0.08);
        padding: 0.125rem 0.375rem;
        border-radius: 4px;
        font-size: 0.8125rem;
      }
      ul {
        color: #cbd5e1;
        line-height: 1.8;
      }
      .link {
        color: #60a5fa;
      }
    `,
  ],
})
export class MovilInfoComponent {}
