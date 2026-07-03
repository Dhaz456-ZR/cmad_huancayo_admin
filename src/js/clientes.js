(function() {
    'use strict';

    // ===== CONFIGURACIÓN =====
    const API_BASE = '/api/clientes';
    let currentPage = 1;
    let currentLimit = 10;
    let currentSearch = '';
    let currentSortBy = 'id';
    let currentSortOrder = 'desc';
    let totalPages = 1;
    let totalItems = 0;

    // ===== ELEMENTOS DOM =====
    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const pageNumbers = document.getElementById('pageNumbers');
    const paginationInfo = document.getElementById('paginationInfo');

    // ===== ESTADÍSTICAS =====
    const totalClientesEl = document.getElementById('totalClientes');
    const verificadosEl = document.getElementById('verificados');
    const bloqueadosEl = document.getElementById('bloqueados');
    const registradosHoyEl = document.getElementById('registradosHoy');

    // ===== FUNCIONES =====

    // Cargar estadísticas
    async function loadStats() {
        try {
            const response = await fetch('/api/clientes/estadisticas');
            const result = await response.json();
            
            if (result.success) {
                totalClientesEl.textContent = result.data.total;
                verificadosEl.textContent = result.data.verificados;
                bloqueadosEl.textContent = result.data.bloqueados;
                registradosHoyEl.textContent = result.data.registrados_hoy;
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    // Cargar clientes
    async function loadClientes() {
        try {
            const url = `${API_BASE}?search=${encodeURIComponent(currentSearch)}&page=${currentPage}&limit=${currentLimit}&sort_by=${currentSortBy}&sort_order=${currentSortOrder}`;
            
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading-text">
                        <i class="fas fa-spinner fa-spin"></i> Cargando clientes...
                    </td>
                </tr>
            `;

            const response = await fetch(url);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Error al cargar clientes');
            }

            const clientes = result.data;
            totalItems = result.total;
            totalPages = result.total_pages;

            // Renderizar tabla
            if (clientes.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align:center;padding:40px;color:rgba(255,255,255,0.2);">
                            <i class="fas fa-inbox" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                            No hay clientes registrados
                        </td>
                    </tr>
                `;
            } else {
                tableBody.innerHTML = clientes.map(cliente => `
                    <tr>
                        <td><span style="font-weight:500;">${cliente.id}</span></td>
                        <td><strong>${cliente.nombre}</strong></td>
                        <td>${cliente.dni}</td>
                        <td style="font-family:monospace;letter-spacing:1px;color:rgba(255,255,255,0.4);">
                            **** **** **** ${cliente.tarjeta.slice(-4)}
                        </td>
                        <td>
                            <span class="badge badge-${cliente.estado.toLowerCase()}">
                                ${cliente.estado}
                            </span>
                        </td>
                        <td style="color:rgba(255,255,255,0.3);font-size:13px;">
                            ${cliente.fecha_creacion_formateada}
                        </td>
                        <td>
                            <button class="btn-action ver" onclick="verCliente(${cliente.id})" title="Ver">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn-action editar" onclick="editarCliente(${cliente.id})" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${cliente.estado === 'Bloqueado' ? `
                                <button class="btn-action activar" onclick="activarCliente(${cliente.id})" title="Activar">
                                    <i class="fas fa-check-circle"></i>
                                </button>
                            ` : `
                                <button class="btn-action bloquear" onclick="bloquearCliente(${cliente.id})" title="Bloquear">
                                    <i class="fas fa-ban"></i>
                                </button>
                            `}
                            <button class="btn-action eliminar" onclick="eliminarCliente(${cliente.id})" title="Eliminar">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `).join('');
            }

            // Actualizar paginación
            updatePagination();

        } catch (error) {
            console.error('Error:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align:center;padding:40px;color:#ff6b7a;">
                        <i class="fas fa-exclamation-circle" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                        ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    // Actualizar paginación
    function updatePagination() {
        const start = (currentPage - 1) * currentLimit + 1;
        const end = Math.min(currentPage * currentLimit, totalItems);
        
        paginationInfo.textContent = `Mostrando ${totalItems > 0 ? start : 0} - ${end} de ${totalItems} clientes`;

        prevPageBtn.disabled = currentPage <= 1;
        nextPageBtn.disabled = currentPage >= totalPages;

        let pagesHtml = '';
        const maxVisible = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(totalPages, startPage + maxVisible - 1);

        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }

        for (let i = startPage; i <= endPage; i++) {
            pagesHtml += `
                <button class="page-number ${i === currentPage ? 'active' : ''}" onclick="irPagina(${i})">
                    ${i}
                </button>
            `;
        }

        pageNumbers.innerHTML = pagesHtml;
    }

    // ===== FUNCIONES GLOBALES =====

    window.irPagina = function(page) {
        if (page < 1 || page > totalPages || page === currentPage) return;
        currentPage = page;
        loadClientes();
    };

    window.verCliente = async function(id) {
        try {
            const response = await fetch(`${API_BASE}/${id}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error);
            }

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
            const response = await fetch(`${API_BASE}/${id}`);
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error);
            }

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
            const response = await fetch(`${API_BASE}/${id}/bloquear`, {
                method: 'PUT'
            });
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            Swal.fire('¡Bloqueado!', 'El cliente ha sido bloqueado.', 'success');
            loadClientes();
            loadStats();
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
            const response = await fetch(`${API_BASE}/${id}/activar`, {
                method: 'PUT'
            });
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            Swal.fire('¡Activado!', 'El cliente ha sido activado.', 'success');
            loadClientes();
            loadStats();
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
            const response = await fetch(`${API_BASE}/${id}`, {
                method: 'DELETE'
            });
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            Swal.fire('¡Eliminado!', 'El cliente ha sido eliminado.', 'success');
            loadClientes();
            loadStats();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    };

    // ===== FUNCIONES DE MODAL =====

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

    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
                document.body.style.overflow = '';
            }
        });
    });

    // ===== EVENTOS =====

    searchInput.addEventListener('input', function() {
        currentSearch = this.value;
        currentPage = 1;
        loadClientes();
    });

    refreshBtn.addEventListener('click', function() {
        loadClientes();
        loadStats();
        this.querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            this.querySelector('i').classList.remove('fa-spin');
        }, 1000);
    });

    prevPageBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadClientes();
        }
    });

    nextPageBtn.addEventListener('click', function() {
        if (currentPage < totalPages) {
            currentPage++;
            loadClientes();
        }
    });

    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', function() {
            const sortBy = this.dataset.sort;
            if (currentSortBy === sortBy) {
                currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                currentSortBy = sortBy;
                currentSortOrder = 'desc';
            }
            
            document.querySelectorAll('.sortable').forEach(el => {
                el.classList.remove('sorted-asc', 'sorted-desc');
            });
            this.classList.add(`sorted-${currentSortOrder}`);
            
            currentPage = 1;
            loadClientes();
        });
    });

    // ===== FORMULARIO EDITAR =====
    document.getElementById('editForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const id = document.getElementById('editId').value;
        const nombre = document.getElementById('editNombre').value.trim();
        const dni = document.getElementById('editDni').value.trim();
        const tarjeta = document.getElementById('editTarjeta').value.trim();
        const estado = document.getElementById('editEstado').value;

        if (!nombre || nombre.length < 2) {
            Swal.fire('Error', 'El nombre debe tener al menos 2 caracteres.', 'error');
            return;
        }
        if (!/^[0-9]{8}$/.test(dni)) {
            Swal.fire('Error', 'El DNI debe tener 8 dígitos.', 'error');
            return;
        }
        if (!/^[0-9]{16}$/.test(tarjeta)) {
            Swal.fire('Error', 'La tarjeta debe tener 16 dígitos.', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('nombre', nombre);
            formData.append('dni', dni);
            formData.append('tarjeta', tarjeta);
            formData.append('estado', estado);

            const response = await fetch(`${API_BASE}/${id}`, {
                method: 'PUT',
                body: formData
            });
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error);
            }

            Swal.fire('¡Guardado!', 'Los cambios se guardaron correctamente.', 'success');
            closeModal('editModal');
            loadClientes();
            loadStats();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    });

    // ===== FORMULARIO NUEVO CLIENTE =====
    document.getElementById('addForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const nombre = document.getElementById('addNombre').value.trim();
        const dni = document.getElementById('addDni').value.trim();
        const tarjeta = document.getElementById('addTarjeta').value.trim();
        const password = document.getElementById('addPassword').value.trim();
        const pin = document.getElementById('addPin').value.trim();

        if (!nombre || nombre.length < 2) {
            Swal.fire('Error', 'El nombre debe tener al menos 2 caracteres.', 'error');
            return;
        }
        if (!/^[0-9]{8}$/.test(dni)) {
            Swal.fire('Error', 'El DNI debe tener 8 dígitos.', 'error');
            return;
        }
        if (!/^[0-9]{16}$/.test(tarjeta)) {
            Swal.fire('Error', 'La tarjeta debe tener 16 dígitos.', 'error');
            return;
        }
        if (password.length < 6) {
            Swal.fire('Error', 'La contraseña debe tener al menos 6 caracteres.', 'error');
            return;
        }
        if (!/^[0-9]{4}$/.test(pin)) {
            Swal.fire('Error', 'El PIN debe tener 4 dígitos.', 'error');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('nombre', nombre);
            formData.append('dni', dni);
            formData.append('tarjeta', tarjeta);
            formData.append('password', password);
            formData.append('pin1', pin[0]);
            formData.append('pin2', pin[1]);
            formData.append('pin3', pin[2]);
            formData.append('pin4', pin[3]);

            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });

            if (response.status === 303 || response.status === 302) {
                Swal.fire('¡Creado!', 'El cliente ha sido registrado exitosamente.', 'success');
                closeModal('addModal');
                loadClientes();
                loadStats();
                document.getElementById('addForm').reset();
            } else {
                const data = await response.json();
                throw new Error(data.mensaje || 'Error al crear cliente');
            }
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    });

    // ===== BOTÓN NUEVO CLIENTE =====
    document.getElementById('addBtn').addEventListener('click', function() {
        document.getElementById('addForm').reset();
        openModal('addModal');
    });

    // ===== INICIALIZAR =====
    loadClientes();
    loadStats();

    setInterval(() => {
        loadStats();
    }, 30000);

})();