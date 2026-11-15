const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playAudio(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const now = audioCtx.currentTime;

    if (type === 'type') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, now);
        osc.frequency.exponentialRampToValueAtTime(1400, now + 0.04);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.04);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.04);

    } else if (type === 'success') {
        [330, 440, 660, 880].forEach((freq, idx) => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(freq, now + (idx * 0.09));
            gain.gain.setValueAtTime(0.12, now + (idx * 0.09));
            gain.gain.exponentialRampToValueAtTime(0.001, now + (idx * 0.09) + 0.22);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now + (idx * 0.09));
            osc.stop(now + (idx * 0.09) + 0.22);
        });

    } else if (type === 'error') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(260, now);
        osc.frequency.linearRampToValueAtTime(110, now + 0.28);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.linearRampToValueAtTime(0.001, now + 0.28);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.28);

    } else if (type === 'open') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(45, now + 0.6);
        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.6);

    } else if (type === 'creak') {
        const osc = audioCtx.createOscillator();
        const osc2 = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc2.type = 'triangle';
        osc.frequency.setValueAtTime(190, now);
        osc.frequency.linearRampToValueAtTime(340, now + 0.25);
        osc.frequency.linearRampToValueAtTime(150, now + 0.65);

        osc2.frequency.setValueAtTime(196, now);
        osc2.frequency.linearRampToValueAtTime(352, now + 0.25);
        osc2.frequency.linearRampToValueAtTime(145, now + 0.65);

        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
        osc.connect(gain);
        osc2.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc2.start(now);
        osc.stop(now + 0.7);
        osc2.stop(now + 0.7);

    } else if (type === 'drawer') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(120, now);
        osc.frequency.linearRampToValueAtTime(85, now + 0.22);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.24);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.24);

    } else if (type === 'step') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(95, now);
        osc.frequency.exponentialRampToValueAtTime(42, now + 0.08);
        gain.gain.setValueAtTime(0.09, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.09);

    } else if (type === 'ding') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.9);

    } else if (type === 'pickup') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(520, now);
        osc.frequency.exponentialRampToValueAtTime(980, now + 0.14);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.15);

    } else if (type === 'unlock') {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.setValueAtTime(520, now + 0.08);
        gain.gain.setValueAtTime(0.14, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.22);

    } else if (type === 'monster') {
        const osc = audioCtx.createOscillator();
        const osc2 = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sawtooth';
        osc2.type = 'square';
        osc.frequency.setValueAtTime(55, now);
        osc.frequency.linearRampToValueAtTime(145, now + 1.5);
        osc.frequency.linearRampToValueAtTime(42, now + 2.8);

        osc2.frequency.setValueAtTime(61, now);
        osc2.frequency.linearRampToValueAtTime(158, now + 1.5);
        osc2.frequency.linearRampToValueAtTime(38, now + 2.8);

        gain.gain.setValueAtTime(0.02, now);
        gain.gain.linearRampToValueAtTime(0.26, now + 1.4);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 2.9);
        osc.connect(gain);
        osc2.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc2.start(now);
        osc.stop(now + 2.9);
        osc2.stop(now + 2.9);
    }
}

const musicaHotelReal = new Audio('/static/Corredor_Horror.mp3');
musicaHotelReal.loop = true;
musicaHotelReal.volume = 0.42;
