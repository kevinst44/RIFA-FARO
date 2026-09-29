import { Routes } from '@angular/router';
import { RaffleFormComponent } from './components/raffle-form/raffle-form.component';
import { AdminPanelComponent } from './components/admin-panel/admin-panel.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: RaffleFormComponent },
  { path: 'admin', component: AdminPanelComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '' }
];
