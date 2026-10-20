/*
  ViviendaSeg - Versión Prolog independiente de la base de reglas.
  Para ejecutarlo se requiere SWI-Prolog (opcional). La web usa el motor
  Python y no invoca este archivo, para permitir ejecución sin instalar Prolog.
  Prototipo docente: no utilizar como evaluación real de asegurabilidad.
*/
:- dynamic dato/2.

% Memoria de trabajo: un dato por atributo; no usar hechos predeterminados.
poner(Clave, Valor) :- retractall(dato(Clave, _)), assertz(dato(Clave, Valor)).
limpiar :- retractall(dato(_, _)).

% La base de conocimiento: antecedente de cada regla -> conclusión.
regla(r01, alto) :- dato(estructura, madera), dato(informe_madera, desfavorable).
regla(r02, alto) :- dato(estructura, mixta), dato(material_mixto, si), dato(informe_madera, desfavorable).
regla(r03, alto) :- dato(electricidad, defectuosa).
regla(r04, alto) :- dato(calefaccion, gas), dato(caldera, fuga).
regla(r05, alto) :- dato(estructura_estado, graves).

regla(r06, medio) :- dato(electricidad, sin_revision).
regla(r07, medio) :- dato(calefaccion, gas), dato(caldera, pendiente).
regla(r08, medio) :- dato(calefaccion, combustion), dato(chimenea, pendiente).
regla(r09, medio) :- dato(calefaccion, combustion), dato(detectores, no).
regla(r10, medio) :- dato(humedades, graves).
regla(r11, medio) :- dato(agua, si).
regla(r12, medio) :- dato(conservacion, pendiente).
regla(r13, medio) :- dato(desocupacion, si).
regla(r14, medio) :- dato(desocupacion, si), dato(seguridad, ninguna).
regla(r15, medio) :- dato(inundaciones, si).
regla(r16, medio) :- estructura_con_madera, dato(proteccion_madera, no),
    (dato(informe_madera, sin_informe) ; dato(informe_madera, unknown)).

estructura_con_madera :- dato(estructura, madera).
estructura_con_madera :- dato(estructura, mixta), dato(material_mixto, si).

% Las respuestas requeridas; las preguntas condicionales son visibles
% solamente cuando se cumplen sus antecedentes.
esencial(uso).
esencial(anio).
esencial(estructura).
esencial(electricidad).
esencial(calefaccion).
esencial(humedades).
esencial(agua).
esencial(estructura_estado).
esencial(desocupacion).
esencial(detectores).
esencial(conservacion).
esencial(seguridad).
esencial(inundaciones).
esencial(reforma) :- dato(anio, N), integer(N), N < 2006.
esencial(material_mixto) :- dato(estructura, mixta).
esencial(proteccion_madera) :- estructura_con_madera, \+ dato(informe_madera, favorable).
esencial(informe_madera) :- estructura_con_madera.
esencial(caldera) :- dato(calefaccion, gas).
esencial(chimenea) :- dato(calefaccion, combustion).

faltante(Campo) :- esencial(Campo), (\+ dato(Campo, _) ; dato(Campo, unknown)).
faltante(informe_madera) :- estructura_con_madera, dato(informe_madera, sin_informe).

% La prioridad es alto > medio; el nivel medio es provisional cuando faltan
% respuestas, a no ser que ya exista un riesgo alto confirmado.
resultado(alto, no, Reglas, Faltantes) :-
    regla(_, alto), !, hallazgos(Reglas, Faltantes).
resultado(medio, si, Reglas, Faltantes) :-
    faltante(_), !, hallazgos(Reglas, Faltantes).
resultado(medio, no, Reglas, Faltantes) :-
    regla(_, medio), !, hallazgos(Reglas, Faltantes).
resultado(bajo, no, Reglas, Faltantes) :-
    hallazgos(Reglas, Faltantes).

hallazgos(Reglas, Faltantes) :-
    findall(ID-Tier, regla(ID,Tier), L), sort(L, Reglas),
    findall(C, faltante(C), M), sort(M, Faltantes).

imprimir_resultado :-
    resultado(Nivel, Provisional, Reglas, Faltantes),
    format('Nivel: ~w, provisional: ~w~n', [Nivel, Provisional]),
    format('Reglas: ~w~n', [Reglas]),
    format('Faltantes: ~w~n', [Faltantes]).

% Un ejemplo compacto de prueba, sin instalar el motor web.
ejemplo_alto :-
    limpiar,
    poner(uso, habitual), poner(anio, 1985),
    poner(estructura, madera), poner(informe_madera, desfavorable),
    poner(proteccion_madera, no), poner(electricidad, defectuosa),
    poner(calefaccion, electrica), poner(humedades, no),
    poner(agua, no), poner(estructura_estado, bien),
    poner(desocupacion, no).
