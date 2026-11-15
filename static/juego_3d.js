let scene3D, camera3D, renderer3D, flashlight;
let doorsActive = false;
let animFrameId = null;

let playerPos = new THREE.Vector3(0, 1.75, 10.6);
let yaw = 0, pitch = 0;
let keys = {};
let walkTimer = 0;
let stepSoundTimer = 0;
let flashlightOn = true;
let battery = 100;
let lockpicks = 0;
let isHiding = false;
let savedPosBeforeHide = new THREE.Vector3();

let elevatorPhase = true;
let elevatorTimer = 0;
let elevatorDingPlayed = false;

let leftArmGroup, rightArmGroup;

let roomsData = [];
let highestRoomGenerated = -1;
let currentRoomIndex = 0;

let monsterMesh = null;
let monsterActive = false;
let monsterWarningTimer = 0;
let monsterZ = 0;
let monsterCooldown = 14;

function initDoors3D() {
    const container = document.getElementById("doors3DContainer");
    scene3D = new THREE.Scene();
    scene3D.background = new THREE.Color(0x050508);
    scene3D.fog = new THREE.FogExp2(0x050508, 0.020);

    camera3D = new THREE.PerspectiveCamera(72, container.clientWidth / container.clientHeight, 0.15, 110);
    scene3D.add(camera3D);

    renderer3D = new THREE.WebGLRenderer({ antialias: true });
    renderer3D.setSize(container.clientWidth, container.clientHeight);
    renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer3D.domElement);

    initMaterialesEscenario();

    const ambLight = new THREE.AmbientLight(0x4a4a5a, 0.75);
    scene3D.add(ambLight);

    flashlight = new THREE.SpotLight(0xfff5e0, 2.7, 34, Math.PI / 3.2, 0.45, 1.0);
    flashlight.position.set(0.25, -0.15, -0.2);
    flashlight.target.position.set(0, -0.15, -6);
    camera3D.add(flashlight);
    camera3D.add(flashlight.target);

    crearBrazosOrganicos();
    crearAscensorEmpotrado(scene3D);
    crearMonstruoIA();

    roomsData = [];
    rainSystems = [];
    highestRoomGenerated = -1;
    for (let i = 0; i < MAX_ACTIVE_ROOMS; i++) {
        roomsData.push(construirHabitacionEnEscena(scene3D, i));
        highestRoomGenerated = i;
    }

    playerPos.set(0, 1.75, 10.6);
    yaw = 0; pitch = 0;
    elevatorPhase = true;
    elevatorTimer = 0;
    elevatorDingPlayed = false;
    lockpicks = 0;
    battery = 100;
    isHiding = false;
    monsterActive = false;
    monsterWarningTimer = 0;
    monsterCooldown = 14;
    actualizarHUD();

    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
        document.getElementById("mobileControls").style.display = "block";
    }
}

function crearBrazosOrganicos() {
    const matManga = new THREE.MeshStandardMaterial({ color: 0x1e242d, roughness: 0.75 });
    const matPiel = new THREE.MeshStandardMaterial({ color: 0xdca98a, roughness: 0.55 });
    const matMetal = new THREE.MeshStandardMaterial({ color: 0x15181e, metalness: 0.85, roughness: 0.2 });

    function buildArm(conLinterna) {
        const armGroup = new THREE.Group();
        const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.058, 0.42, 16), matManga);
        forearm.rotation.x = Math.PI / 2.15;
        armGroup.add(forearm);

        const palm = new THREE.Mesh(new THREE.SphereGeometry(0.048, 16, 16), matPiel);
        palm.scale.set(0.95, 0.75, 1.25);
        palm.position.set(0, 0.015, -0.23);
        armGroup.add(palm);

        for (let f = -1.5; f <= 1.5; f += 1) {
            const finger = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.011, 0.075, 10), matPiel);
            finger.rotation.x = Math.PI / 2.6;
            finger.position.set(f * 0.018, 0.01, -0.29);
            armGroup.add(finger);
        }

        if (conLinterna) {
            const body = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.024, 0.22, 16), matMetal);
            body.rotation.x = Math.PI / 2.1;
            body.position.set(0, 0.032, -0.26);
            const head = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.026, 0.06, 16), matMetal);
            head.rotation.x = Math.PI / 2.1;
            head.position.set(0, 0.038, -0.38);
            armGroup.add(body, head);
        }
        return armGroup;
    }

    leftArmGroup = buildArm(false);
    leftArmGroup.position.set(-0.32, -0.29, -0.36);
    camera3D.add(leftArmGroup);

    rightArmGroup = buildArm(true);
    rightArmGroup.position.set(0.32, -0.29, -0.36);
    camera3D.add(rightArmGroup);
}

function crearMonstruoIA() {
    monsterMesh = new THREE.Group();
    const core = new THREE.Mesh(new THREE.SphereGeometry(1.25, 16, 16), new THREE.MeshBasicMaterial({ color: 0x050508 }));
    const aura = new THREE.Mesh(new THREE.SphereGeometry(1.65, 16, 16), new THREE.MeshBasicMaterial({ color: 0x1a0508, transparent: true, opacity: 0.55 }));
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff2244 });
    const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.18, 10, 10), eyeMat);
    eyeL.position.set(-0.42, 0.28, 1.1);
    const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.18, 10, 10), eyeMat);
    eyeR.position.set(0.42, 0.28, 1.1);
    const mLight = new THREE.PointLight(0xff1133, 4.0, 22);
    monsterMesh.add(core, aura, eyeL, eyeR, mLight);
    monsterMesh.visible = false;
    scene3D.add(monsterMesh);
}

function activarAtaqueMonstruo() {
    if (monsterActive || monsterWarningTimer > 0) return;
    monsterWarningTimer = 3.0;
    playAudio('monster');
}

function actualizarIAMonstruo(dt) {
    if (elevatorPhase) return;

    if (!monsterActive && monsterWarningTimer <= 0 && currentRoomIndex >= 2) {
        monsterCooldown -= dt;
        if (monsterCooldown <= 0) {
            monsterCooldown = 20 + Math.random() * 14;
            activarAtaqueMonstruo();
        }
    }

    if (monsterWarningTimer > 0) {
        monsterWarningTimer -= dt;
        const flicker = Math.random() > 0.45;
        for (const r of roomsData) {
            for (const l of r.lights) l.visible = flicker;
        }
        if (flashlightOn) flashlight.visible = flicker;

        if (monsterWarningTimer <= 0) {
            for (const r of roomsData) {
                for (const l of r.lights) l.visible = true;
            }
            if (flashlightOn) flashlight.visible = true;

            monsterActive = true;
            monsterZ = playerPos.z + (ROOM_LENGTH * 2);
            monsterMesh.position.set(0, 1.9, monsterZ);
            monsterMesh.visible = true;
        }
    }

    if (monsterActive) {
        monsterZ -= 26 * dt;
        monsterMesh.position.z = monsterZ;
        monsterMesh.position.x = Math.sin(monsterZ * 0.8) * 1.2;

        if (!isHiding && Math.abs(monsterZ - playerPos.z) < 2.2) {
            monsterActive = false;
            monsterMesh.visible = false;
            playAudio('error');
            playerPos.set(0, 1.75, 4.0);
            yaw = 0;
            actualizarHUD("Sei stato catturato. Sei tornato nella Lobby.");
            return;
        }

        if (monsterZ < playerPos.z - 45) {
            monsterActive = false;
            monsterMesh.visible = false;
        }
    }
}

function gestionarRangoProduccion() {
    const calcRoom = Math.max(0, Math.floor((-playerPos.z + ROOM_LENGTH / 2) / ROOM_LENGTH));
    if (calcRoom !== currentRoomIndex) {
        currentRoomIndex = calcRoom;
        actualizarHUD();
    }

    while (highestRoomGenerated < currentRoomIndex + MAX_ACTIVE_ROOMS) {
        const nextIdx = highestRoomGenerated + 1;
        roomsData.push(construirHabitacionEnEscena(scene3D, nextIdx));
        highestRoomGenerated = nextIdx;
    }

    while (roomsData.length > 0 && roomsData[0].index <= currentRoomIndex - MAX_ACTIVE_ROOMS) {
        const oldRoom = roomsData.shift();
        scene3D.remove(oldRoom.group);
        oldRoom.group.traverse((obj) => {
            if (obj.geometry) obj.geometry.dispose();
        });
    }
}

function checkCollision(nextPos) {
    const playerRadius = 0.42;
    const playerSphere = new THREE.Sphere(new THREE.Vector3(nextPos.x, 1.0, nextPos.z), playerRadius);

    for (const room of roomsData) {
        for (const box of room.wallBoxes) {
            if (box.intersectsSphere(playerSphere)) return true;
        }
        if (!room.doorOpen && room.doorBox.intersectsSphere(playerSphere)) {
            return true;
        }
    }
    return false;
}

function interactuar() {
    if (elevatorPhase) return;

    if (isHiding) {
        isHiding = false;
        playerPos.copy(savedPosBeforeHide);
        playAudio('creak');
        actualizarHUD("Uscito dall'armadio");
        return;
    }

    for (const room of roomsData) {
        for (const c of room.closets) {
            if (playerPos.distanceTo(c.worldPos) < 2.8) {
                isHiding = true;
                savedPosBeforeHide.copy(playerPos);
                playerPos.copy(c.hidePos);
                yaw = c.lookYaw;
                playAudio('creak');
                actualizarHUD("Nascosto nell'armadio ([E / Clic] per uscire)");
                return;
            }
        }

        const doorCenter = new THREE.Vector3(0, 1.6, room.zFrontWall);
        if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 3.0) {
            if (room.locked) {
                if (lockpicks > 0) {
                    lockpicks--;
                    room.locked = false;
                    if (room.padlockMesh) room.padlockMesh.visible = false;
                    playAudio('unlock');
                    actualizarHUD("Lucchetto aperto con grimaldello");
                } else {
                    actualizarHUD("Porta chiusa con lucchetto (Cerca un grimaldello nei cassetti)");
                    return;
                }
            }
            room.doorOpen = true;
            room.doorTargetRot = -Math.PI * 0.48;
            playAudio('creak');
            actualizarHUD(`Porta ${String(room.index + 1).padStart(4, '0')} aperta`);
            return;
        }

        for (const d of room.drawers) {
            if (playerPos.distanceTo(d.worldPos) < 2.8) {
                if (!d.open) {
                    d.open = true;
                    d.targetZ = 0.50;
                    playAudio('drawer');
                } else if (d.lootType && !d.lootTaken) {
                    d.lootTaken = true;
                    if (d.lootMesh) d.lootMesh.visible = false;
                    playAudio('pickup');
                    if (d.lootType === 'lockpick') {
                        lockpicks++;
                        actualizarHUD("Hai raccolto un Grimaldello!");
                    } else if (d.lootType === 'battery') {
                        battery = Math.min(100, battery + 45);
                        actualizarHUD("Batteria torcia ricaricata (+45%)!");
                    }
                } else {
                    d.open = false;
                    d.targetZ = 0.04;
                    playAudio('drawer');
                }
                return;
            }
        }
    }
}

function actualizarHUD(statusMsg) {
    document.getElementById("hudRoom").innerText = `STANZA: ${String(currentRoomIndex).padStart(4, '0')}`;
    document.getElementById("slotBatText").innerText = `${Math.ceil(battery)}%`;
    document.getElementById("slotKeyCount").innerText = `x${lockpicks}`;

    const slotFlash = document.getElementById("slotFlashlight");
    if (flashlightOn) slotFlash.classList.add("active");
    else slotFlash.classList.remove("active");

    if (statusMsg) {
        document.getElementById("hudStatus").innerText = statusMsg;
    }
}

function updateDoors3D(dt) {
    for (const sys of rainSystems) {
        for (const drop of sys.drops) {
            drop.position.y -= 5.2 * dt;
            if (drop.position.y < -sys.halfH) drop.position.y = sys.halfH;
        }
    }

    if (elevatorPhase) {
        elevatorTimer += dt;
        if (elevatorTimer < 0.9) actualizarDisplayAscensor("▲ B2");
        else if (elevatorTimer < 1.8) actualizarDisplayAscensor("▲ B1");
        else actualizarDisplayAscensor("LOBBY");

        camera3D.position.set(
            playerPos.x + (Math.random() - 0.5) * 0.018,
            playerPos.y + (Math.random() - 0.5) * 0.018,
            playerPos.z
        );

        if (elevatorTimer > 2.0) {
            if (!elevatorDingPlayed) {
                elevatorDingPlayed = true;
                playAudio('ding');
            }
            if (elevatorDoorLeft.position.x > -2.1) {
                elevatorDoorLeft.position.x -= 1.3 * dt;
                elevatorDoorRight.position.x += 1.3 * dt;
            } else {
                elevatorPhase = false;
                actualizarHUD("Benvenuto nella Lobby");
            }
        }
        return;
    }

    if (flashlightOn && battery > 0) {
        battery = Math.max(0, battery - 0.35 * dt);
        flashlight.intensity = 1.2 + (battery / 100) * 1.6;
        document.getElementById("slotBatText").innerText = `${Math.ceil(battery)}%`;
        if (battery === 0) {
            flashlightOn = false;
            flashlight.visible = false;
            actualizarHUD();
        }
    }

    let isMoving = false;
    if (!isHiding) {
        const speed = 5.2 * dt;
        const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
        const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
        let moveVec = new THREE.Vector3();

        if (keys['KeyW'] || keys['ArrowUp']) moveVec.add(forward);
        if (keys['KeyS'] || keys['ArrowDown']) moveVec.sub(forward);
        if (keys['KeyD'] || keys['ArrowRight']) moveVec.add(right);
        if (keys['KeyA'] || keys['ArrowLeft']) moveVec.sub(right);

        isMoving = moveVec.lengthSq() > 0;
        if (isMoving) {
            moveVec.normalize().multiplyScalar(speed);
            const tryX = playerPos.clone().add(new THREE.Vector3(moveVec.x, 0, 0));
            if (!checkCollision(tryX)) playerPos.x = tryX.x;

            const tryZ = playerPos.clone().add(new THREE.Vector3(0, 0, moveVec.z));
            if (!checkCollision(tryZ)) playerPos.z = tryZ.z;

            walkTimer += dt * 9;
            stepSoundTimer += dt;
            if (stepSoundTimer > 0.44) {
                stepSoundTimer = 0;
                playAudio('step');
            }
        } else {
            walkTimer = 0;
        }
    }

    const bobY = isMoving ? Math.sin(walkTimer * 2) * 0.045 : 0;
    camera3D.position.set(playerPos.x, playerPos.y + bobY, playerPos.z);
    camera3D.rotation.order = 'YXZ';
    camera3D.rotation.y = yaw;
    camera3D.rotation.x = pitch;

    if (leftArmGroup && rightArmGroup) {
        leftArmGroup.visible = !isHiding;
        rightArmGroup.visible = !isHiding;
        leftArmGroup.position.y = -0.29 + (isMoving ? Math.sin(walkTimer) * 0.022 : 0);
        rightArmGroup.position.y = -0.29 + (isMoving ? -Math.sin(walkTimer) * 0.022 : 0);
    }

    let promptVisible = false;
    const promptEl = document.getElementById("promptText");

    if (isHiding) {
        promptVisible = true;
        promptEl.innerText = "[E / Clic] Esci dall'armadio";
    } else {
        for (const room of roomsData) {
            if (Math.abs(room.doorPivot.rotation.y - room.doorTargetRot) > 0.005) {
                room.doorPivot.rotation.y += (room.doorTargetRot - room.doorPivot.rotation.y) * 6 * dt;
            }

            const doorCenter = new THREE.Vector3(0, 1.6, room.zFrontWall);
            if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 3.0) {
                promptVisible = true;
                promptEl.innerText = room.locked
                    ? `[E / Clic] Apri Lucchetto Porta ${String(room.index + 1).padStart(4, '0')} (Serve 1 Grimaldello)`
                    : `[E / Clic] Apri Porta ${String(room.index + 1).padStart(4, '0')}`;
            }

            for (const d of room.drawers) {
                d.group.position.z += (d.targetZ - d.group.position.z) * 10 * dt;

                if (playerPos.distanceTo(d.worldPos) < 2.8) {
                    promptVisible = true;
                    if (!d.open) {
                        promptEl.innerText = "[E / Clic] Apri cassetto";
                    } else if (d.lootType && !d.lootTaken) {
                        promptEl.innerText = d.lootType === 'lockpick'
                            ? "[E / Clic] Prendi Grimaldello 🔑"
                            : "[E / Clic] Usa Batteria 🔋";
                    } else {
                        promptEl.innerText = "[E / Clic] Chiudi cassetto";
                    }
                }
            }

            for (const c of room.closets) {
                if (playerPos.distanceTo(c.worldPos) < 2.8) {
                    promptVisible = true;
                    promptEl.innerText = "[E / Clic] Nasconditi nell'armadio";
                }
            }
        }
    }

    promptEl.style.display = promptVisible ? "block" : "none";
    actualizarIAMonstruo(dt);
    gestionarRangoProduccion();
}

let lastTime = performance.now();
function bucleDoors3D(now) {
    if (!doorsActive) return;
    const dt = Math.min((now - lastTime) / 1000, 0.05);
    lastTime = now;

    updateDoors3D(dt);
    renderer3D.render(scene3D, camera3D);
    animFrameId = requestAnimationFrame(bucleDoors3D);
}

function abrirJuego() {
    const modal = document.getElementById("gameModal");
    modal.style.display = "flex";
    document.getElementById("startOverlay3D").style.display = "flex";

    if (!renderer3D) initDoors3D();
    doorsActive = true;
    lastTime = performance.now();
    bucleDoors3D(lastTime);
    musicaHotelReal.currentTime = 0;
    musicaHotelReal.play().catch(() => {});
}

function cerrarJuego() {
    doorsActive = false;
    if (animFrameId) cancelAnimationFrame(animFrameId);
    musicaHotelReal.pause();
    if (document.pointerLockElement) document.exitPointerLock();
    document.getElementById("gameModal").style.display = "none";
}

function iniciarControl3D() {
    document.getElementById("startOverlay3D").style.display = "none";
    const container = document.getElementById("doors3DContainer");
    if (container.requestPointerLock) container.requestPointerLock();
    musicaHotelReal.play().catch(() => {});
}

function toggleFullscreen() {
    const box = document.getElementById("gameModalBox");
    if (!document.fullscreenElement) box.requestFullscreen().catch(() => {});
    else document.exitFullscreen().catch(() => {});
}

window.addEventListener("keydown", (e) => {
    keys[e.code] = true;
    if (!doorsActive) return;
    if (e.code === "KeyF" && battery > 0) {
        flashlightOn = !flashlightOn;
        flashlight.visible = flashlightOn;
        actualizarHUD();
    }
    if (e.code === "KeyE") interactuar();
    if (e.key === "F11") { e.preventDefault(); toggleFullscreen(); }
});

window.addEventListener("keyup", (e) => { keys[e.code] = false; });

window.addEventListener("mousemove", (e) => {
    if (!doorsActive) return;
    if (document.pointerLockElement === document.getElementById("doors3DContainer")) {
        yaw -= e.movementX * 0.0022;
        pitch -= e.movementY * 0.0022;
        pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
    }
});

document.getElementById("doors3DContainer").addEventListener("mousedown", () => {
    if (!doorsActive) return;
    if (document.getElementById("startOverlay3D").style.display !== "none") return;
    if (document.pointerLockElement !== document.getElementById("doors3DContainer") && !('ontouchstart' in window)) {
        document.getElementById("doors3DContainer").requestPointerLock();
    } else {
        interactuar();
    }
});

let lastTouchX = 0, lastTouchY = 0;
const container3D = document.getElementById("doors3DContainer");
container3D.addEventListener("touchstart", (e) => { lastTouchX = e.touches[0].clientX; lastTouchY = e.touches[0].clientY; }, { passive: true });
container3D.addEventListener("touchmove", (e) => {
    const dx = e.touches[0].clientX - lastTouchX;
    const dy = e.touches[0].clientY - lastTouchY;
    lastTouchX = e.touches[0].clientX;
    lastTouchY = e.touches[0].clientY;
    yaw -= dx * 0.005;
    pitch -= dy * 0.005;
    pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
}, { passive: true });

function bindTouchBtn(id, keyCode) {
    const btn = document.getElementById(id);
    btn.addEventListener("touchstart", (e) => { e.preventDefault(); keys[keyCode] = true; });
    btn.addEventListener("touchend", (e) => { e.preventDefault(); keys[keyCode] = false; });
}
bindTouchBtn("btnUp", "KeyW");
bindTouchBtn("btnDown", "KeyS");
bindTouchBtn("btnLeft", "KeyA");
bindTouchBtn("btnRight", "KeyD");

document.getElementById("btnFlash").addEventListener("touchstart", (e) => {
    e.preventDefault();
    if (battery > 0) { flashlightOn = !flashlightOn; flashlight.visible = flashlightOn; actualizarHUD(); }
});
document.getElementById("btnInteract").addEventListener("touchstart", (e) => { e.preventDefault(); interactuar(); });

window.addEventListener("resize", () => {
    if (!renderer3D || !camera3D) return;
    const c = document.getElementById("doors3DContainer");
    camera3D.aspect = c.clientWidth / c.clientHeight;
    camera3D.updateProjectionMatrix();
    renderer3D.setSize(c.clientWidth, c.clientHeight);
});
