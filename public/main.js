'use strict';
let schema = null;
let answers = {};
let step = 0;
let showingResult = false;
const $ = (id) => document.getElementById(id);
const ESC = (s) => String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const matches = (cond) => {if(cond.all)return cond.all.every(matches);if(cond.any)return cond.any.some(matches);const actual=answers[cond.field];if(Object.hasOwn(cond,'lt'))return Number.isInteger(actual)&&actual<cond.lt;if(Object.hasOwn(cond,'in'))return cond.in.includes(actual);return actual===cond.eq;};
const visible = (q) => !q.show_if || matches(q.show_if);
const questions = () => schema.questions.filter(visible);
const complete = (q) => Object.hasOwn(answers, q.id) && (q.type !== 'year' || answers[q.id] === 'unknown' || (Number.isInteger(answers[q.id]) && answers[q.id] >= 1800 && answers[q.id] <= new Date().getFullYear()));
const resetHidden = () => { for (const q of schema.questions) if (!visible(q)) delete answers[q.id]; };
const allowed = () => ['habitual','segunda','desocupada'].includes(answers.uso);
const excluded = () => ['alquilada','no_residencial'].includes(answers.uso);

function setAnswer(id,value){answers[id]=value;resetHidden();$('validation').textContent='';render();}
function render(){
  if(showingResult)return;
  let qlist=questions(); step=Math.max(0,Math.min(step,qlist.length-1));
  let q=qlist[step], count=qlist.length, done=qlist.filter(complete).length;
  $('sidebar-count').textContent=`${String(step+1).padStart(2,'0')} / ${String(count).padStart(2,'0')}`;
  $('progress-fill').style.width=`${Math.round(done/count*100)}%`;
  $('step-count').textContent=`PREGUNTA ${step+1} DE ${count}`;
  $('current-section').textContent=q.section.toUpperCase();
  $('q-index').textContent=`${String(step+1).padStart(2,'0')} —`;
  $('panel-title').textContent=q.label;
  $('question-help').textContent=q.help;
  const safety = $('active-alert');
  if(answers.caldera === 'fuga'){
    safety.classList.remove('hidden');
    safety.textContent='POSIBLE EMERGENCIA: si sospechas una fuga de gas, abandona la zona; desde un lugar seguro, llama al 112 o al servicio de emergencias. No acciones interruptores ni produzcas llamas.';
  }else if(answers.estructura_estado === 'graves'){
    safety.classList.remove('hidden');
    safety.textContent='AVISO DE SEGURIDAD: si hay signos de inestabilidad estructural, evita acceder a zonas peligrosas y solicita una evaluación técnica urgente.';
  }else safety.classList.add('hidden');
  $('next').textContent= step===count-1 || (q.id==='uso' && excluded()) ? 'Obtener resultado →' : 'Continuar →';
  $('back').disabled=step===0;
  const sections=[...new Set(schema.questions.map(x=>x.section))];
  const currentSec=sections.indexOf(q.section);
  $('sections').innerHTML=sections.map((sec,i)=>`<div class="section-row ${i===currentSec?'active':i<currentSec?'done':''}"><span class="section-number">${i<currentSec?'✓':String(i+1).padStart(2,'0')}</span>${ESC(sec)}</div>`).join('');
  const box=$('answers');box.innerHTML='';
  if(q.type==='choice'){
    const list=document.createElement('div');list.className='answer-list';
    for (const [value,label] of q.options){
      const btn=document.createElement('button');btn.type='button';btn.className='option'+(answers[q.id]===value?' selected':'');
      btn.setAttribute('aria-pressed', String(answers[q.id]===value));
      btn.innerHTML='<span class="radio-dot" aria-hidden="true"></span><span>'+ESC(label)+'</span>';
      btn.addEventListener('click',()=>setAnswer(q.id,value));list.appendChild(btn);
    }
    box.appendChild(list);
  } else {
    const wrap=document.createElement('div');wrap.className='year-wrap';
    const label=document.createElement('label');label.htmlFor='year-field';label.textContent='Año de construcción';
    const input=document.createElement('input');input.id='year-field';input.className='year-input';input.type='number';input.min='1800';input.max=String(new Date().getFullYear());input.placeholder='Ej. 1985';input.value=typeof answers[q.id]==='number' ? String(answers[q.id]) : '';
    input.addEventListener('change',()=>{const n=Number(input.value);if(!input.value||!Number.isInteger(n)||n<1800||n>new Date().getFullYear()){$('validation').textContent='Introduce un año válido o selecciona «No lo sé».';return;}setAnswer(q.id,n);});
    wrap.append(label,input);
    const opt=document.createElement('button');opt.type='button';opt.className='option'+(answers[q.id]==='unknown'?' selected':'');opt.innerHTML='<span class="radio-dot" aria-hidden="true"></span><span>No lo sé</span>';
    opt.addEventListener('click',()=>setAnswer(q.id,'unknown'));wrap.appendChild(opt);box.appendChild(wrap);
  }
}

async function next(){
  let qlist=questions(),q=qlist[step];
  if(q.type==='year'){
    const input=$('year-field');
    if(input && input.value.trim() && answers.anio !== 'unknown'){
      const n=Number(input.value);
      if(Number.isInteger(n)&&n>=1800&&n<=new Date().getFullYear())answers.anio=n;
    }
  }
  if(!complete(q)){$('validation').textContent='Selecciona una respuesta o indica «No lo sé» para continuar.';return;}
  resetHidden();qlist=questions();
  if(excluded() || step===qlist.length-1){await finish();return;}
  step++;render();
}

function liItems(id, values){
  const target=$(id);target.innerHTML='';
  for(const val of values){const li=document.createElement('li');li.textContent=val;target.appendChild(li);}
}
function showRules(rules){
  const target=$('fired-rules');target.innerHTML='';
  if(!rules.length){const p=document.createElement('p');p.className='question-help';p.textContent='No se activaron reglas de riesgo alto o medio con las respuestas disponibles.';target.appendChild(p);return;}
  for(const rule of rules){const card=document.createElement('div');card.className='rule-card';
    const tag=document.createElement('span');tag.className='rule-tag';tag.textContent=rule.id+' · '+rule.tier.toUpperCase();
    const title=document.createElement('strong');title.textContent=rule.category;
    const p=document.createElement('p');p.textContent=rule.reason;
    card.append(tag,title,p);target.appendChild(card);
  }
}
async function finish(){
  $('next').disabled=true;
  try{
    const response=await fetch('/api/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(answers)});
    const data=await response.json();if(!response.ok)throw new Error(data.error||'No se pudo procesar la evaluación');
    showingResult=true;$('question-view').classList.add('hidden');$('result-view').classList.remove('hidden');
    if(data.status==='excluded'){
      $('result-title').textContent='Fuera del alcance del prototipo';
      $('risk-label').textContent='No evaluable';$('risk-state').textContent='Uso no incluido';
      $('result-box').className='result-box';$('risk-description').textContent=data.reason;
    }else{
      $('result-title').textContent='Resultado de tu vivienda';
      $('result-box').className='result-box '+data.level;
      $('risk-label').textContent=`Riesgo ${data.level}`;
      $('risk-state').textContent=data.provisional?'PROVISIONAL':data.missing.length?'CON DATOS PENDIENTES':'RESPUESTAS COMPLETAS';
      $('risk-description').textContent=data.message;
    }
    $('emergency').classList.toggle('hidden',!data.urgent);
    $('missing-block').classList.toggle('hidden',!data.missing?.length);
    liItems('missing-list',(data.missing||[]).map(x=>x.label));
    showRules(data.triggered_rules||[]);
    liItems('recommendations',data.recommendations?.length?data.recommendations:['Mantener las medidas de conservación y revisar el estado de la vivienda periódicamente.']);
    $('reco-block').classList.toggle('hidden',data.status==='excluded');
    $('rules-block').classList.toggle('hidden',data.status==='excluded');
    $('sidebar-count').textContent='FIN';$('progress-fill').style.width='100%';
    $('sections').querySelectorAll('.section-row').forEach(x=>x.classList.add('done'));
    window.scrollTo({top:document.querySelector('.workspace').getBoundingClientRect().top+window.scrollY-15,behavior:'smooth'});
  }catch(e){$('validation').textContent=e.message;}finally{$('next').disabled=false;}
}
function reset(){answers={};step=0;edit();}
function edit(){showingResult=false;$('question-view').classList.remove('hidden');$('result-view').classList.add('hidden');render();}
const defaults={uso:'habitual',anio:2016,estructura:'hormigon',electricidad:'revisada',calefaccion:'electrica',detectores:'si',humedades:'no',agua:'no',estructura_estado:'bien',conservacion:'bueno',desocupacion:'no',seguridad:'ambas',inundaciones:'no'};
const examples={
  bajo:{...defaults},
  medio:{...defaults,calefaccion:'gas',caldera:'pendiente',detectores:'no',desocupacion:'si'},
  alto:{...defaults,anio:1985,estructura:'madera',reforma:'si',proteccion_madera:'no',informe_madera:'desfavorable'},
  provisional:{...defaults,anio:'unknown',electricidad:'unknown',estructura:'unknown'}
};
async function load(){
  const response=await fetch('/api/schema');if(!response.ok)throw new Error('No se pudo cargar la base de conocimiento.');schema=await response.json();
  $('back').addEventListener('click',()=>{if(step>0){step--;render();}});
  $('next').addEventListener('click',next);
  $('reset').addEventListener('click',reset);
  $('again').addEventListener('click',reset);
  $('edit-answers').addEventListener('click',()=>{step=0;edit();});
  $('print').addEventListener('click',()=>window.print());
  document.querySelectorAll('[data-scenario]').forEach(btn=>btn.addEventListener('click',()=>{answers={...examples[btn.dataset.scenario]};step=0;edit();document.querySelector('.workspace').scrollIntoView({behavior:'smooth'});}));
  render();
}
load().catch(err=>{ $('panel-title').textContent='No se puede iniciar el sistema';$('question-help').textContent=err.message+' Abre la página mediante «py app.py», no directamente desde un archivo HTML.';});
