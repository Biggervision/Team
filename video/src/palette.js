// Brand tokens. Provisional values sampled from the portrait backdrop.
// Swap the hex values for the official brand reference; keep the roles.
const P = {
  canvas: '#F7F9FB',
  ink: '#0E1A2B',
  ink2: '#5B6878',
  mute: '#A9B4C0',
  line: '#DDE4EC',
  brand: '#20B4CE',
  deep: '#0B5F78',
  tint: '#E3F6FA',
  warn: '#F08A24',
  loss: '#E5484D',
};

function rgba(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
}
