// src/app/core/interceptors/auth.interceptor.ts
// =========================================================
// Interceptor HTTP — agrega el token JWT a todas las requests
// Angular 17+ usa provideHttpClient con withInterceptors()
// =========================================================
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const token = authService.getToken();

  // Clonar la request con el header Authorization
  const authReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token expirado o inválido — limpiar sesión y redirigir
        localStorage.clear();
        router.navigate(['/auth/login']);
      }
      return throwError(() => error);
    })
  );
};
