// src/environments/environment.ts
// =========================================================
// Entorno de DESARROLLO
// Los valores de producción van en environment.production.ts
// Angular sustituye automáticamente el archivo al compilar con --configuration production
// =========================================================
export const environment = {
  production: false,
  /** Dev: mismo origen vía proxy.conf.js → BACKEND_URL en .env raíz */
  apiUrl: '/api',
  appName: 'Plataforma Emergencias Vehiculares',
};
