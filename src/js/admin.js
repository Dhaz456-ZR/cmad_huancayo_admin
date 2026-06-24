const data = document.getElementById("dashboard-data");

const totalClientes = parseInt(data.dataset.clientes || 0);
const totalCreditos = parseInt(data.dataset.creditos || 0);

const vigente = parseFloat(data.dataset.vigente || 0);
const vencida = parseFloat(data.dataset.vencida || 0);

const normal = parseInt(data.dataset.normal || 0);
const cpp = parseInt(data.dataset.cpp || 0);
const deficiente = parseInt(data.dataset.deficiente || 0);
const dudoso = parseInt(data.dataset.dudoso || 0);
const perdida = parseInt(data.dataset.perdida || 0);



// ==========================
// CAMPANITA
// ==========================

const bellBtn = document.getElementById("bellBtn");

if (bellBtn) {

    bellBtn.addEventListener("click", () => {

        alert(
            "No tienes nuevas notificaciones."
        );

    });

}

// ==========================
// CUMPLIMIENTO DE META
// ==========================

const metaCanvas =
document.getElementById("metaChart");

if (metaCanvas) {

    const metaCumplida = vigente || 0;
    const metaPendiente = vencida || 0;

    new Chart(metaCanvas, {

        type: "doughnut",

        data: {

            labels: [
                "Cumplido",
                "Pendiente"
            ],

            datasets: [

                {

                    data: [
                        metaCumplida,
                        metaPendiente
                    ],

                    backgroundColor: [
                        "#b40000",
                        "#e5e7eb"
                    ],

                    borderWidth: 0

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    position: "bottom"
                }

            }

        }

    });

}


// ==========================
// CARTERA POR CALIFICACION
// ==========================

const calificacionCanvas =
document.getElementById(
    "calificacionChart"
);

if (calificacionCanvas) {

    new Chart(calificacionCanvas, {

        type: "bar",

        data: {

            labels: [
                "Normal",
                "CPP",
                "Deficiente",
                "Dudoso",
                "Pérdida"
            ],

            datasets: [

                {

                    label: "Clientes",

                    data: [

                        normal || 0,
                        cpp || 0,
                        deficiente || 0,
                        dudoso || 0,
                        perdida || 0

                    ],

                    backgroundColor: [

                        "#b40000",
                        "#d62828",
                        "#ef4444",
                        "#f87171",
                        "#fca5a5"

                    ],

                    borderRadius: 10

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: false
                }

            },

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

}


// ==========================
// CARTERA VENCIDA PRODUCTOS
// ==========================

const productoCanvas =
document.getElementById(
    "productoChart"
);

if (productoCanvas) {

    new Chart(productoCanvas, {

        type: "pie",

        data: {

            labels: [

                "Personal",
                "Hipotecario",
                "Vehicular",
                "Empresarial"

            ],

            datasets: [

                {

                    data: [

                        15,
                        25,
                        10,
                        8

                    ],

                    backgroundColor: [

                        "#b40000",
                        "#dc2626",
                        "#ef4444",
                        "#f87171"

                    ]

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom"

                }

            }

        }

    });

}


// ==========================
// EFECTO TARJETAS
// ==========================

const cards =
document.querySelectorAll(".card");

cards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform =
        "translateY(-6px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform =
        "translateY(0px)";

    });

});

