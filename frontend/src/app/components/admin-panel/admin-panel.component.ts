import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService, Participant, AdminStats } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-admin-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-panel.component.html',
  styleUrl: './admin-panel.component.scss'
})
export class AdminPanelComponent implements OnInit {
  participants: Participant[] = [];
  stats: AdminStats = { total: 0, pending: 0, accepted: 0, rejected: 0, max_tickets: 300, remaining_tickets: 300 };
  isLoading = true;
  error = '';

  filter: 'all' | 'pending' | 'accepted' | 'rejected' = 'all';
  selectedImageUrl: string | null = null;
  selectedParticipant: Participant | null = null;

  processingId: string | null = null;
  actionSuccess = '';
  searchCedula = '';

  // Modal de edición
  editingParticipant: Participant | null = null;
  editData = { nombre: '', cedula: '', celular: '', email: '' };
  isSavingEdit = false;

  // Reenvío de correo
  resendingId: string | null = null;

  readonly apiUrl = environment.apiUrl;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.apiService.getParticipants().subscribe({
      next: (data) => {
        this.participants = data;
        this.updateStats(data);
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Error al cargar participantes';
        this.isLoading = false;
        if (err.status === 401) {
          this.authService.logout();
          this.router.navigate(['/']);
        }
      }
    });
  }

  private updateStats(data: Participant[]): void {
    const accepted = data.filter(p => p.status === 'accepted').length;
    this.stats = {
      total: data.length,
      pending: data.filter(p => p.status === 'pending').length,
      accepted,
      rejected: data.filter(p => p.status === 'rejected').length,
      max_tickets: 300,
      remaining_tickets: Math.max(0, 300 - accepted),
    };
  }

  get filteredParticipants(): Participant[] {
    let list = this.filter === 'all'
      ? this.participants
      : this.participants.filter(p => p.status === this.filter);

    if (this.searchCedula.trim()) {
      list = list.filter(p => p.cedula.includes(this.searchCedula.trim()));
    }
    return list;
  }

  viewImage(participant: Participant): void {
    this.selectedParticipant = participant;
    this.selectedImageUrl = `${this.apiUrl}${participant.payment_image_url}`;
  }

  closeImageViewer(): void {
    this.selectedImageUrl = null;
    this.selectedParticipant = null;
  }

  acceptParticipant(participant: Participant): void {
    if (this.processingId) return;
    this.processingId = participant.id;
    this.actionSuccess = '';

    this.apiService.acceptParticipant(participant.id).subscribe({
      next: (res) => {
        this.processingId = null;
        const smsStatus = res.sms_sent ? '📱 SMS ✅' : '';
        const emailStatus = res.email_sent ? '📧 Email ✅' : '📧 Email pendiente config';
        const notifs = [smsStatus, emailStatus].filter(Boolean).join(' · ');
        this.actionSuccess = `¡${participant.nombre} aceptado! Boleta #${String(res.ticket_number).padStart(3, '0')} — ${notifs}`;
        this.loadData();
        setTimeout(() => (this.actionSuccess = ''), 6000);
      },
      error: (err) => {
        this.processingId = null;
        this.error = err.error?.detail || 'Error al aceptar participante';
        setTimeout(() => (this.error = ''), 4000);
      }
    });
  }

  rejectParticipant(participant: Participant): void {
    if (!confirm(`¿Rechazar a ${participant.nombre}?`)) return;
    if (this.processingId) return;
    this.processingId = participant.id;

    this.apiService.rejectParticipant(participant.id).subscribe({
      next: () => {
        this.processingId = null;
        this.loadData();
      },
      error: (err) => {
        this.processingId = null;
        this.error = err.error?.detail || 'Error al rechazar';
        setTimeout(() => (this.error = ''), 4000);
      }
    });
  }

  openEdit(participant: Participant): void {
    this.editingParticipant = participant;
    this.editData = {
      nombre: participant.nombre,
      cedula: participant.cedula,
      celular: participant.celular,
      email: participant.email || ''
    };
  }

  closeEdit(): void {
    this.editingParticipant = null;
    this.isSavingEdit = false;
  }

  saveEdit(): void {
    if (!this.editingParticipant) return;
    this.isSavingEdit = true;
    this.apiService.updateParticipant(this.editingParticipant.id, this.editData).subscribe({
      next: () => {
        this.isSavingEdit = false;
        this.actionSuccess = `Datos de ${this.editData.nombre} actualizados correctamente`;
        this.closeEdit();
        this.loadData();
        setTimeout(() => (this.actionSuccess = ''), 4000);
      },
      error: (err) => {
        this.isSavingEdit = false;
        this.error = err.error?.detail || 'Error al actualizar los datos';
        setTimeout(() => (this.error = ''), 4000);
      }
    });
  }

  resendEmail(participant: Participant): void {
    if (this.resendingId) return;
    this.resendingId = participant.id;
    this.apiService.resendEmail(participant.id).subscribe({
      next: (res) => {
        this.resendingId = null;
        this.actionSuccess = `📧 ${res.message}`;
        setTimeout(() => (this.actionSuccess = ''), 5000);
      },
      error: (err) => {
        this.resendingId = null;
        this.error = err.error?.detail || 'Error al reenviar el correo';
        setTimeout(() => (this.error = ''), 4000);
      }
    });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/']);
  }

  getImageUrl(url: string): string {
    return `${this.apiUrl}${url}`;
  }

  formatDate(dateStr: string): string {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-CO', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }
}
