/**
 * Sistema de notificaciones con sonido para nuevos turnos
 */

class TurnoNotification {
    constructor() {
        this.audioContext = null;
        this.lastTurnCount = 0;
        this.enabled = true;
        this.init();
    }

    init() {
        // Pedir permiso para notificaciones del navegador
        if ("Notification" in window && Notification.permission === "default") {
            Notification.requestPermission();
        }
    }

    // Generar sonido de notificación usando Web Audio API
    playNotificationSound() {
        if (!this.enabled) return;

        try {
            // Crear contexto de audio si no existe
            if (!this.audioContext) {
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            }

            const ctx = this.audioContext;
            const now = ctx.currentTime;

            // Crear oscilador para el sonido
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);

            // Configurar sonido agradable (dos tonos)
            oscillator.frequency.value = 800; // Frecuencia inicial
            oscillator.type = 'sine';

            // Envelope para volumen
            gainNode.gain.setValueAtTime(0, now);
            gainNode.gain.linearRampToValueAtTime(0.3, now + 0.01);
            gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);

            oscillator.start(now);
            oscillator.stop(now + 0.3);

            // Segundo tono
            setTimeout(() => {
                const osc2 = ctx.createOscillator();
                const gain2 = ctx.createGain();
                
                osc2.connect(gain2);
                gain2.connect(ctx.destination);
                
                osc2.frequency.value = 1000;
                osc2.type = 'sine';
                
                const now2 = ctx.currentTime;
                gain2.gain.setValueAtTime(0, now2);
                gain2.gain.linearRampToValueAtTime(0.3, now2 + 0.01);
                gain2.gain.exponentialRampToValueAtTime(0.01, now2 + 0.3);
                
                osc2.start(now2);
                osc2.stop(now2 + 0.3);
            }, 150);

        } catch (err) {
            console.warn('Error reproduciendo sonido:', err);
        }
    }

    // Mostrar notificación del navegador
    showBrowserNotification(turno) {
        if ("Notification" in window && Notification.permission === "granted") {
            const notification = new Notification("Nuevo turno registrado", {
                body: `${turno.nombre} - ${turno.area_nombre}`,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico',
                tag: 'turno-' + turno.id,
                requireInteraction: false
            });

            // Auto-cerrar después de 5 segundos
            setTimeout(() => notification.close(), 5000);
        }
    }

    // Mostrar notificación en pantalla (toast)
    showToastNotification(turno) {
        // Crear elemento de notificación
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <div class="toast-header">
                <i class="bi bi-bell-fill text-primary me-2"></i>
                <strong>Nuevo Turno</strong>
            </div>
            <div class="toast-body">
                <strong>${turno.nombre}</strong><br>
                ${turno.area_nombre}
            </div>
        `;

        // Agregar al DOM
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 9999;
            `;
            document.body.appendChild(container);
        }

        container.appendChild(toast);

        // Animar entrada
        setTimeout(() => toast.classList.add('show'), 10);

        // Auto-remover después de 4 segundos
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // Verificar nuevos turnos
    checkNewTurns(currentCount) {
        if (this.lastTurnCount > 0 && currentCount > this.lastTurnCount) {
            return currentCount - this.lastTurnCount;
        }
        this.lastTurnCount = currentCount;
        return 0;
    }

    // Notificar nuevo turno
    notifyNewTurn(turno) {
        this.playNotificationSound();
        this.showToastNotification(turno);
        this.showBrowserNotification(turno);
    }

    // Activar/desactivar sonido
    toggleSound() {
        this.enabled = !this.enabled;
        return this.enabled;
    }
}

// CSS para las notificaciones toast
const style = document.createElement('style');
style.textContent = `
.toast-notification {
    background: white;
    border-left: 4px solid #0d6efd;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 10px;
    max-width: 350px;
    opacity: 0;
    transform: translateX(400px);
    transition: all 0.3s ease;
}

.toast-notification.show {
    opacity: 1;
    transform: translateX(0);
}

.toast-notification .toast-header {
    background: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    border-radius: 7px 7px 0 0;
    padding: 10px 15px;
    font-size: 14px;
}

.toast-notification .toast-body {
    padding: 15px;
    font-size: 14px;
}
`;
document.head.appendChild(style);

// Exportar instancia global
window.turnoNotifier = new TurnoNotification();
