import {evaluate} from '../functions/_shared/engine.js';
const parts=[];
for await (const chunk of process.stdin) parts.push(chunk);
const inputs=JSON.parse(Buffer.concat(parts).toString('utf8'));
const outputs=inputs.map(input=>{
  try { return {ok: true, data: evaluate(input)}; }
  catch(e) {return {ok:false, error:e.message};}
});
process.stdout.write(JSON.stringify(outputs));
