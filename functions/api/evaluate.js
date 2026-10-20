import { evaluate } from '../_shared/engine.js';

export async function onRequestPost({ request }) {
  try {
    // La API solo procesa una evaluación temporal y no persiste datos.
    const body = await request.text();
    if (!body || new TextEncoder().encode(body).length > 30000) {
      return Response.json({error: 'Formulario demasiado grande o vacío'}, {status: 413, headers: {'Cache-Control':'no-store'}});
    }
    const result = evaluate(JSON.parse(body));
    return Response.json(result, {headers: {'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
  } catch (error) {
    const detail = error instanceof Error ? error.message : 'Datos no válidos';
    return Response.json({error: detail}, {status: 400, headers: {'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
  }
}
