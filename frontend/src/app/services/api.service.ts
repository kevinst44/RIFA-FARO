import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Participant {
  id: string;
  nombre: string;
  cedula: string;
  celular: string;
  email: string;
  payment_image_url: string;
  status: 'pending' | 'accepted' | 'rejected';
  ticket_number: number | null;
  created_at: string;
  accepted_at: string | null;
}

export interface PaymentInfo {
  bank: string;
  account_number: string;
  account_type: string;
  owner: string;
  document: string;
  raffle_name: string;
}

export interface Availability {
  max_tickets: number;
  assigned: number;
  remaining: number;
  sold_out: boolean;
  percentage_taken: number;
}

export interface AdminStats {
  total: number;
  pending: number;
  accepted: number;
  rejected: number;
  max_tickets: number;
  remaining_tickets: number;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  getPaymentInfo(): Observable<PaymentInfo> {
    return this.http.get<PaymentInfo>(`${this.apiUrl}/api/participants/payment-info`);
  }

  getAvailability(): Observable<Availability> {
    return this.http.get<Availability>(`${this.apiUrl}/api/participants/availability`);
  }

  submitParticipant(formData: FormData): Observable<{ id: string; message: string; remaining_tickets: number }> {
    return this.http.post<{ id: string; message: string; remaining_tickets: number }>(
      `${this.apiUrl}/api/participants/`,
      formData
    );
  }

  getParticipants(): Observable<Participant[]> {
    return this.http.get<Participant[]>(`${this.apiUrl}/api/admin/participants`);
  }

  acceptParticipant(id: string): Observable<{ message: string; ticket_number: number; sms_sent: boolean; email_sent: boolean; remaining_tickets: number }> {
    return this.http.post<{ message: string; ticket_number: number; sms_sent: boolean; email_sent: boolean; remaining_tickets: number }>(
      `${this.apiUrl}/api/admin/participants/${id}/accept`,
      {}
    );
  }

  updateParticipant(id: string, data: { nombre?: string; cedula?: string; celular?: string; email?: string }): Observable<Participant> {
    return this.http.put<Participant>(`${this.apiUrl}/api/admin/participants/${id}`, data);
  }

  resendEmail(id: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.apiUrl}/api/admin/participants/${id}/resend-email`, {});
  }

  rejectParticipant(id: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${this.apiUrl}/api/admin/participants/${id}/reject`,
      {}
    );
  }

  getStats(): Observable<AdminStats> {
    return this.http.get<AdminStats>(`${this.apiUrl}/api/admin/stats`);
  }
}
