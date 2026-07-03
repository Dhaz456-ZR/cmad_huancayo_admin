document.addEventListener('DOMContentLoaded', function() {

    const tableBody = document.getElementById('tableBody');
    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');

    const totalCreditosEl = document.getElementById('totalCreditos');
    const creditosAprobadosEl = document.getElementById('creditosAprobados');
    const creditosPendientesEl = document.getElementById('creditosPendientes');
    const creditosRechazadosEl = document.getElementById('creditosRechazados');

    async function loadStats() {
        try {
            const response = await fetch('/api/creditos/estadisticas');
            const result = await response.json();
            
            if (result.success) {
                totalCreditosEl.textContent = result.data.total;
                creditosAprobadosEl.textContent = result.data.aprobados;
                creditosPendientesEl.textContent = result.data.pendientes;
                creditosRechazadosEl.textContent = result.data.rechazados;
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    async function loadCreditos(search = '') {
        try {
            const url = `/api/creditos${search ? `?search=${encodeURIComponent(search)}` : ''}`;
            
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="loading-text">
                        <i class="fas fa-spinner fa-spin"></i> Cargando créditos...
                    </td>
                </tr>
            `;

            const response = await fetch(url);
            console.log('Response:', response); // Debug
            const result = await response.json();
            console.log('Result:', result); // Debug

            if (!result.success) {
                throw new Error(result.error || 'Error al cargar créditos');
            }

            const creditos = result.data;

            if (creditos.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" style="text-align:center;padding:40px;color:rgba(255,255,255,0.2);">
                            <i class="fas fa-inbox" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                            No hay créditos registrados
                        </td>
                    </tr>
                `;
            } else {
                tableBody.innerHTML = creditos.map(credito => {
                    // Mostrar botones según el estado
                    let acciones = '';
                    if (credito.estado === 'Pendiente') {
                        acciones = `
                            <button class="btn-action aprobar" onclick="aprobarCredito(${credito.id})" title="Aprobar">
                                <i class="fas fa-check"></i>
                            </button>
                            <button class="btn-action rechazar" onclick="rechazarCredito(${credito.id})" title="Rechazar">
                                <i class="fas fa-times"></i>
                            </button>
                        `;
                    } else if (credito.estado === 'Aprobado') {
                        acciones = `
                            <button class="btn-action desembolsar" onclick="desembolsarCredito(${credito.id})" title="Desembolsar">
                                <i class="fas fa-money-bill-wave"></i>
                            </button>
                        `;
                    } else {
                        acciones = `<span style="color:rgba(255,255,255,0.2);font-size:12px;">Sin acciones</span>`;
                    }

                    return `
                    <tr>
                        <td><span style="font-weight:500;">${credito.id}</span></td>
                        <td><strong>${credito.cliente_nombre || 'N/A'}</strong></td>
                        <td>${credito.tipo_credito}</td>
                        <td style="color:#22c55e;font-weight:600;">S/ ${credito.monto_total}</td>
                        <td>S/ ${credito.cuota_mensual}</td>
                        <td>${credito.cuotas_pagadas}/${credito.cuotas_totales}</td>
                        <td>
                            <span class="badge badge-${credito.estado.toLowerCase()}">
                                ${credito.estado}
                            </span>
                        </td>
                        <td style="color:rgba(255,255,255,0.3);font-size:13px;">${credito.fecha}</td>
                        <td>${acciones}</td>
                    </tr>
                `}).join('');
            }
        } catch (error) {
            console.error('Error:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" style="text-align:center;padding:40px;color:#ff6b7a;">
                        <i class="fas fa-exclamation-circle" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                        ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    window.aprobarCredito = async function(id) {
        const result = await Swal.fire({
            title: '¿Aprobar crédito?',
            text: 'El crédito será aprobado y podrá ser desembolsado.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#22c55e',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, aprobar',
            cancelButtonText: 'Cancelar'
        });

        if (!result.isConfirmed) return;

        try {
            await fetch(`/core-creditos/${id}/aprobar`, { method: 'POST' });
            Swal.fire('¡Aprobado!', 'El crédito ha sido aprobado.', 'success');
            loadCreditos(searchInput.value);
            loadStats();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    };

    window.rechazarCredito = async function(id) {
        const result = await Swal.fire({
            title: '¿Rechazar crédito?',
            text: 'El crédito será rechazado.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, rechazar',
            cancelButtonText: 'Cancelar'
        });

        if (!result.isConfirmed) return;

        try {
            await fetch(`/core-creditos/${id}/rechazar`, { method: 'POST' });
            Swal.fire('¡Rechazado!', 'El crédito ha sido rechazado.', 'success');
            loadCreditos(searchInput.value);
            loadStats();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    };

    window.desembolsarCredito = async function(id) {
        const result = await Swal.fire({
            title: '¿Desembolsar crédito?',
            text: 'El monto será depositado en la cuenta del cliente.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#22c55e',
            cancelButtonColor: '#6b7280',
            confirmButtonText: 'Sí, desembolsar',
            cancelButtonText: 'Cancelar'
        });

        if (!result.isConfirmed) return;

        try {
            await fetch(`/core-creditos/${id}/desembolsar`, { method: 'POST' });
            Swal.fire('¡Desembolsado!', 'El crédito ha sido desembolsado.', 'success');
            loadCreditos(searchInput.value);
            loadStats();
        } catch (error) {
            Swal.fire('Error', error.message, 'error');
        }
    };

    searchInput.addEventListener('input', function() {
        loadCreditos(this.value);
    });

    refreshBtn.addEventListener('click', function() {
        loadCreditos(searchInput.value);
        loadStats();
        this.querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            this.querySelector('i').classList.remove('fa-spin');
        }, 1000);
    });

    // Cargar datos
    loadCreditos();
    loadStats();

});