// src/app/core/services/auth.service.ts
// =========================================================
// Servicio de autenticación Angular
// Maneja: login, logout, tokens JWT, estado de sesión
// =========================================================
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

interface LoginRequest {
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

interface MeResponse {
  id: number;
  nombres: string;
  apellidos: string;
  email: string;
  username: string | null;
  roles: string[];
  permisos: string[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_KEY = 'refresh_token';
  private readonly USER_KEY = 'current_user';

  // Signal reactivo — todos los componentes se actualizan automáticamente
  currentUser = signal<MeResponse | null>(null);

  constructor(private http: HttpClient, private router: Router) {
    // Restaurar el usuario desde localStorage al recargar
    const stored = localStorage.getItem(this.USER_KEY);
    if (stored) {
      this.currentUser.set(JSON.parse(stored));
    }
  }

  login(credentials: LoginRequest): Observable<TokenResponse> {
    return this.http
      .post<TokenResponse>(`${environment.apiUrl}/auth/login`, credentials)
      .pipe(
        tap((response) => {
          // Guardar tokens y cargar datos del usuario
          localStorage.setItem(this.TOKEN_KEY, response.access_token);
          localStorage.setItem(this.REFRESH_KEY, response.refresh_token);
          this.loadCurrentUser();
        })
      );
  }

  logout(): void {
    this.http.post(`${environment.apiUrl}/auth/logout`, {}).subscribe({
      complete: () => this.clearSession(),
      error: () => this.clearSession(), // Limpiar de todas formas si falla
    });
  }

  private loadCurrentUser(): void {
    this.http.get<MeResponse>(`${environment.apiUrl}/auth/me`).subscribe({
      next: (user) => {
        this.currentUser.set(user);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      },
    });
  }

  private clearSession(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
    localStorage.removeItem(this.USER_KEY);
    this.currentUser.set(null);
    this.router.navigate(['/auth/login']);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  hasPermission(codigo: string): boolean {
    return this.currentUser()?.permisos?.includes(codigo) ?? false;
  }

  hasRole(rol: string): boolean {
    return this.currentUser()?.roles?.includes(rol) ?? false;
  }
}
