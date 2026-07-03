// ============================================
// ADMIN.JS - FUNCIONES GLOBALES
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Panel Administrativo CMAC Huancayo cargado');

    // ===== CARGAR ESTADÍSTICAS DEL DASHBOARD =====
    async function loadDashboardStats() {
        try {
            const response = await fetch('/api/clientes/estadisticas');
            const result = await response.json();
            
            if (result.success && document.getElementById('totalClientes')) {
                document.getElementById('totalClientes').textContent = result.data.total;
                document.getElementById('verificados').textContent = result.data.verificados;
                document.getElementById('bloqueados').textContent = result.data.bloqueados;
                document.getElementById('registradosHoy').textContent = result.data.registrados_hoy;
            }
        } catch (error) {
            console.error('Error cargando estadísticas del dashboard:', error);
        }
    }

    // ===== CARGAR ACTIVIDADES RECIENTES =====
    async function loadRecentActivities() {
        try {
            const list = document.getElementById('movementsList');
            if (!list) return;

            const response = await fetch('/api/clientes?limit=5');
            const result = await response.json();
            
            const totalEl = document.getElementById('totalActividades');
            
            if (result.success && result.data.length > 0) {
                if (totalEl) totalEl.textContent = `${result.total} clientes totales`;
                
                list.innerHTML = result.data.map(cliente => `
                    <div class="movement-item">
                        <div class="movement-icon entry">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="movement-info">
                            <span class="movement-desc">${cliente.nombre}</span>
                            <span class="movement-date">DNI: ${cliente.dni} • ${cliente.fecha_creacion_formateada || 'Nuevo'}</span>
                        </div>
                        <div class="movement-status">
                            <span class="badge badge-${cliente.estado.toLowerCase()}">${cliente.estado}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                list.innerHTML = `
                    <div class="movement-empty">
                        <i class="fas fa-inbox"></i>
                        <p>No hay clientes registrados</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error cargando actividades:', error);
            const list = document.getElementById('movementsList');
            if (list) {
                list.innerHTML = `
                    <div class="movement-empty">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Error al cargar actividades</p>
                    </div>
                `;
            }
        }
    }

    // ===== INICIALIZAR DASHBOARD =====
    if (document.querySelector('.header-left h1')?.textContent.includes('Dashboard')) {
        loadDashboardStats();
        loadRecentActivities();
        
        // Recargar cada 30 segundos
        setInterval(() => {
            loadDashboardStats();
            loadRecentActivities();
        }, 30000);
    }

    // ===== FUNCIÓN PARA ACTUALIZAR REFRESH BUTTONS =====
    document.querySelectorAll('.btn-refresh-premium, .btn-refresh').forEach(btn => {
        btn.addEventListener('click', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.add('fa-spin');
                setTimeout(() => {
                    icon.classList.remove('fa-spin');
                }, 1000);
            }
        });
    });

    // ===== SIDEBAR TOGGLE PARA MÓVIL =====
    // Opcional: agregar toggle para móvil si es necesario

});

// ============================================
// FUNCIONES PARA CLIENTES
// ============================================

window.irPagina = function(page) {
    if (window.loadClientesPage) {
        window.loadClientesPage(page);
    }
};

window.verCliente = async function(id) {
    try {
        const response = await fetch(`/api/clientes/${id}`);
        const result = await response.json();
        if (!result.success) throw new Error(result.error);
        const cliente = result.data;
        
        document.getElementById('viewId').textContent = cliente.id;
        document.getElementById('viewNombre').textContent = cliente.nombre;
        document.getElementById('viewDni').textContent = cliente.dni;
        document.getElementById('viewTarjeta').textContent = cliente.tarjeta;
        document.getElementById('viewEstado').innerHTML = `<span class="badge badge-${cliente.estado.toLowerCase()}">${cliente.estado}</span>`;
        document.getElementById('viewFecha').textContent = cliente.fecha_creacion_formateada;
        
        openModal('viewModal');
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
};

window.editarCliente = async function(id) {
    try {
        const response = await fetch(`/api/clientes/${id}`);
        const result = await response.json();
        if (!result.success) throw new Error(result.error);
        const cliente = result.data;
        
        document.getElementById('editId').value = cliente.id;
        document.getElementById('editNombre').value = cliente.nombre;
        document.getElementById('editDni').value = cliente.dni;
        document.getElementById('editTarjeta').value = cliente.tarjeta;
        document.getElementById('editEstado').value = cliente.estado;
        
        openModal('editModal');
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
};

window.bloquearCliente = async function(id) {
    const result = await Swal.fire({
        title: '¿Bloquear cliente?',
        text: 'El cliente no podrá acceder a su cuenta.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, bloquear',
        cancelButtonText: 'Cancelar'
    });
    if (!result.isConfirmed) return;
    try {
        const response = await fetch(`/api/clientes/${id}/bloquear`, { method: 'PUT' });
        const data = await response.json();
        if (!data.success) throw new Error(data.error);
        Swal.fire('¡Bloqueado!', 'El cliente ha sido bloqueado.', 'success');
        if (window.loadClientesPage) window.loadClientesPage();
        if (window.loadStats) window.loadStats();
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
};

window.activarCliente = async function(id) {
    const result = await Swal.fire({
        title: '¿Activar cliente?',
        text: 'El cliente podrá acceder nuevamente a su cuenta.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#22c55e',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, activar',
        cancelButtonText: 'Cancelar'
    });
    if (!result.isConfirmed) return;
    try {
        const response = await fetch(`/api/clientes/${id}/activar`, { method: 'PUT' });
        const data = await response.json();
        if (!data.success) throw new Error(data.error);
        Swal.fire('¡Activado!', 'El cliente ha sido activado.', 'success');
        if (window.loadClientesPage) window.loadClientesPage();
        if (window.loadStats) window.loadStats();
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
};

window.eliminarCliente = async function(id) {
    const result = await Swal.fire({
        title: '¿Eliminar cliente?',
        text: 'Esta acción no se puede deshacer.',
        icon: 'error',
        showCancelButton: true,
        confirmButtonColor: '#dc2626',
        cancelButtonColor: '#6b7280',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });
    if (!result.isConfirmed) return;
    try {
        const response = await fetch(`/api/clientes/${id}`, { method: 'DELETE' });
        const data = await response.json();
        if (!data.success) throw new Error(data.error);
        Swal.fire('¡Eliminado!', 'El cliente ha sido eliminado.', 'success');
        if (window.loadClientesPage) window.loadClientesPage();
        if (window.loadStats) window.loadStats();
    } catch (error) {
        Swal.fire('Error', error.message, 'error');
    }
};

// ============================================
// FUNCIONES DE MODAL
// ============================================

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

window.closeModal = function(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
};

// Cerrar modal al hacer clic fuera
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('show');
            document.body.style.overflow = '';
        }
    });
});