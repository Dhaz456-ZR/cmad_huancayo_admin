console.log("Módulo Reportes iniciado");

/* ==========================
   ANIMACIÓN DE TARJETAS
========================== */

const cards = document.querySelectorAll(".card");

cards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-8px)";
        card.style.transition = "0.3s";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});

/* ==========================
   EFECTO TABLA
========================== */

const filas = document.querySelectorAll("tbody tr");

filas.forEach(fila => {

    fila.addEventListener("mouseenter", () => {

        fila.style.background = "#fff5f5";

    });

    fila.addEventListener("mouseleave", () => {

        fila.style.background = "";

    });

});

/* ==========================
   FECHA Y HORA ACTUAL
========================== */

function actualizarFechaHora(){

    const ahora = new Date();

    const fecha = ahora.toLocaleDateString("es-PE", {
        day: "2-digit",
        month: "long",
        year: "numeric"
    });

    const hora = ahora.toLocaleTimeString("es-PE");

    const fechaElemento = document.getElementById("fechaActual");
    const horaElemento = document.getElementById("horaActual");

    if(fechaElemento){
        fechaElemento.innerText = fecha;
    }

    if(horaElemento){
        horaElemento.innerText = hora;
    }

}

actualizarFechaHora();

setInterval(actualizarFechaHora, 1000);

/* ==========================
   MENSAJE SISTEMA
========================== */

setTimeout(() => {

    console.log(
        "Sistema de Reportes CMAC Huancayo operativo."
    );

}, 1000);

/* ==========================
   CONTADOR ANIMADO KPIs
========================== */

function animarNumero(elemento, destino){

    let actual = 0;

    const incremento = Math.ceil(destino / 50);

    const intervalo = setInterval(() => {

        actual += incremento;

        if(actual >= destino){

            actual = destino;
            clearInterval(intervalo);

        }

        elemento.innerText = actual;

    }, 20);

}

document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".card h2").forEach(card => {

        const valor = parseInt(
            card.innerText.replace(/\D/g, "")
        );

        if(!isNaN(valor)){
            animarNumero(card, valor);
        }

    });

});