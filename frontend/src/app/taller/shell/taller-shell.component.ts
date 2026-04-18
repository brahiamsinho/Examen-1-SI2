import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { TallerAuthService } from '../../core/services/taller-auth.service';

@Component({
  selector: 'app-taller-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './taller-shell.component.html',
  styleUrl: './taller-shell.component.scss',
})
export class TallerShellComponent {
  readonly auth = inject(TallerAuthService);

  readonly nav = [
    { path: '/taller/panel', label: 'Resumen', exact: true },
    { path: '/taller/panel/mi-taller', label: 'Mi taller', exact: false },
    { path: '/taller/panel/tecnicos', label: 'Técnicos', exact: false },
  ] as const;
}
