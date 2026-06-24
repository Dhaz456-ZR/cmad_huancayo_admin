console.log("Módulo Operaciones iniciado");

/* =========================
   BUSCADOR DE OPERACIONES
========================= */

const searchInput = document.getElementById("searchInput");

if(searchInput){

    searchInput.addEventListener("keyup", () => {

        const filtro = searchInput.value.toLowerCase();

        const filas = document.querySelectorAll(
            "#tablaOperaciones tbody tr"
        );

        filas.forEach(fila => {

            const texto = fila.innerText.toLowerCase();

            if(texto.includes(filtro)){
                fila.style.display = "";
            }else{
                fila.style.display = "none";
            }

        });

    });

}

/* =========================
   ANIMACION KPI
========================= */

const tarjetas = document.querySelectorAll(".card");

tarjetas.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-5px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});