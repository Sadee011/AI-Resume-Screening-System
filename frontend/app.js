// ── Backend only ──
async function analyzeResume(resumeText, jobText) {
  const res = await fetch('http://127.0.0.1:8000/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, job_description: jobText })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Backend error: ' + res.status);
  }
  return await res.json();
}


// ══════════════════════════════
//  Three.js Scene
// ══════════════════════════════
let scene, camera, renderer;
let coreOrb, orbGlow, ringGroup, particleSystem, starField;
let currentScore = 0, targetScore = 0;
let clock, analysisDone = false;
let burstParticles = [];

function initThreeJS() {
  const container = document.getElementById('canvas-container');
  const W = 380, H = 360;
  scene  = new THREE.Scene();
  clock  = new THREE.Clock();
  camera = new THREE.PerspectiveCamera(55, W / H, 0.1, 500);
  camera.position.set(0, 0, 10);
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(W, H);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  renderer.setClearColor(0x020817, 1);
  container.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  const dl = new THREE.DirectionalLight(0x00f5ff, 2); dl.position.set(5,8,5); scene.add(dl);
  const bl = new THREE.DirectionalLight(0x7c3aed, 1.5); bl.position.set(-5,-5,-5); scene.add(bl);
  const pl = new THREE.PointLight(0x00f5ff, 3, 20); pl.position.set(0,0,5); scene.add(pl);

  buildStarField(); buildCoreOrb(); buildRings(); buildParticleCloud(); buildGridPlane();
  animate();
}

function buildStarField() {
  const count = 800, geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    pos[i*3]   = (Math.random()-.5)*200;
    pos[i*3+1] = (Math.random()-.5)*200;
    pos[i*3+2] = (Math.random()-.5)*200-50;
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  starField = new THREE.Points(geo, new THREE.PointsMaterial({ color:0x8ab4f8, size:0.12, transparent:true, opacity:0.6, sizeAttenuation:true }));
  scene.add(starField);
}

function buildCoreOrb() {
  coreOrb = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.4, 4),
    new THREE.MeshStandardMaterial({ color:0x00f5ff, emissive:0x003344, metalness:0.9, roughness:0.1 })
  );
  scene.add(coreOrb);
  orbGlow = new THREE.Mesh(
    new THREE.IcosahedronGeometry(1.7, 2),
    new THREE.MeshBasicMaterial({ color:0x00f5ff, transparent:true, opacity:0.06, wireframe:true })
  );
  scene.add(orbGlow);
}

function buildRings() {
  ringGroup = new THREE.Group();
  [
    { r:2.4, tube:0.018, color:0x00f5ff, opacity:0.7,  rx:Math.PI/2,  ry:0,         speed:0.4   },
    { r:3.2, tube:0.012, color:0x7c3aed, opacity:0.5,  rx:Math.PI/3,  ry:Math.PI/4, speed:-0.3  },
    { r:4.0, tube:0.008, color:0x00f5ff, opacity:0.35, rx:Math.PI/6,  ry:Math.PI/3, speed:0.2   },
    { r:5.0, tube:0.005, color:0xffffff, opacity:0.15, rx:-Math.PI/4, ry:Math.PI/5, speed:-0.15 },
  ].forEach(d => {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(d.r, d.tube, 8, 120),
      new THREE.MeshBasicMaterial({ color:d.color, transparent:true, opacity:d.opacity })
    );
    ring.rotation.set(d.rx, d.ry, 0);
    ring.userData = { speed:d.speed, baseOpacity:d.opacity };
    ringGroup.add(ring);
  });
  scene.add(ringGroup);
}

function buildParticleCloud() {
  const count = 200, geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3), phi = Math.PI*(3-Math.sqrt(5));
  for (let i = 0; i < count; i++) {
    const y = 1-(i/(count-1))*2, r = Math.sqrt(1-y*y)*3.5, t = phi*i;
    pos[i*3]   = Math.cos(t)*r*(0.8+Math.random()*0.4);
    pos[i*3+1] = y*3.5*(0.8+Math.random()*0.4);
    pos[i*3+2] = Math.sin(t)*r*(0.8+Math.random()*0.4);
  }
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  particleSystem = new THREE.Points(geo, new THREE.PointsMaterial({ color:0x00f5ff, size:0.07, transparent:true, opacity:0.5, sizeAttenuation:true }));
  scene.add(particleSystem);
}

function buildGridPlane() {
  const grid = new THREE.GridHelper(30, 30, 0x00f5ff, 0x001122);
  grid.position.y = -5; grid.material.transparent = true; grid.material.opacity = 0.08;
  scene.add(grid);
}

function triggerBurst(score) {
  const color = score>=70 ? 0x22c55e : score>=45 ? 0xf59e0b : 0xef4444;
  for (let i = 0; i < 80; i++) {
    const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.04,4,4), new THREE.MeshBasicMaterial({ color }));
    const theta = Math.random()*Math.PI*2, phi2 = Math.random()*Math.PI, spd = 0.05+Math.random()*0.12;
    mesh.userData = {
      vx:Math.sin(phi2)*Math.cos(theta)*spd, vy:Math.sin(phi2)*Math.sin(theta)*spd, vz:Math.cos(phi2)*spd,
      life:1.0, decay:0.012+Math.random()*0.01
    };
    scene.add(mesh); burstParticles.push(mesh);
  }
}

function updateSceneTheme(score) {
  const c = score>=70 ? new THREE.Color(0x22c55e) : score>=45 ? new THREE.Color(0xf59e0b) : new THREE.Color(0xef4444);
  coreOrb.material.color.copy(c);
  coreOrb.material.emissive.copy(c.clone().multiplyScalar(0.2));
  orbGlow.material.color.copy(c);
  particleSystem.material.color.copy(c);
  ringGroup.children[0].material.color.copy(c);
  const s = 0.5+(score/100)*1.2;
  coreOrb.scale.set(s,s,s); orbGlow.scale.set(s,s,s);
}

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();
  if (analysisDone) currentScore += (targetScore-currentScore)*0.03;
  if (coreOrb) { coreOrb.rotation.y = t*0.3; coreOrb.rotation.x = Math.sin(t*0.2)*0.2; }
  if (orbGlow) {
    orbGlow.rotation.y = -t*0.15; orbGlow.rotation.z = t*0.1;
    orbGlow.scale.setScalar((1+Math.sin(t*1.5)*0.03)*(0.5+(currentScore/100)*1.2));
  }
  if (ringGroup) {
    ringGroup.rotation.z = t*0.05;
    ringGroup.children.forEach((r,i) => {
      r.rotation.z += r.userData.speed*0.01;
      r.material.opacity = r.userData.baseOpacity*(0.7+Math.sin(t*1.2+i)*0.3);
    });
  }
  if (particleSystem) { particleSystem.rotation.y = t*0.08; particleSystem.rotation.x = Math.sin(t*0.05)*0.1; }
  if (starField) starField.rotation.y = t*0.005;
  for (let i = burstParticles.length-1; i >= 0; i--) {
    const p = burstParticles[i], d = p.userData;
    p.position.x += d.vx; p.position.y += d.vy; p.position.z += d.vz;
    d.life -= d.decay; p.material.opacity = Math.max(0,d.life); p.material.transparent = true;
    if (d.life <= 0) { scene.remove(p); burstParticles.splice(i,1); }
  }
  renderer.render(scene, camera);
}


// ══════════════════════════════
//  Analyze Button
// ══════════════════════════════
document.getElementById('analyze-btn').addEventListener('click', async () => {
  const resumeText = document.getElementById('resume').value;
  const jobText    = document.getElementById('job-desc').value;

  if (!resumeText || !jobText) { alert('Both fields are required!'); return; }

  const btn = document.getElementById('analyze-btn');
  const btnText = btn.querySelector('.btn-text');
  const btnIcon = btn.querySelector('.btn-icon');
  btnText.textContent = 'ANALYZING...'; btnIcon.textContent = '⏳'; btn.disabled = true;

  try {
    const data = await analyzeResume(resumeText, jobText);

    document.getElementById('results-section').classList.remove('hidden');

    const scoreEl = document.getElementById('score-value');
    scoreEl.textContent = `${data.score}%`;
    scoreEl.style.color = data.color;
    document.getElementById('match-label').textContent = `${data.emoji} ${data.label}`;
    document.getElementById('advice-text').textContent = data.advice;

    const matchingEl = document.getElementById('matching-skills');
    const missingEl  = document.getElementById('missing-skills');
    matchingEl.innerHTML = '<h3>✅ MATCHING SKILLS</h3>';
    data.skills.matching_skills.forEach((s,i) => {
      const span = document.createElement('span');
      span.className = 'skill match'; span.textContent = s;
      span.style.animationDelay = `${i*80}ms`; matchingEl.appendChild(span);
    });
    missingEl.innerHTML = '<h3>❌ MISSING SKILLS</h3>';
    data.skills.missing_skills.forEach((s,i) => {
      const span = document.createElement('span');
      span.className = 'skill missing'; span.textContent = s;
      span.style.animationDelay = `${i*80}ms`; missingEl.appendChild(span);
    });

    const barFill = document.getElementById('bar-fill');
    barFill.style.background = data.score >= 70 ? 'linear-gradient(90deg,#16a34a,#22c55e)'
                             : data.score >= 45 ? 'linear-gradient(90deg,#d97706,#f59e0b)'
                                                : 'linear-gradient(90deg,#b91c1c,#ef4444)';
    setTimeout(() => { barFill.style.width = `${data.score}%`; }, 100);

    targetScore = data.score; analysisDone = true;
    updateSceneTheme(data.score);
    setTimeout(() => triggerBurst(data.score), 300);

  } catch (err) {
    console.error(err);
    alert('⚠️ Analysis failed: ' + err.message + '\n\nBackend run වෙනවාද check කරන්න:\nuvicorn api.main:app --port 8000 --reload');
  } finally {
    btnText.textContent = 'ANALYZE MATCH'; btnIcon.textContent = '⚡'; btn.disabled = false;
  }
});

window.onload = () => initThreeJS();