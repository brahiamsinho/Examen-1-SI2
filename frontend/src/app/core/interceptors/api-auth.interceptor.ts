import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AdminAuthService } from '../services/admin-auth.service';
import { TallerAuthService } from '../services/taller-auth.service';
import { environment } from '../../../environments/environment';

/** Bearer: portal taller (`/api/portal/taller/*`) vs resto del panel admin. */
export const apiAuthInterceptor: HttpInterceptorFn = (req, next) => {
  const api = environment.apiUrl;
  const isApi = req.url.includes(`${api}/`) || req.url.endsWith(api);
  if (!isApi) {
    return next(req);
  }
  if (req.url.includes(`${api}/auth/login`)) {
    return next(req);
  }

  const portalPrefix = `${api}/portal/taller`;
  const isPortal = req.url.includes(portalPrefix);
  const isPublicRegistro =
    isPortal && req.url.includes('/portal/taller/registro') && req.method === 'POST';

  if (isPublicRegistro) {
    return next(req);
  }

  const token = isPortal
    ? inject(TallerAuthService).getAccessToken()
    : inject(AdminAuthService).getAccessToken();

  if (!token) {
    return next(req);
  }
  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    }),
  );
};
