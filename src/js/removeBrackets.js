function cleanUpSpaces(text){
    return text.replace(/ /g, '');
}

function removeBrackets() {
  const sel = window.getSelection();
  const field = get_field(sel);
  let text = field.innerHTML;
  if (text === "") return;
  if(!/\[[^\[]*?\]/.test(text))return;
  let pattern2 = /(\[sound:[^\]]+?\])|(?:\[\d*\])/g;
  if(!/\[[^\[]*?\]/.test(text))return ;
  replacements = false;
  pattern = /<[^<]*?>/g;
  matches = false;
  if (pattern.test(text)){
    matches = text.match(pattern)
    for (x in matches){
        text = text.replace(matches[x], '---NEWLINE___')
    }   
    // text.match(/<[^<]?>/, '')
  }
  
  matches2 = false;
  if (pattern2.test(text)){
    matches2 = text.match(pattern2)
    for (x in matches2){
        text = text.replace(matches2[x], '---SOUNDREF___')
    }   
    // text.match(/<[^<]?>/, '')
  }
  text = cleanUpSpaces(text);
  if(matches){
    for (x in matches){
      text = text.replace( '---NEWLINE___', matches[x])
    } 

  }

  text = text.replace(/\[[^\[]*?\]/g, "");
  if(matches2){
    for (x in matches2){
      text = text.replace( '---SOUNDREF___', matches2[x])
    } 

  }
  const html = text;
  selectAllFieldNodes(field, sel);
  setFormat("inserthtml", html);
}
try {
  removeBrackets();
} catch (e) {
  alert(e);
}
