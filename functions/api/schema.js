import { schema } from '../_shared/engine.js';

export function onRequestGet() {
  return Response.json(schema(), {headers: {'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
}
