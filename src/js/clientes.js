console.log("Modulo Clientes iniciado");

const searchInput = document.getElementById("searchInput");

searchInput.addEventListener("keyup", () => {

    const filtro = searchInput.value.toLowerCase();

    const filas = document.querySelectorAll(
        "#tablaClientes tbody tr"
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