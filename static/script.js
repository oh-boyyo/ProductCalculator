const materials = document.getElementById('materials');
const addButton = document.getElementById('add-material');
const template = document.getElementById('material-template');
let nextId = Math.max(0, ...Array.from(materials.querySelectorAll('[name="material_id"]'), el => Number(el.value) + 1));

function renumber() {
  materials.querySelectorAll('[data-material]').forEach((node, index) => {
    node.querySelector('.material-number').textContent = index + 1;
    node.querySelector('[data-remove]').disabled = materials.querySelectorAll('[data-material]').length === 1;
  });
}

addButton.addEventListener('click', () => {
  if (materials.querySelectorAll('[data-material]').length >= 100) return;
  const id = String(nextId++);
  const html = template.innerHTML.replaceAll('__ID__', id);
  materials.insertAdjacentHTML('beforeend', html);
  renumber();
  materials.lastElementChild.querySelector('input[type="text"]').focus();
});

materials.addEventListener('click', event => {
  if (!event.target.matches('[data-remove]')) return;
  if (materials.querySelectorAll('[data-material]').length <= 1) return;
  event.target.closest('[data-material]').remove();
  renumber();
});
renumber();

if (document.querySelector('#results')) {
  document.querySelector('#results').scrollIntoView({behavior: 'smooth', block: 'start'});
}
