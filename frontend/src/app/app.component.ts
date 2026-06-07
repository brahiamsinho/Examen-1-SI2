import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { PwaInstallBannerComponent } from './core/components/pwa-install-banner.component';
import { PwaUpdateBannerComponent } from './core/components/pwa-update-banner.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, PwaInstallBannerComponent, PwaUpdateBannerComponent],
  template: `
    <router-outlet />
    <app-pwa-install-banner />
    <app-pwa-update-banner />
  `,
  styles: [],
})
export class AppComponent {
  title = 'emergencias-frontend';
}
