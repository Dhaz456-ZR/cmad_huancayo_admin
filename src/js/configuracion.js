console.log("Módulo Configuración iniciado");

/* ==========================
   CAMBIAR TEMA
========================== */

const themeBtn = document.getElementById("themeBtn");

if(themeBtn){

    themeBtn.addEventListener("click", () => {

        document.body.classList.toggle("dark-mode");

        const modoOscuro =
            document.body.classList.contains("dark-mode");

        localStorage.setItem(
            "modoOscuro",
            modoOscuro
        );

        if(modoOscuro){
            themeBtn.innerHTML =
                "☀️ Tema Claro";
        }else{
            themeBtn.innerHTML =
                "🌙 Cambiar Tema";
        }

    });

}

/* ==========================
   CARGAR TEMA GUARDADO
========================== */

window.addEventListener("load", () => {

    const modoGuardado =
        localStorage.getItem("modoOscuro");

    if(modoGuardado === "true"){

        document.body.classList.add("dark-mode");

        if(themeBtn){
            themeBtn.innerHTML =
                "☀️ Tema Claro";
        }

    }

});

/* ==========================
   SINCRONIZAR POSTGRESQL
========================== */

const syncBtn = document.getElementById("syncBtn");

if(syncBtn){

    syncBtn.addEventListener("click", () => {

        alert(
            "Sincronización iniciada.\n\n" +
            "MySQL → PostgreSQL"
        );

        console.log(
            "Sincronización solicitada"
        );

    });

}

/* ==========================
   CREAR BACKUP
========================== */

const backupBtn = document.getElementById("backupBtn");

if(backupBtn){

    backupBtn.addEventListener("click", () => {

        alert(
            "Backup generado correctamente."
        );

        console.log(
            "Backup ejecutado"
        );

    });

}

/* ==========================
   ACTUALIZAR SISTEMA
========================== */

const refreshBtn =
    document.getElementById("refreshBtn");

if(refreshBtn){

    refreshBtn.addEventListener("click", () => {

        alert(
            "Sistema actualizado."
        );

        location.reload();

    });

}

/* ==========================
   ANIMACIÓN CARDS
========================== */

const cards =
    document.querySelectorAll(".card");

cards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform =
            "translateY(-8px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform =
            "translateY(0px)";

    });

});

/* ==========================
   MENSAJE DE SISTEMA
========================== */

setTimeout(() => {

    console.log(
        "CMAD Huancayo Configuración cargada correctamente."
    );

}, 1000);