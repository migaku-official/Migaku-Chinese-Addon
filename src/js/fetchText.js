function fetchCText() {
  const sel = window.getSelection();
  const field = get_field(sel);
  const text = field.innerHTML;
  pycmd("textToCReading:||:||:" + text + ':||:||:' +  currentField.id.substring(1) + ':||:||:' + currentNoteId);
  
  
}
try {
  fetchCText();
} catch (e) {
  alert(e);
}
