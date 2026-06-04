import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import type { PricingPlanDto } from '../models/admin-api.models';

export interface PublicTenantOption {
  slug: string;
  nombre: string;
}

export interface StripePublicConfigDto {
  enabled: boolean;
  publishable_key: string | null;
}

export interface PublicCheckoutPayload {
  plan_slug: string;
  email: string;
  success_url: string;
  cancel_url: string;
}

export interface PublicCheckoutResponse {
  checkout_url: string;
  session_id: string;
}

/** Endpoints públicos de `/api/public/*` (sin Bearer). */
@Injectable({ providedIn: 'root' })
export class PublicApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/public`;

  listActiveTenants(): Observable<PublicTenantOption[]> {
    return this.http.get<PublicTenantOption[]>(`${this.base}/tenants`);
  }

  listPricingPlans(): Observable<PricingPlanDto[]> {
    return this.http.get<PricingPlanDto[]>(`${this.base}/pricing/plans`);
  }

  getStripeConfig(): Observable<StripePublicConfigDto> {
    return this.http.get<StripePublicConfigDto>(`${this.base}/pricing/stripe-config`);
  }

  createCheckout(payload: PublicCheckoutPayload): Observable<PublicCheckoutResponse> {
    return this.http.post<PublicCheckoutResponse>(`${this.base}/pricing/checkout`, payload);
  }
}
