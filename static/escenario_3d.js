const ROOM_LENGTH = 18;
const ROOM_WIDTH = 14;
const ROOM_HEIGHT = 9.2;
const DOOR_WIDTH = 2.2;
const DOOR_HEIGHT = 3.4;
const MAX_ACTIVE_ROOMS = 5;

let matMadera, matAlfombra, matPared, matHierroViejo, matOro;
let elevatorGroup = null;
let elevatorDoorLeft = null;
let elevatorDoorRight = null;
let elevatorFloorCanvas = null;
let elevatorFloorTex = null;
let lastFloorText = "";
let rainSystems = [];

function crearTexturaMadera() {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 256;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#472212';
    ctx.fillRect(0, 0, 256, 256);
    for (let y = 0; y < 256; y += 3) {
        ctx.strokeStyle = y % 9 === 0 ? 'rgba(15, 5, 1, 0.7)' : 'rgba(28, 10, 3, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.bezierCurveTo(85, y + Math.sin(y * 0.1) * 8, 170, y - Math.sin(y * 0.1) * 8, 256, y);
        ctx.stroke();
    }
    ctx.fillStyle = 'rgba(10, 3, 0, 0.85)';
    for (let x = 0; x < 256; x += 64) ctx.fillRect(x, 0, 2, 256);
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    return tex;
}

function crearTexturaAlfombra() {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 256;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#4a1219';
    ctx.fillRect(0, 0, 256, 256);
    ctx.fillStyle = 'rgba(25, 5, 8, 0.35)';
    for (let i = 0; i < 256; i += 8) {
        ctx.fillRect(i, 0, 2, 256);
        ctx.fillRect(0, i, 256, 2);
    }
    ctx.strokeStyle = 'rgba(212, 175, 55, 0.32)';
    ctx.lineWidth = 4;
    ctx.strokeRect(10, 10, 236, 236);
    const tex = new THREE.CanvasTexture(c);
    tex.wrapS = THREE.RepeatWrapping;
    tex.wrapT = THREE.RepeatWrapping;
    tex.repeat.set(4, 5);
    tex.anisotropy = 8;
    return tex;
}

function crearCartelMaderaDoors(numero) {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 96;
    const ctx = c.getContext('2d');
    ctx.fillStyle = '#2d160b';
    ctx.fillRect(0, 0, 256, 96);
    for (let y = 0; y < 96; y += 3) {
        ctx.strokeStyle = 'rgba(15, 6, 2, 0.45)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(256, y + Math.sin(y * 0.2) * 3);
        ctx.stroke();
    }
    ctx.strokeStyle = '#7c5332';
    ctx.lineWidth = 8;
    ctx.strokeRect(4, 4, 248, 88);
    ctx.strokeStyle = '#180a04';
    ctx.lineWidth = 2;
    ctx.strokeRect(10, 10, 236, 76);

    ctx.fillStyle = '#efe6d5';
    ctx.shadowColor = '#000000';
    ctx.shadowBlur = 4;
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;
    ctx.font = 'bold 46px Georgia, serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(numero).padStart(4, '0'), 128, 50);
    return new THREE.CanvasTexture(c);
}

function crearTexturaCuadro(tipo) {
    const c = document.createElement('canvas');
    c.width = 256; c.height = 320;
    const ctx = c.getContext('2d');
    if (tipo === 0) {
        const grad = ctx.createLinearGradient(0, 0, 0, 320);
        grad.addColorStop(0, '#0a1428');
        grad.addColorStop(1, '#1e2d42');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 256, 320);
        ctx.fillStyle = '#e8eef5';
        ctx.beginPath();
        ctx.arc(185, 70, 26, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#090d14';
        ctx.beginPath();
        ctx.moveTo(0, 250);
        ctx.lineTo(90, 140);
        ctx.lineTo(170, 220);
        ctx.lineTo(256, 150);
        ctx.lineTo(256, 320);
        ctx.lineTo(0, 320);
        ctx.fill();
    } else {
        ctx.fillStyle = '#24140e';
        ctx.fillRect(0, 0, 256, 320);
        ctx.fillStyle = '#111116';
        ctx.beginPath();
        ctx.ellipse(128, 255, 65, 85, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#c8a688';
        ctx.beginPath();
        ctx.ellipse(128, 135, 34, 44, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#181412';
        ctx.fillRect(92, 85, 72, 22);
    }
    return new THREE.CanvasTexture(c);
}

function initMaterialesEscenario() {
    const texMadera = crearTexturaMadera();
    const texAlfombra = crearTexturaAlfombra();
    matMadera = new THREE.MeshStandardMaterial({ map: texMadera, bumpMap: texMadera, bumpScale: 0.03, roughness: 0.6 });
    matAlfombra = new THREE.MeshStandardMaterial({
        map: texAlfombra,
        roughness: 0.9,
        polygonOffset: true,
        polygonOffsetFactor: -1
    });
    matPared = new THREE.MeshStandardMaterial({ color: 0x332924, roughness: 0.85 });
    matHierroViejo = new THREE.MeshStandardMaterial({ color: 0x2c2825, metalness: 0.8, roughness: 0.65 });
    matOro = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.85, roughness: 0.25 });
}

function actualizarDisplayAscensor(texto) {
    if (!elevatorFloorCanvas || lastFloorText === texto) return;
    lastFloorText = texto;
    const ctx = elevatorFloorCanvas.getContext('2d');
    ctx.fillStyle = '#090d14';
    ctx.fillRect(0, 0, 256, 80);
    ctx.strokeStyle = '#d4af37';
    ctx.lineWidth = 4;
    ctx.strokeRect(4, 4, 248, 72);
    ctx.fillStyle = '#ffaa22';
    ctx.font = 'bold 34px monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(texto, 128, 42);
    if (elevatorFloorTex) elevatorFloorTex.needsUpdate = true;
}

function crearAscensorEmpotrado(scene) {
    elevatorGroup = new THREE.Group();
    const matCabinaMadera = new THREE.MeshStandardMaterial({ map: crearTexturaMadera(), roughness: 0.5 });
    const matRejaMetal = new THREE.MeshStandardMaterial({ color: 0x2b3038, metalness: 0.85, roughness: 0.3 });

    const wallThick = 0.55;
    const cabW = 3.2, cabH = 3.8, cabD = 3.2, cabZ = 10.6;

    const cabFloor = new THREE.Mesh(new THREE.BoxGeometry(cabW + wallThick * 2, 0.3, cabD + wallThick), matAlfombra);
    cabFloor.position.set(0, -0.14, cabZ);
    const cabCeil = new THREE.Mesh(new THREE.BoxGeometry(cabW + wallThick * 2, 0.4, cabD + wallThick), matCabinaMadera);
    cabCeil.position.set(0, cabH + 0.2, cabZ);

    const cabLeft = new THREE.Mesh(new THREE.BoxGeometry(wallThick, cabH, cabD + wallThick), matCabinaMadera);
    cabLeft.position.set(-(cabW / 2 + wallThick / 2), cabH / 2, cabZ);
    const cabRight = new THREE.Mesh(new THREE.BoxGeometry(wallThick, cabH, cabD + wallThick), matCabinaMadera);
    cabRight.position.set(cabW / 2 + wallThick / 2, cabH / 2, cabZ);
    const cabBack = new THREE.Mesh(new THREE.BoxGeometry(cabW + wallThick * 2, cabH, wallThick), matCabinaMadera);
    cabBack.position.set(0, cabH / 2, cabZ + cabD / 2 + wallThick / 2);

    elevatorGroup.add(cabFloor, cabCeil, cabLeft, cabRight, cabBack);

    const railBack = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 3.0, 12), matOro);
    railBack.rotation.z = Math.PI / 2;
    railBack.position.set(0, 1.05, cabZ + cabD / 2 - 0.08);
    const railLeft = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.8, 12), matOro);
    railLeft.rotation.x = Math.PI / 2;
    railLeft.position.set(-cabW / 2 + 0.08, 1.05, cabZ);
    elevatorGroup.add(railBack, railLeft);

    // Panel de botones de pisos
    const panelGroup = new THREE.Group();
    panelGroup.position.set(cabW / 2 - 0.03, 1.45, cabZ - 0.55);
    panelGroup.rotation.y = -Math.PI / 2;
    panelGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.78, 0.04), matOro));

    [
        { label: "LOBBY", color: 0x00ff88, y: 0.24 },
        { label: "B1",    color: 0xffaa00, y: 0.08 },
        { label: "B2",    color: 0xffaa00, y: -0.08 },
        { label: "BELL",  color: 0xff3344, y: -0.24 }
    ].forEach((p) => {
        const btn = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.036, 0.03, 14), new THREE.MeshBasicMaterial({ color: p.color }));
        btn.rotation.x = Math.PI / 2;
        btn.position.set(-0.07, p.y, 0.025);
        panelGroup.add(btn);

        const cBtn = document.createElement('canvas');
        cBtn.width = 96; cBtn.height = 40;
        const ctxB = cBtn.getContext('2d');
        ctxB.fillStyle = '#1a1208';
        ctxB.fillRect(0, 0, 96, 40);
        ctxB.fillStyle = '#fff';
        ctxB.font = 'bold 22px monospace';
        ctxB.textAlign = 'center';
        ctxB.textBaseline = 'middle';
        ctxB.fillText(p.label, 48, 20);
        const lblMesh = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.065), new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(cBtn) }));
        lblMesh.position.set(0.06, p.y, 0.023);
        panelGroup.add(lblMesh);
    });
    elevatorGroup.add(panelGroup);

    const plafon = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 1.4), new THREE.MeshBasicMaterial({ color: 0xffe8b5 }));
    plafon.position.set(0, cabH - 0.02, cabZ);
    elevatorGroup.add(plafon);

    elevatorFloorCanvas = document.createElement('canvas');
    elevatorFloorCanvas.width = 256;
    elevatorFloorCanvas.height = 80;
    elevatorFloorTex = new THREE.CanvasTexture(elevatorFloorCanvas);
    actualizarDisplayAscensor("▲ B2");

    const displayMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.2, 0.36), new THREE.MeshBasicMaterial({ map: elevatorFloorTex }));
    displayMesh.position.set(0, 3.55, 8.78);
    elevatorGroup.add(displayMesh);

    function crearHojaReja() {
        const hoja = new THREE.Group();
        hoja.add(new THREE.Mesh(new THREE.BoxGeometry(1.58, 3.3, 0.08), matRejaMetal));
        for (let bx = -0.6; bx <= 0.6; bx += 0.24) {
            const barrote = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 3.1, 8), matOro);
            barrote.position.set(bx, 0, 0.045);
            hoja.add(barrote);
        }
        return hoja;
    }

    elevatorDoorLeft = crearHojaReja();
    elevatorDoorLeft.position.set(-0.79, 1.65, 9.0);
    elevatorDoorRight = crearHojaReja();
    elevatorDoorRight.position.set(0.79, 1.65, 9.0);
    elevatorGroup.add(elevatorDoorLeft, elevatorDoorRight);

    const luzAscensor = new THREE.PointLight(0xffc978, 2.0, 9);
    luzAscensor.position.set(0, 3.4, cabZ);
    elevatorGroup.add(luzAscensor);

    scene.add(elevatorGroup);
}

function crearCandelabroClasico(x, yTecho, z, lit) {
    const chandGroup = new THREE.Group();
    chandGroup.position.set(x, yTecho, z);

    const chain = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 2.2, 8), matHierroViejo);
    chain.position.y = -1.1;
    chandGroup.add(chain);

    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.95, 0.055, 10, 24), matOro);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = -2.2;
    chandGroup.add(ring);

    const matVela = new THREE.MeshBasicMaterial({ color: lit ? 0xfff0c2 : 0x333333 });
    for (let i = 0; i < 6; i++) {
        const ang = (i / 6) * Math.PI * 2;
        const candle = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.24, 8), matVela);
        candle.position.set(Math.cos(ang) * 0.95, -2.06, Math.sin(ang) * 0.95);
        chandGroup.add(candle);
    }

    let pointLight = null;
    if (lit) {
        pointLight = new THREE.PointLight(0xffdfa8, 2.2, 28);
        pointLight.position.set(0, -2.4, 0);
        chandGroup.add(pointLight);
    }
    return { group: chandGroup, light: pointLight };
}

function crearCandadoViejo() {
    const lockGroup = new THREE.Group();
    lockGroup.add(new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.28, 0.09), matHierroViejo));
    const shackle = new THREE.Mesh(new THREE.TorusGeometry(0.085, 0.022, 8, 16, Math.PI), matHierroViejo);
    shackle.position.set(0, 0.14, 0);
    lockGroup.add(shackle);
    const keyhole = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.08, 0.1), new THREE.MeshBasicMaterial({ color: 0x050505 }));
    keyhole.position.set(0, -0.02, 0.01);
    lockGroup.add(keyhole);
    return lockGroup;
}

function crearVentanaLargaNocheLluvia(x, y, z, rotY) {
    const winGroup = new THREE.Group();
    winGroup.position.set(x, y, z);
    winGroup.rotation.y = rotY;

    const winW = 2.4, winH = 5.6;
    const sky = new THREE.Mesh(new THREE.PlaneGeometry(winW, winH), new THREE.MeshBasicMaterial({ color: 0x060c1a }));
    sky.position.z = -0.05;
    winGroup.add(sky);

    const moon = new THREE.Mesh(new THREE.CircleGeometry(0.42, 24), new THREE.MeshBasicMaterial({ color: 0xf4f7ff }));
    moon.position.set(0.45, 1.75, -0.04);
    winGroup.add(moon);

    const topBar = new THREE.Mesh(new THREE.BoxGeometry(winW + 0.24, 0.22, 0.16), matMadera);
    topBar.position.y = winH / 2;
    const botBar = new THREE.Mesh(new THREE.BoxGeometry(winW + 0.24, 0.26, 0.20), matMadera);
    botBar.position.y = -winH / 2;
    const leftBar = new THREE.Mesh(new THREE.BoxGeometry(0.20, winH + 0.2, 0.16), matMadera);
    leftBar.position.x = -winW / 2;
    const rightBar = new THREE.Mesh(new THREE.BoxGeometry(0.20, winH + 0.2, 0.16), matMadera);
    rightBar.position.x = winW / 2;
    const midV = new THREE.Mesh(new THREE.BoxGeometry(0.09, winH, 0.10), matMadera);
    const midH1 = new THREE.Mesh(new THREE.BoxGeometry(winW, 0.09, 0.10), matMadera);
    midH1.position.y = winH * 0.18;
    const midH2 = new THREE.Mesh(new THREE.BoxGeometry(winW, 0.09, 0.10), matMadera);
    midH2.position.y = -winH * 0.18;
    winGroup.add(topBar, botBar, leftBar, rightBar, midV, midH1, midH2);

    const rainDrops = [];
    const matGota = new THREE.MeshBasicMaterial({ color: 0x7aa4d4, transparent: true, opacity: 0.65 });
    for (let r = 0; r < 40; r++) {
        const drop = new THREE.Mesh(new THREE.BoxGeometry(0.016, 0.28, 0.01), matGota);
        drop.position.set((Math.random() - 0.5) * (winW - 0.2), (Math.random() - 0.5) * (winH - 0.3), -0.02);
        winGroup.add(drop);
        rainDrops.push(drop);
    }
    rainSystems.push({ drops: rainDrops, halfH: winH / 2 - 0.15 });
    return winGroup;
}

function decorarVestibulo(roomGroup, wallBoxes, zCenter) {
    const deskGroup = new THREE.Group();
    deskGroup.position.set(-4.8, 0, zCenter - 1.5);
    const counterBase = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.15, 5.2), matMadera);
    counterBase.position.y = 0.575;
    const counterTop = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.1, 5.4), matOro);
    counterTop.position.y = 1.18;
    deskGroup.add(counterBase, counterTop);

    const bell = new THREE.Mesh(new THREE.SphereGeometry(0.1, 14, 14), matOro);
    bell.position.set(0.4, 1.28, 0.6);
    deskGroup.add(bell);

    const lampStand = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.12, 0.45, 12), matOro);
    lampStand.position.set(0.3, 1.42, -1.2);
    const lampShade = new THREE.Mesh(new THREE.ConeGeometry(0.24, 0.22, 16), new THREE.MeshStandardMaterial({ color: 0x165b33, emissive: 0x0b331b }));
    lampShade.position.set(0.3, 1.65, -1.2);
    deskGroup.add(lampStand, lampShade);
    roomGroup.add(deskGroup);
    wallBoxes.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(-4.8, 0.6, zCenter - 1.5), new THREE.Vector3(1.8, 1.3, 5.4)));

    const matSofa = new THREE.MeshStandardMaterial({ color: 0x5c1118, roughness: 0.7 });
    [-2.5, 2.2].forEach((offsetZ) => {
        const sofa = new THREE.Group();
        sofa.position.set(4.8, 0, zCenter + offsetZ);
        const seat = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.45, 2.6), matSofa);
        seat.position.y = 0.25;
        const back = new THREE.Mesh(new THREE.BoxGeometry(0.35, 1.05, 2.6), matSofa);
        back.position.set(0.55, 0.55, 0);
        sofa.add(seat, back);
        roomGroup.add(sofa);
        wallBoxes.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(4.8, 0.5, zCenter + offsetZ), new THREE.Vector3(1.5, 1.1, 2.7)));
    });

    const texCuadro0 = crearTexturaCuadro(0);
    const texCuadro1 = crearTexturaCuadro(1);
    [
        { x: -ROOM_WIDTH / 2 + 0.24, y: 3.1, z: zCenter - 2.0, rotY: Math.PI / 2, tex: texCuadro0 },
        { x: -ROOM_WIDTH / 2 + 0.24, y: 3.1, z: zCenter + 2.5, rotY: Math.PI / 2, tex: texCuadro1 },
        { x: ROOM_WIDTH / 2 - 0.24, y: 3.1, z: zCenter - 2.5, rotY: -Math.PI / 2, tex: texCuadro1 },
        { x: ROOM_WIDTH / 2 - 0.24, y: 3.1, z: zCenter + 2.2, rotY: -Math.PI / 2, tex: texCuadro0 }
    ].forEach((c) => {
        const frameGroup = new THREE.Group();
        frameGroup.position.set(c.x, c.y, c.z);
        frameGroup.rotation.y = c.rotY;
        const border = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.1, 0.08), matOro);
        const canvasMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.48, 1.88), new THREE.MeshBasicMaterial({ map: c.tex }));
        canvasMesh.position.z = 0.045;
        frameGroup.add(border, canvasMesh);
        roomGroup.add(frameGroup);
    });

    [[-6.3, -8.2], [6.3, -8.2], [-6.3, 8.2], [6.3, 8.2]].forEach(([cx, cz]) => {
        const col = new THREE.Mesh(new THREE.BoxGeometry(0.65, ROOM_HEIGHT, 0.65), matMadera);
        col.position.set(cx, ROOM_HEIGHT / 2, zCenter + cz);
        roomGroup.add(col);
    });
}

function construirHabitacionEnEscena(scene, index) {
    const zCenter = -index * ROOM_LENGTH;
    const zFrontWall = zCenter - ROOM_LENGTH / 2;
    const zBackWall = zCenter + ROOM_LENGTH / 2;

    const roomGroup = new THREE.Group();
    const wallBoxes = [];
    const drawers = [];
    const closets = [];
    const lights = [];

    const subFloor = new THREE.Mesh(new THREE.BoxGeometry(ROOM_WIDTH + 0.6, 0.2, ROOM_LENGTH + 0.2), new THREE.MeshBasicMaterial({ color: 0x120806 }));
    subFloor.position.set(0, -0.11, zCenter);
    roomGroup.add(subFloor);

    const floor = new THREE.Mesh(new THREE.PlaneGeometry(ROOM_WIDTH, ROOM_LENGTH), matAlfombra);
    floor.rotation.x = -Math.PI / 2;
    floor.position.set(0, 0.005, zCenter);
    roomGroup.add(floor);

    const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(ROOM_WIDTH, ROOM_LENGTH), matPared);
    ceiling.rotation.x = Math.PI / 2;
    ceiling.position.set(0, ROOM_HEIGHT, zCenter);
    roomGroup.add(ceiling);

    const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, ROOM_HEIGHT, ROOM_LENGTH), matPared);
    leftWall.position.set(-ROOM_WIDTH / 2, ROOM_HEIGHT / 2, zCenter);
    roomGroup.add(leftWall);
    wallBoxes.push(new THREE.Box3().setFromObject(leftWall));

    const rightWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, ROOM_HEIGHT, ROOM_LENGTH), matPared);
    rightWall.position.set(ROOM_WIDTH / 2, ROOM_HEIGHT / 2, zCenter);
    roomGroup.add(rightWall);
    wallBoxes.push(new THREE.Box3().setFromObject(rightWall));

    if (index === 0) {
        const elevOpenW = 3.2, elevOpenH = 3.3;
        const backSideW = (ROOM_WIDTH - elevOpenW) / 2;

        const backLeft = new THREE.Mesh(new THREE.BoxGeometry(backSideW, ROOM_HEIGHT, 0.45), matPared);
        backLeft.position.set(-(elevOpenW / 2 + backSideW / 2), ROOM_HEIGHT / 2, zBackWall);
        roomGroup.add(backLeft);
        wallBoxes.push(new THREE.Box3().setFromObject(backLeft));

        const backRight = new THREE.Mesh(new THREE.BoxGeometry(backSideW, ROOM_HEIGHT, 0.45), matPared);
        backRight.position.set(elevOpenW / 2 + backSideW / 2, ROOM_HEIGHT / 2, zBackWall);
        roomGroup.add(backRight);
        wallBoxes.push(new THREE.Box3().setFromObject(backRight));

        const backTop = new THREE.Mesh(new THREE.BoxGeometry(elevOpenW, ROOM_HEIGHT - elevOpenH, 0.45), matPared);
        backTop.position.set(0, elevOpenH + (ROOM_HEIGHT - elevOpenH) / 2, zBackWall);
        roomGroup.add(backTop);

        decorarVestibulo(roomGroup, wallBoxes, zCenter);
    } else {
        const winSide = (index % 2 === 0) ? 1 : -1;
        const winX = winSide * (ROOM_WIDTH / 2 - 0.22);
        const winRot = (winSide === 1) ? (-Math.PI / 2) : (Math.PI / 2);
        roomGroup.add(crearVentanaLargaNocheLluvia(winX, 3.6, zCenter + 1.2, winRot));
    }

    const sideWallW = (ROOM_WIDTH - DOOR_WIDTH) / 2;
    const frontLeft = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.45), matPared);
    frontLeft.position.set(-(DOOR_WIDTH / 2 + sideWallW / 2), ROOM_HEIGHT / 2, zFrontWall);
    roomGroup.add(frontLeft);
    wallBoxes.push(new THREE.Box3().setFromObject(frontLeft));

    const frontRight = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.45), matPared);
    frontRight.position.set(DOOR_WIDTH / 2 + sideWallW / 2, ROOM_HEIGHT / 2, zFrontWall);
    roomGroup.add(frontRight);
    wallBoxes.push(new THREE.Box3().setFromObject(frontRight));

    const frontTop = new THREE.Mesh(new THREE.BoxGeometry(DOOR_WIDTH, ROOM_HEIGHT - DOOR_HEIGHT, 0.45), matPared);
    frontTop.position.set(0, DOOR_HEIGHT + (ROOM_HEIGHT - DOOR_HEIGHT) / 2, zFrontWall);
    roomGroup.add(frontTop);

    const doorPivot = new THREE.Group();
    doorPivot.position.set(-DOOR_WIDTH / 2 + 0.04, 0, zFrontWall);

    const doorLeafW = DOOR_WIDTH - 0.08;
    const doorMesh = new THREE.Mesh(new THREE.BoxGeometry(doorLeafW, DOOR_HEIGHT - 0.04, 0.12), matMadera);
    doorMesh.position.set(doorLeafW / 2, (DOOR_HEIGHT - 0.04) / 2, 0);
    doorPivot.add(doorMesh);

    const doorKnob = new THREE.Mesh(new THREE.SphereGeometry(0.08, 12, 12), matOro);
    doorKnob.position.set(doorLeafW - 0.22, 1.45, 0.11);
    doorPivot.add(doorKnob);

    const signMesh = new THREE.Mesh(new THREE.BoxGeometry(1.18, 0.44, 0.06), new THREE.MeshBasicMaterial({ map: crearCartelMaderaDoors(index + 1) }));
    signMesh.position.set(0, DOOR_HEIGHT + 0.48, zFrontWall + 0.25);
    roomGroup.add(signMesh);

    const isLocked = index >= 2 && Math.random() < 0.28;
    let padlockMesh = null;
    if (isLocked) {
        padlockMesh = crearCandadoViejo();
        padlockMesh.position.set(doorLeafW - 0.22, 1.24, 0.14);
        doorPivot.add(padlockMesh);
    }

    roomGroup.add(doorPivot);

    const doorBox = new THREE.Box3(
        new THREE.Vector3(-DOOR_WIDTH / 2 - 0.1, 0, zFrontWall - 0.3),
        new THREE.Vector3(DOOR_WIDTH / 2 + 0.1, DOOR_HEIGHT, zFrontWall + 0.3)
    );

    let lit = true;
    if (index > 5) {
        lit = (index % 15 === 0) ? (Math.random() < 0.25) : (Math.random() < 0.65);
    }
    const chand = crearCandelabroClasico(0, ROOM_HEIGHT, zCenter, lit);
    roomGroup.add(chand.group);
    if (chand.light) lights.push(chand.light);

    const side = (index % 2 === 0) ? -1 : 1;
    const tableX = side * (ROOM_WIDTH / 2 - 0.85);
    const tableZ = zCenter - 2.2;

    const deskGroup = new THREE.Group();
    deskGroup.position.set(tableX, 0, tableZ);
    deskGroup.rotation.y = (side === -1) ? (Math.PI / 2) : (-Math.PI / 2);

    const baseBody = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.58, 0.85), matMadera);
    baseBody.position.y = 0.29;
    const topBoard = new THREE.Mesh(new THREE.BoxGeometry(1.86, 0.08, 0.9), matMadera);
    topBoard.position.y = 0.96;
    const sideL = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.36, 0.85), matMadera);
    sideL.position.set(-0.83, 0.76, 0);
    const sideR = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.36, 0.85), matMadera);
    sideR.position.set(0.83, 0.76, 0);
    deskGroup.add(baseBody, topBoard, sideL, sideR);

    const drawerGroup = new THREE.Group();
    drawerGroup.position.set(0, 0.75, 0.04);

    const matInteriorOscuro = new THREE.MeshStandardMaterial({ color: 0x160903, roughness: 0.9 });
    const dBottom = new THREE.Mesh(new THREE.BoxGeometry(1.48, 0.04, 0.74), matInteriorOscuro);
    dBottom.position.y = -0.12;
    const dFront = new THREE.Mesh(new THREE.BoxGeometry(1.52, 0.28, 0.05), matMadera);
    dFront.position.z = 0.36;
    const dBack = new THREE.Mesh(new THREE.BoxGeometry(1.48, 0.24, 0.04), matInteriorOscuro);
    dBack.position.z = -0.35;
    const dWallL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.24, 0.72), matInteriorOscuro);
    dWallL.position.x = -0.72;
    const dWallR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.24, 0.72), matInteriorOscuro);
    dWallR.position.x = 0.72;
    drawerGroup.add(dBottom, dFront, dBack, dWallL, dWallR);

    const drawerKnob = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), matOro);
    drawerKnob.position.set(0, 0, 0.41);
    drawerGroup.add(drawerKnob);

    const lootRoll = Math.random();
    let lootType = null;
    let lootMesh = null;
    if (lootRoll < 0.72) {
        lootMesh = new THREE.Group();
        lootMesh.position.set(0, -0.05, 0.08);
        if (lootRoll < 0.40) {
            lootType = 'lockpick';
            const ring = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.014, 8, 16), matOro);
            ring.rotation.x = Math.PI / 2;
            ring.position.x = -0.12;
            const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.24, 10), matOro);
            shaft.rotation.z = Math.PI / 2;
            shaft.position.x = 0.04;
            const tooth = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.015, 0.04), matOro);
            tooth.position.set(0.14, 0, 0.025);
            lootMesh.add(ring, shaft, tooth);
        } else {
            lootType = 'battery';
            const batBody = new THREE.Mesh(new THREE.CylinderGeometry(0.042, 0.042, 0.16, 16), new THREE.MeshStandardMaterial({ color: 0x114488, metalness: 0.6, roughness: 0.3 }));
            batBody.rotation.z = Math.PI / 2;
            const batCap = new THREE.Mesh(new THREE.CylinderGeometry(0.042, 0.042, 0.04, 16), new THREE.MeshStandardMaterial({ color: 0xd97724, metalness: 0.85, roughness: 0.2 }));
            batCap.rotation.z = Math.PI / 2;
            batCap.position.x = 0.09;
            lootMesh.add(batBody, batCap);
        }
        drawerGroup.add(lootMesh);
    }

    deskGroup.add(drawerGroup);
    roomGroup.add(deskGroup);

    wallBoxes.push(new THREE.Box3().setFromCenterAndSize(new THREE.Vector3(tableX, 0.5, tableZ), new THREE.Vector3(1.05, 1.1, 1.9)));

    drawers.push({
        group: drawerGroup,
        worldPos: new THREE.Vector3(tableX, 0.75, tableZ),
        open: false,
        targetZ: 0.04,
        lootType: lootType,
        lootTaken: false,
        lootMesh: lootMesh
    });

    const closetX = -side * (ROOM_WIDTH / 2 - 0.85);
    const closetZ = zCenter + 2.8;
    const closetMesh = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.9, 1.8), matMadera);
    closetMesh.position.set(closetX, 1.45, closetZ);
    roomGroup.add(closetMesh);
    wallBoxes.push(new THREE.Box3().setFromObject(closetMesh));

    closets.push({
        worldPos: new THREE.Vector3(closetX, 1.5, closetZ),
        hidePos: new THREE.Vector3(closetX - side * 0.2, 1.75, closetZ),
        lookYaw: (side === 1) ? (-Math.PI / 2) : (Math.PI / 2)
    });

    scene.add(roomGroup);

    return {
        index: index,
        zFrontWall: zFrontWall,
        group: roomGroup,
        doorPivot: doorPivot,
        doorOpen: false,
        doorTargetRot: 0,
        doorBox: doorBox,
        locked: isLocked,
        padlockMesh: padlockMesh,
        wallBoxes: wallBoxes,
        drawers: drawers,
        closets: closets,
        lights: lights
    };
}
