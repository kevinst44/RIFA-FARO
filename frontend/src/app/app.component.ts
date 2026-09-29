import { Component } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';
import { LoginModalComponent } from './components/login-modal/login-modal.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, LoginModalComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  showLoginModal = false;
  isAdminRoute = false;

  constructor(private authService: AuthService, private router: Router) {
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe((e: any) => {
      this.isAdminRoute = e.url === '/admin' || e.url.startsWith('/admin');
    });
  }

  onFaroClick(): void {
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/admin']);
    } else {
      this.showLoginModal = true;
    }
  }

  onLoginSuccess(): void {
    this.showLoginModal = false;
    this.router.navigate(['/admin']);
  }

  onModalClose(): void {
    this.showLoginModal = false;
  }
}
