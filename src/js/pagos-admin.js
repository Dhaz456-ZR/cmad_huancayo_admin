document.addEventListener('DOMContentLoaded', function() {

    const tableBody = document.getElementById('tableBody');
    const totalPagosEl = document.getElementById('totalPagos');
    const montoTotalEl = document.getElementById('montoTotal');

    async function loadPagos() {
        try {
            const response = await fetch('/api/pagos');
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Error al cargar pagos');
            }

            const pagos = result.data;

            totalPagosEl.textContent = pagos.length;
            
            let montoTotal = 0;
            pagos.forEach(p => montoTotal += parseFloat(p.monto));
            montoTotalEl.textContent = `S/ ${montoTotal.toFixed(2)}`;

            if (pagos.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align:center;padding:40px;color:rgba(255,255,255,0.2);">
                            <i class="fas fa-inbox" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                            No hay pagos registrados
                        </td>
                    </tr>
                `;
            } else {
                tableBody.innerHTML = pagos.map(p => `
                    <tr>
                        <td><span style="font-weight:500;">${p.id}</span></td>
                        <td><strong>${p.cliente_nombre || 'N/A'}</strong></td>
                        <td>${p.servicio}</td>
                        <td>${p.codigo_cliente}</td>
                        <td style="color:#f87171;font-weight:600;">S/ ${p.monto}</td>
                        <td style="color:rgba(255,255,255,0.3);font-size:13px;">${p.fecha}</td>
                    </tr>
                `).join('');
            }
        } catch (error) {
            console.error('Error:', error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center;padding:40px;color:#ff6b7a;">
                        <i class="fas fa-exclamation-circle" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                        ${error.message}
                    </td>
                </tr>
            `;
        }
    }

    loadPagos();

});