import { inject } from '@angular/core';
import { type CanActivateFn } from '@angular/router';
import { AdminAuthService } from '../services/admin-auth.service';

/** Si ya hay sesión admin, no mostrar login (misma recarga que post-login). */
export const adminGuestGuard: CanActivateFn = () => {
  const auth = inject(AdminAuthService);

  if (auth.isAdminSession()) {
    globalThis.location.replace('/admin/panel');
    return false;
  }
  return true;
};
