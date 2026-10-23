/* Pruebas educativas de las reglas Prolog de ViviendaSeg.
   Ejecutar desde la raiz del repositorio:
   swipl -q -s tests/test_rules.pl -g run_tests -t halt
*/
:- ensure_loaded('../rules.pl').
:- begin_tests(viviendaseg).

base :-
    limpiar,
    forall(member(K-V, [
        uso-habitual, anio-2018, estructura-hormigon,
        electricidad-revisada, calefaccion-electrica, detectores-si,
        humedades-no, agua-no, estructura_estado-bien,
        conservacion-bueno, desocupacion-no, seguridad-ambas,
        inundaciones-no
    ]), poner(K, V)).

test(riesgo_bajo_completo, [setup(base), cleanup(limpiar)]) :-
    evaluacion(ok, bajo, no, [], []).

test(electricidad_sin_revision_es_medio, [setup(base), cleanup(limpiar)]) :-
    poner(electricidad, sin_revision),
    evaluacion(ok, medio, no, Reglas, []),
    memberchk(r06-medio, Reglas).

test(electricidad_defectuosa_es_alto, [setup(base), cleanup(limpiar)]) :-
    poner(electricidad, defectuosa),
    evaluacion(ok, alto, no, Reglas, []),
    memberchk(r03-alto, Reglas).

test(gas_con_fuga_es_alto, [setup(base), cleanup(limpiar)]) :-
    poner(calefaccion, gas),
    poner(caldera, fuga),
    evaluacion(ok, alto, no, Reglas, []),
    memberchk(r04-alto, Reglas).

test(gas_con_mantenimiento_pendiente_es_medio, [setup(base), cleanup(limpiar)]) :-
    poner(calefaccion, gas),
    poner(caldera, pendiente),
    evaluacion(ok, medio, no, Reglas, []),
    memberchk(r07-medio, Reglas).

test(gas_desconocido_es_medio_provisional, [setup(base), cleanup(limpiar)]) :-
    poner(calefaccion, gas),
    evaluacion(ok, medio, si, _, Faltantes),
    memberchk(caldera, Faltantes).

test(madera_con_informe_desfavorable_es_alto, [setup(base), cleanup(limpiar)]) :-
    poner(estructura, madera),
    poner(proteccion_madera, si),
    poner(informe_madera, desfavorable),
    evaluacion(ok, alto, no, Reglas, []),
    memberchk(r01-alto, Reglas).

test(madera_con_informe_favorable_puede_ser_bajo, [setup(base), cleanup(limpiar)]) :-
    poner(estructura, madera),
    poner(proteccion_madera, unknown),
    poner(informe_madera, favorable),
    evaluacion(ok, bajo, no, [], []).

test(madera_sin_documentacion_es_provisional, [setup(base), cleanup(limpiar)]) :-
    poner(estructura, madera),
    poner(proteccion_madera, si),
    poner(informe_madera, sin_informe),
    evaluacion(ok, medio, si, _, Faltantes),
    memberchk(informe_madera, Faltantes).

test(madera_mixta_informe_desfavorable, [setup(base), cleanup(limpiar)]) :-
    poner(estructura, mixta),
    poner(material_mixto, si),
    poner(proteccion_madera, no),
    poner(informe_madera, desfavorable),
    evaluacion(ok, alto, no, Reglas, []),
    memberchk(r02-alto, Reglas).

test(alto_prevalece_sobre_dato_desconocido, [setup(base), cleanup(limpiar)]) :-
    poner(electricidad, defectuosa),
    poner(detectores, unknown),
    evaluacion(ok, alto, no, Reglas, Faltantes),
    memberchk(r03-alto, Reglas),
    memberchk(detectores, Faltantes).

test(anio_antiguo_exige_reforma, [setup(base), cleanup(limpiar)]) :-
    poner(anio, 1980),
    evaluacion(ok, medio, si, [], Faltantes),
    memberchk(reforma, Faltantes).

test(caldera_oculta_no_activa_riesgo, [setup(base), cleanup(limpiar)]) :-
    poner(caldera, fuga),
    evaluacion(ok, bajo, no, [], []).

test(uso_alquilada_se_excluye, [setup(base), cleanup(limpiar)]) :-
    poner(uso, alquilada),
    evaluacion(excluded, null, no, [], []).

test(uso_no_residencial_se_excluye, [setup(base), cleanup(limpiar)]) :-
    poner(uso, no_residencial),
    evaluacion(excluded, null, no, [], []).

test(uso_desconocido_es_incompleto, [setup(base), cleanup(limpiar)]) :-
    poner(uso, unknown),
    evaluacion(incomplete, medio, si, [], [uso]).

:- end_tests(viviendaseg).
