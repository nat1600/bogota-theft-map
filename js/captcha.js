// captcha.js - Sistema de verificación CAPTCHA para SafeMap Bogotá
class CaptchaSystem {
    constructor() {
      this.captcha = '';
      this.alphabets = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz";
      this.statusElement = document.getElementById('captchaStatus');
      this.generatedElement = document.getElementById('generatedCaptcha');
      this.userInputElement = document.getElementById('enteredCaptcha');
      this.captchaScreen = document.getElementById('captchaScreen');
      this.appContainer = document.getElementById('appContainer');
      
      this.initEventListeners();
      this.generate(); // Generar captcha inicial
    }
  
    initEventListeners() {
      // Enter key support
      this.userInputElement?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.check();
        }
      });
      
      // Focus on input when screen shows
      setTimeout(() => {
        this.userInputElement?.focus();
      }, 100);
      
      // Prevenir paste en el input del captcha
      this.userInputElement?.addEventListener('paste', (e) => {
        e.preventDefault();
      });
    }
  
    generate() {
      const first = this.alphabets[Math.floor(Math.random() * this.alphabets.length)];
      const second = Math.floor(Math.random() * 10);
      const third = Math.floor(Math.random() * 10);
      const fourth = this.alphabets[Math.floor(Math.random() * this.alphabets.length)];
      const fifth = this.alphabets[Math.floor(Math.random() * this.alphabets.length)];
      const sixth = Math.floor(Math.random() * 10);
      
      this.captcha = first.toString() + second.toString() + third.toString() + 
                     fourth.toString() + fifth.toString() + sixth.toString();
      
      if (this.generatedElement) {
        this.generatedElement.value = this.captcha;
      }
      
      if (this.userInputElement) {
        this.userInputElement.value = '';
        setTimeout(() => {
          this.userInputElement.focus();
        }, 100);
      }
      
      this.updateStatus("Ingrese el código mostrado arriba", "default");
      
      console.log('CAPTCHA generado:', this.captcha); // Solo para debugging
    }
  
    check() {
      if (!this.userInputElement) return;
      
      const userValue = this.userInputElement.value.trim();
      
      if (userValue === this.captcha) {
        this.updateStatus("✅ Verificación exitosa", "success");
        this.onSuccess();
      } else {
        this.updateStatus("❌ Código incorrecto, intente nuevamente", "error");
        this.onError();
      }
    }
  
    updateStatus(message, type) {
      if (!this.statusElement) return;
      
      this.statusElement.textContent = message;
      this.statusElement.className = `captcha-status ${type}`;
    }
  
    onSuccess() {
      // Deshabilitar inputs después del éxito
      if (this.userInputElement) {
        this.userInputElement.disabled = true;
      }
      
      // Ocultar pantalla de captcha y mostrar aplicación principal
      setTimeout(() => {
        if (this.captchaScreen) {
          this.captchaScreen.classList.add('hidden');
        }
        
        if (this.appContainer) {
          this.appContainer.classList.add('visible');
        }
        
        // Inicializar el mapa si la función existe
        if (typeof initMap === 'function') {
          try {
            initMap();
          } catch (error) {
            console.error('Error inicializando el mapa:', error);
          }
        }
        
        // Callback personalizado para cuando el captcha es exitoso
        if (typeof window.onCaptchaSuccess === 'function') {
          window.onCaptchaSuccess();
        }
        
      }, 1000);
    }
  
    onError() {
      // Limpiar input
      if (this.userInputElement) {
        this.userInputElement.value = '';
        this.userInputElement.focus();
      }
      
      // Generar nuevo captcha después de un error
      setTimeout(() => {
        this.generate();
      }, 1500);
    }
  
    // Método público para regenerar captcha manualmente
    regenerate() {
      this.generate();
    }
  
    // Método para resetear el sistema de captcha
    reset() {
      this.generate();
      if (this.userInputElement) {
        this.userInputElement.disabled = false;
      }
      this.updateStatus("Por favor, complete el captcha para acceder", "default");
    }
  }
  
  // Funciones globales para mantener compatibilidad con HTML existente
  function generateCaptcha() {
    if (window.captchaSystem) {
      window.captchaSystem.regenerate();
    }
  }
  
  function checkCaptcha() {
    if (window.captchaSystem) {
      window.captchaSystem.check();
    }
  }
  
  // Inicialización automática cuando se carga el DOM
  document.addEventListener('DOMContentLoaded', function() {
    // Crear instancia global del sistema de captcha
    window.captchaSystem = new CaptchaSystem();
  });
  
  // Función opcional para manejar el éxito del captcha desde otros scripts
  window.onCaptchaSuccess = function() {
    console.log('CAPTCHA verificado exitosamente - Aplicación iniciada');
    
    // Aquí puedes agregar cualquier lógica adicional que necesites
    // cuando el captcha sea exitoso
    
    // Ejemplo: inicializar otros componentes
    if (typeof window.initializeApp === 'function') {
      window.initializeApp();
    }
  };