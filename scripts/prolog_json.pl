/* Adaptador JSON para contrastar el motor Prolog con engine.py.
   Entrada stdin: un objeto de hechos normalizados o lista de objetos.
   Ejecucion: swipl -q -s scripts/prolog_json.pl -g main -t halt
   Solo para ensayos locales; la aplicacion web no ejecuta Prolog.
*/
:- use_module(library(http/json)).
:- use_module(library(apply)).
:- ensure_loaded('../rules.pl').

main :-
    catch(
        (json_read_dict(current_input, Entrada),
         (is_list(Entrada) ->
             maplist(evaluar_una, Entrada, Salida)
         ;   evaluar_una(Entrada, Salida)),
         json_write_dict(current_output, Salida, [width(0)]),
         nl),
        Error,
        (print_message(error, Error), halt(1))).

evaluar_una(Datos, Respuesta) :-
    is_dict(Datos),
    limpiar,
    dict_pairs(Datos, _, Pares),
    maplist(cargar_hecho, Pares),
    evaluacion(Estado, Nivel, Prov, Reglas, Faltantes),
    (Prov == si -> Provisional = true ; Provisional = false),
    maplist(regla_a_json, Reglas, ReglasJson),
    Respuesta = _{
        status: Estado,
        level: Nivel,
        provisional: Provisional,
        triggered_rules: ReglasJson,
        missing: Faltantes
    }.

cargar_hecho(Clave-Valor) :-
    (string(Valor) -> atom_string(Atomico, Valor)
    ; integer(Valor) -> Atomico = Valor
    ; throw(error(type_error(valor_normalizado, Valor), _))),
    poner(Clave, Atomico).

regla_a_json(Id-Tier, _{id:IdMayuscula, tier:Tier}) :-
    upcase_atom(Id, IdMayuscula).
