function removeHTML() {
  const sel = window.getSelection();
  const field = get_field(sel);
  let text = field.innerHTML;
  if (text === "") return;
  field.innerHTML = '';
  text = text.replace('<br>', '---newline---')
  let html = text.replace(/<span class="[^<]*?">◆<\/span>/g, "");
  html = html.replace(/\<[^<]*?\>/g, "");
  html = html.replace('---newline---', '<br>');
  setFormat("inserthtml", html.replace(/ /g, ''));
  clean_field(field);
}
try {
  removeHTML();
} catch (e) {
  alert(e);
}
