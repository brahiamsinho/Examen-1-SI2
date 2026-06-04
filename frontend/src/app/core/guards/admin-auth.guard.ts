import { inject } from '@angular/core';
import { Router, type CanActivateFn } from '@angular/router';
import { AdminAuthService } from '../services/admin-auth.service';

/**
 * Solo comprobación síncrona. Sin HTTP en el guard (evita pantalla congelada si /auth/me tarda o falla).
 * Tras login, `persist()` ya guardó token + me en storage.
 */
export const adminAuthGuard: CanActivateFn = () => {
  const auth = inject(AdminAuthService);
  const router = inject(Router);

  if (auth.isAdminSession()) {
    return true;
  }

  return router.parseUrl('/admin/login');
};
