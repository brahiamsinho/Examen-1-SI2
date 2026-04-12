// src/app/core/guards/auth.guard.ts
// =========================================================
// Guard funcional (Angular 17+) — protege rutas privadas
// Si no hay token: redirige a /auth/login
// =========================================================
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Guardar la URL de retorno para redirigir después del login
  router.navigate(['/auth/login'], {
    queryParams: { returnUrl: state.url },
  });
  return false;
};
