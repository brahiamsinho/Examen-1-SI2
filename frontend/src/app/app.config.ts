// src/app/app.config.ts
// =========================================================
// Configuración de la aplicación Angular (standalone, sin NgModule)
// Angular 17 usa provideX() en lugar de imports en AppModule
// =========================================================
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withViewTransitions } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Router con animaciones de transición entre rutas
    provideRouter(routes, withViewTransitions()),

    // HTTP client con el interceptor de autenticación
    provideHttpClient(withInterceptors([authInterceptor])),

    // Animaciones asíncronas (mejor performance)
    provideAnimationsAsync(),
  ],
};
