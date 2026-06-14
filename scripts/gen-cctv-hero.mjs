/**
 * Generate a branded CCTV hero illustration (SVG) and rasterize to
 * jpg + webp (desktop + mobile), keeping the same filenames/references.
 * Run: node scripts/gen-cctv-hero.mjs
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import sharp from 'sharp';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HERO_DIR = path.join(__dirname, '..', 'public', 'assets', 'images', 'hero');

const PRIMARY = '#1A3A5C';
const PRIMARY_DARK = '#0F2640';
const DEEPER = '#091A2E';
const ACCENT = '#D4AF37';

function svg(w, h) {
  const cx = w * 0.62, cy = h * 0.42;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${PRIMARY}"/>
      <stop offset="0.55" stop-color="${PRIMARY_DARK}"/>
      <stop offset="1" stop-color="${DEEPER}"/>
    </linearGradient>
    <radialGradient id="glow" cx="62%" cy="42%" r="55%">
      <stop offset="0" stop-color="${ACCENT}" stop-opacity="0.18"/>
      <stop offset="1" stop-color="${ACCENT}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="${w}" height="${h}" fill="url(#bg)"/>
  <rect width="${w}" height="${h}" fill="url(#glow)"/>

  <!-- subtle grid -->
  <g stroke="${ACCENT}" stroke-opacity="0.06" stroke-width="1">
    ${Array.from({length: Math.ceil(w/64)}, (_,i)=>`<line x1="${i*64}" y1="0" x2="${i*64}" y2="${h}"/>`).join('')}
    ${Array.from({length: Math.ceil(h/64)}, (_,i)=>`<line x1="0" y1="${i*64}" x2="${w}" y2="${i*64}"/>`).join('')}
  </g>

  <!-- field-of-view cone -->
  <path d="M ${cx} ${cy} L ${cx-w*0.5} ${cy+h*0.55} L ${cx-w*0.18} ${cy+h*0.62} Z"
        fill="${ACCENT}" fill-opacity="0.10"/>

  <!-- camera, rotated -->
  <g transform="translate(${cx} ${cy}) rotate(28)">
    <!-- mount arm -->
    <rect x="-14" y="-6" width="120" height="14" rx="7" fill="${ACCENT}"/>
    <circle cx="-14" cy="1" r="16" fill="${ACCENT}"/>
    <!-- body -->
    <rect x="-150" y="-44" width="170" height="78" rx="20" fill="${PRIMARY_DARK}" stroke="${ACCENT}" stroke-width="3"/>
    <!-- lens -->
    <circle cx="-150" cy="-5" r="46" fill="${DEEPER}" stroke="${ACCENT}" stroke-width="4"/>
    <circle cx="-150" cy="-5" r="26" fill="#000"/>
    <circle cx="-162" cy="-17" r="9" fill="${ACCENT}" fill-opacity="0.85"/>
    <!-- top fin -->
    <rect x="-70" y="-58" width="70" height="16" rx="8" fill="${ACCENT}" fill-opacity="0.9"/>
    <!-- rec light -->
    <circle cx="5" cy="-22" r="7" fill="#e23"/>
  </g>

  <!-- scanning ring near lens -->
  <circle cx="${cx-150*Math.cos(28*Math.PI/180)+5}" cy="${cy-150*Math.sin(28*Math.PI/180)}" r="0" fill="none"/>
</svg>`;
}

async function emit(name, w, h) {
  const buf = Buffer.from(svg(w, h));
  await sharp(buf).jpeg({ quality: 82, mozjpeg: true }).toFile(path.join(HERO_DIR, `${name}.jpg`));
  await sharp(buf).webp({ quality: 80 }).toFile(path.join(HERO_DIR, `${name}.webp`));
  console.log(`  ${name}.jpg / .webp (${w}x${h})`);
}

await emit('cctv_installation', 1600, 900);
await emit('cctv_installation_mobile', 800, 520);
console.log('Done.');
