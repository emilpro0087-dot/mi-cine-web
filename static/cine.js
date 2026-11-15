let claveServidor = "";

window.addEventListener("DOMContentLoaded", () => {
    const bar = document.getElementById("progressBar");
    const label = document.getElementById("statusLabel");
    const loader = document.getElementById("loaderOverlay");
    const login = document.getElementById("loginScreen");

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 7) + 3;
        if (progress > 100) progress = 100;

        bar.style.width = progress + "%";
        label.innerText = `Sincronizzazione in corso... (${progress}%)`;

        if (progress === 100) {
            clearInterval(interval);
            setTimeout(() => {
                loader.style.opacity = "0";
                setTimeout(() => {
                    loader.style.visibility = "hidden";
                    login.style.visibility = "visible";
                    login.style.opacity = "1";
                    document.getElementById("passInput").focus();
                }, 500);
            }, 400);
        }
    }, 60);
});

function validarAcceso(claveEsperada) {
    if (claveEsperada) claveServidor = claveEsperada;
    const input = document.getElementById("passInput");
    const error = document.getElementById("errorLabel");
    const loginScreen = document.getElementById("loginScreen");

    if (input.value === claveServidor) {
        error.innerText = "";
        playAudio('success');
        loginScreen.classList.add("screen-shake");
        setTimeout(() => {
            loginScreen.classList.remove("screen-shake");
            loginScreen.classList.add("slide-down-exit");
        }, 460);
    } else {
        playAudio('error');
        error.innerText = "Password errata. Accesso non autorizzato.";
        input.value = "";
        const card = document.getElementById("loginCard");
        card.style.transform = "translateX(-8px)";
        setTimeout(() => { card.style.transform = "translateX(8px)"; }, 80);
        setTimeout(() => { card.style.transform = "translateX(-4px)"; }, 160);
        setTimeout(() => { card.style.transform = "translateX(0)"; }, 240);
    }
}

document.getElementById("passInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        document.querySelector(".btn-submit").click();
    }
});

function toggleSubtitles(activar) {
    const player = document.getElementById("player");
    if (player.textTracks && player.textTracks.length > 0) {
        for (let i = 0; i < player.textTracks.length; i++) {
            player.textTracks[i].mode = activar ? "showing" : "disabled";
        }
    }
}

function reproducir(peliculaId) {
    const modal = document.getElementById("videoModal");
    const player = document.getElementById("player");

    modal.style.display = "flex";
    player.innerHTML = "";
    player.src = `/stream-video/${peliculaId}`;

    // Conectar pista real de subtítulos .vtt desde el servidor
    const trackEl = document.createElement("track");
    trackEl.kind = "subtitles";
    trackEl.label = "Italiano (Solo Voce)";
    trackEl.srclang = "it";
    trackEl.src = `/subtitulos/${peliculaId}.vtt`;
    trackEl.default = true;
    player.appendChild(trackEl);

    trackEl.addEventListener("load", () => {
        if (trackEl.track && trackEl.track.cues) {
            for (let i = 0; i < trackEl.track.cues.length; i++) {
                let txt = trackEl.track.cues[i].text;
                txt = txt.replace(/[♪♫#♬♩]/g, "").replace(/\[.*?\]/g, "").replace(/\(.*?\)/g, "").trim();
                trackEl.track.cues[i].text = txt;
            }
        }
        toggleSubtitles(document.getElementById("toggleAutoSub").checked);
    });

    player.play().catch(() => {});
}

function cerrarVideo() {
    const modal = document.getElementById("videoModal");
    const player = document.getElementById("player");

    modal.style.display = "none";
    player.pause();
    player.innerHTML = "";
    player.removeAttribute("src");
    player.load();
}
