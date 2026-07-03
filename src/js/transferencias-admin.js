document.addEventListener('DOMContentLoaded', function() {

    const tableBody = document.getElementById('tableBody');
    const totalTransferenciasEl = document.getElementById('totalTransferencias');
    const montoTotalEl = document.getElementById('montoTotal');

    async function loadTransferencias() {
        try {
            const response = await fetch('/api/transferencias');
            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Error al cargar transferencias');
            }

            const transferencias = result.data;

            totalTransferenciasEl.textContent = transferencias.length;
            
            let montoTotal = 0;
            transferencias.forEach(t => montoTotal += parseFloat(t.monto));
            montoTotalEl.textContent = `S/ ${montoTotal.toFixed(2)}`;

            if (transferencias.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="7" style="text-align:center;padding:40px;color:rgba(255,255,255,0.2);">
                            <i class="fas fa-inbox" style="font-size:24px;display:block;margin-bottom:12px;"></i>
                            No hay transferencias registradas
                        </td>
                    </tr>
                `;
            } else {
                tableBody.innerHTML = transferencias.map(t => `
                    <tr>
                        <td><span style="font-weight:500;">${t.id}</span></td>
                        <td><strong>${t.cliente_nombre || 'N/A'}</strong></td>
                        <td>${t.cuenta_destino}</td>
                        <td>${t.destinatario}</td>
                        <td style="color:#f87171;font-weight:600;">S/ ${t.monto}</td>
                        <td style="color:rgba(255,255,255,0.5);">${t.motivo || '-'}</td>
                        <td style="color:rgba(255,255,255,0.3);font-size:13px;">${t.fecha}</td>
                    </tr>
                `).join('');
            }
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

    loadTransferencias();

});