window.$ = id => document.getElementById(id);

const CURSEFORGE_BASE = 'https://www.curseforge.com/minecraft/mc-mods/';
const MODRINTH_BASE   = 'https://modrinth.com/mod/';

//each mod has one card
function buildCard(mod) {
  const badges = mod.minecraft_versions
    .map(v => `<span class="badge">${v}</span>`)
    .join('');

  const links = [
    mod.curse_slug  ? `<a href="${CURSEFORGE_BASE}${mod.curse_slug}" target="_blank" rel="noopener">CurseForge</a>` : '',
    mod.modrinth_id ? `<a href="${MODRINTH_BASE}${mod.modrinth_id}" target="_blank" rel="noopener">Modrinth</a>`   : '',
  ].filter(Boolean).join('');

  return `
    <div class="card">
      <h3>${mod.name}</h3>
      <p>${mod.description}</p>
      <div class="badges">${badges}</div>
      ${links ? `<div class="links">${links}</div>` : ''}
    </div>`;
}

// section has the label and then grid of cards
function buildSection(category, mods) {
  const cards = mods.map(buildCard).join('');
  return `
    <section class="category">
      <h2>${category.label}</h2>
      <div class="grid">${cards}</div>
    </section>`;
}

//build all and set innerHTML of main
async function render() {
  const main = $('main');
  try {
    const [categories, mods] = await Promise.all([
      fetch('categories.json').then(r => r.json()),
      fetch('mods.json').then(r => r.json()),
    ]);

    const html = categories.map(cat => {
      const catMods = mods.filter(m => m.category === cat.id);
      return catMods.length ? buildSection(cat, catMods) : '';
    }).join('');

    main.innerHTML = html;
  } catch (err) {
    main.innerHTML = `<p id="error">Failed to load mod data: ${err.message}</p>`;
  }
}


render();
