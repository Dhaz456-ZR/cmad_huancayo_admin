// ======================
// CORE CREDITOS JS
// ======================

console.log("CMAC Huancayo - Core Créditos iniciado");

// ======================
// NOTIFICACIONES
// ======================

const bellBtn = document.getElementById("bellBtn");

if (bellBtn) {

    bellBtn.addEventListener("click", () => {

        alert(
            "🔔 Notificaciones\n\n" +
            "• Nuevas solicitudes pendientes.\n" +
            "• Créditos aprobados pendientes de desembolso.\n" +
            "• Sistema funcionando correctamente."
        );

    });

}

// ======================
// BUSCADOR
// ======================

const searchInput = document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener("keyup", () => {

        const filtro = searchInput.value.toLowerCase();

        const filas =
            document.querySelectorAll(
                "#tablaCreditos tbody tr"
            );

        filas.forEach(fila => {

            const texto =
                fila.innerText.toLowerCase();

            fila.style.display =
                texto.includes(filtro)
                ? ""
                : "none";

        });

    });

}

// ======================
// FILTRO POR ESTADO
// ======================

const estadoFiltro =
    document.getElementById("estadoFiltro");

if (estadoFiltro) {

    estadoFiltro.addEventListener("change", () => {

        const estadoSeleccionado =
            estadoFiltro.value.toLowerCase();

        const filas =
            document.querySelectorAll(
                "#tablaCreditos tbody tr"
            );

        filas.forEach(fila => {

            const badge =
                fila.querySelector(".badge");

            if (!badge) return;

            const estado =
                badge.textContent
                .trim()
                .toLowerCase();

            if (
                estadoSeleccionado === "" ||
                estado === estadoSeleccionado
            ) {

                fila.style.display = "";

            } else {

                fila.style.display = "none";

            }

        });

    });

}

// ======================
// CONFIRMACIONES
// ======================

document
.querySelectorAll(".btn-aprobar")
.forEach(btn => {

    btn.addEventListener("click", function(e){

        const confirmar = confirm(
            "¿Desea aprobar este crédito?"
        );

        if(!confirmar){

            e.preventDefault();

        }

    });

});

document
.querySelectorAll(".btn-rechazar")
.forEach(btn => {

    btn.addEventListener("click", function(e){

        const confirmar = confirm(
            "¿Desea rechazar este crédito?"
        );

        if(!confirmar){

            e.preventDefault();

        }

    });

});

document
.querySelectorAll(".btn-desembolsar")
.forEach(btn => {

    btn.addEventListener("click", function(e){

        const confirmar = confirm(
            "¿Desea desembolsar este crédito?"
        );

        if(!confirmar){

            e.preventDefault();

        }

    });

});

// ======================
// RESALTAR FILA
// ======================

const filas =
document.querySelectorAll(
    "#tablaCreditos tbody tr"
);

filas.forEach(fila => {

    fila.addEventListener("mouseenter", () => {

        fila.style.transition = ".2s";
        fila.style.transform = "scale(1.01)";

    });

    fila.addEventListener("mouseleave", () => {

        fila.style.transform = "scale(1)";

    });

});

// ======================
// RELOJ DEL SISTEMA
// ======================

function actualizarHora(){

    const ahora = new Date();

    const hora =
        ahora.toLocaleTimeString(
            "es-PE"
        );

    const reloj =
        document.getElementById(
            "relojSistema"
        );

    if(reloj){

        reloj.textContent = hora;

    }

}

setInterval(
    actualizarHora,
    1000
);

actualizarHora();

console.log("Core Créditos cargado correctamente");