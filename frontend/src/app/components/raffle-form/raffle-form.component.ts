import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService, PaymentInfo, Availability } from '../../services/api.service';

@Component({
  selector: 'app-raffle-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './raffle-form.component.html',
  styleUrl: './raffle-form.component.scss'
})
export class RaffleFormComponent implements OnInit {
  form!: FormGroup;
  paymentInfo: PaymentInfo | null = null;
  availability: Availability | null = null;
  knowsWhereToPay: boolean | null = null;

  selectedFile: File | null = null;
  selectedFilePreview: string | null = null;
  isDragOver = false;

  isSubmitting = false;
  submitSuccess = false;
  submitError = '';
  ticketNumber: number | null = null;
  participantId: string | null = null;

  constructor(private fb: FormBuilder, private apiService: ApiService) {}

  ngOnInit(): void {
    const emailPattern = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;

    this.form = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(100)]],
      cedula: ['', [Validators.required, Validators.pattern(/^\d{6,12}$/)]],
      celular: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
      email: ['', [Validators.required, Validators.pattern(emailPattern)]]
    });

    this.apiService.getPaymentInfo().subscribe({
      next: (info) => (this.paymentInfo = info),
      error: (err) => console.error('Error al cargar info de pago', err)
    });

    this.apiService.getAvailability().subscribe({
      next: (data) => (this.availability = data),
      error: (err) => console.error('Error al cargar disponibilidad', err)
    });
  }

  setKnowsWhereToPay(knows: boolean): void {
    this.knowsWhereToPay = knows;
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.processFile(input.files[0]);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = true;
  }

  onDragLeave(): void {
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver = false;
    const files = event.dataTransfer?.files;
    if (files && files[0]) {
      this.processFile(files[0]);
    }
  }

  private processFile(file: File): void {
    if (!file.type.startsWith('image/')) {
      this.submitError = 'Solo se permiten imágenes (JPG, PNG, WEBP)';
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      this.submitError = 'La imagen no puede superar 10MB';
      return;
    }
    this.submitError = '';
    this.selectedFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      this.selectedFilePreview = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  removeFile(): void {
    this.selectedFile = null;
    this.selectedFilePreview = null;
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    if (!this.selectedFile) {
      this.submitError = 'Por favor adjunta el comprobante de pago';
      return;
    }

    this.isSubmitting = true;
    this.submitError = '';

    const formData = new FormData();
    formData.append('nombre', this.form.value.nombre.trim());
    formData.append('cedula', this.form.value.cedula.trim());
    formData.append('celular', this.form.value.celular.trim());
    formData.append('email', this.form.value.email.trim().toLowerCase());
    formData.append('payment_image', this.selectedFile);

    this.apiService.submitParticipant(formData).subscribe({
      next: (res: any) => {
        this.submitSuccess = true;
        this.isSubmitting = false;
        this.ticketNumber = res.ticket_number ?? null;
        this.participantId = res.id ?? null;
      },
      error: (err) => {
        this.submitError = err.error?.detail || 'Error al enviar el formulario. Intenta de nuevo.';
        this.isSubmitting = false;
      }
    });
  }

  downloadTicket(): void {
    if (!this.participantId) return;
    const url = `${this.apiService.getBaseUrl()}/api/participants/${this.participantId}/ticket`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `boleta-${String(this.ticketNumber).padStart(3,'0')}.html`;
    a.target = '_blank';
    a.click();
  }

  resetForm(): void {
    this.form.reset();
    this.selectedFile = null;
    this.selectedFilePreview = null;
    this.knowsWhereToPay = null;
    this.submitSuccess = false;
    this.submitError = '';
    this.ticketNumber = null;
    this.participantId = null;
  }

  get nombreCtrl() { return this.form.get('nombre'); }
  get cedulaCtrl() { return this.form.get('cedula'); }
  get celularCtrl() { return this.form.get('celular'); }
  get emailCtrl() { return this.form.get('email'); }
}
