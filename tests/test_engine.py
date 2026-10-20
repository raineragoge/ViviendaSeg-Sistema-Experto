import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import evaluate, visible_questions

BASE = {
    "uso":"habitual","anio":2018,"estructura":"hormigon",
    "electricidad":"revisada","calefaccion":"electrica","detectores":"si",
    "humedades":"no","agua":"no","estructura_estado":"bien",
    "conservacion":"bueno","desocupacion":"no","seguridad":"ambas",
    "inundaciones":"no"
}

class RulesTest(unittest.TestCase):
    def evaluate(self, **kw):
        return evaluate({**BASE, **kw})
    def test_low_complete(self):
        r=self.evaluate()
        self.assertEqual((r['level'],r['provisional']),('bajo',False))
        self.assertEqual(r['missing'],[])
    def test_wood_high(self):
        r=self.evaluate(estructura='madera',proteccion_madera='no',informe_madera='desfavorable')
        self.assertEqual(r['level'],'alto')
        self.assertIn('R01',[x['id'] for x in r['triggered_rules']])
    def test_mix_conditional(self):
        r=self.evaluate(estructura='mixta',material_mixto='si',proteccion_madera='no',informe_madera='desfavorable')
        self.assertEqual(r['level'],'alto')
        self.assertIn('R02',[x['id'] for x in r['triggered_rules']])
    def test_mix_unknown(self):
        r=self.evaluate(estructura='mixta',material_mixto='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
    def test_gas_leak_urgent(self):
        r=self.evaluate(calefaccion='gas',caldera='fuga')
        self.assertEqual(r['level'],'alto')
        self.assertTrue(r['urgent'])
    def test_gas_pending_medium(self):
        r=self.evaluate(calefaccion='gas',caldera='pendiente')
        self.assertEqual((r['level'],r['provisional']),('medio',False))
        self.assertIn('R07',[x['id'] for x in r['triggered_rules']])
    def test_combustion_smoke_rule(self):
        r=self.evaluate(calefaccion='combustion',chimenea='al_dia',detectores='no')
        self.assertIn('R09',[x['id'] for x in r['triggered_rules']])
    def test_active_water_medium(self):
        self.assertEqual(self.evaluate(agua='si')['level'],'medio')
    def test_occupancy_medium(self):
        r=self.evaluate(desocupacion='si',seguridad='ninguna')
        self.assertIn('R13',[x['id'] for x in r['triggered_rules']])
        self.assertIn('R14',[x['id'] for x in r['triggered_rules']])
    def test_older_year_not_automatically_high(self):
        r=self.evaluate(anio=1985,reforma='no')
        self.assertEqual(r['level'],'bajo')
    def test_unknown_provisional(self):
        r=self.evaluate(electricidad='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        self.assertEqual(r['missing'][0]['id'],'electricidad')
    def test_high_kept_with_unknown(self):
        r=self.evaluate(estructura='madera',proteccion_madera='si',informe_madera='desfavorable',electricidad='unknown')
        self.assertEqual((r['level'],r['provisional']),('alto',False))
        self.assertTrue(r['missing'])
    def test_medium_kept_provisional_with_unknown(self):
        r=self.evaluate(agua='si',anio='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
    def test_hidden_branch_ignored(self):
        r=self.evaluate(calefaccion='electrica',caldera='fuga')
        self.assertEqual(r['level'],'bajo')
        self.assertNotIn('R04',[x['id'] for x in r['triggered_rules']])
    def test_branch_gas_required(self):
        r=self.evaluate(calefaccion='gas')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        self.assertIn('caldera',[x['id'] for x in r['missing']])
    def test_branch_reform_appears(self):
        self.assertIn('reforma',[x['id'] for x in visible_questions({'anio':1985})])
        self.assertNotIn('reforma',[x['id'] for x in visible_questions({'anio':2018})])
    def test_excluded_rental(self):
        r=self.evaluate(uso='alquilada')
        self.assertEqual((r['status'],r['level']),('excluded',None))
    def test_excluded_office(self):
        self.assertEqual(self.evaluate(uso='no_residencial')['status'],'excluded')
    def test_invalid_option_rejected(self):
        with self.assertRaises(ValueError): self.evaluate(estructura='diamante')
    def test_invalid_year_rejected(self):
        with self.assertRaises(ValueError): self.evaluate(anio=2090)
    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError): self.evaluate(no_existe='foo')
    def test_no_structural_assumption_from_code_year(self):
        self.assertEqual(self.evaluate(anio=2024,estructura='madera',proteccion_madera='si',informe_madera='favorable')['level'],'bajo')
    def test_flood_medium(self):
        self.assertEqual(self.evaluate(inundaciones='si')['level'],'medio')
    def test_grave_structural_urgent(self):
        r=self.evaluate(estructura_estado='graves')
        self.assertEqual(r['level'],'alto')
        self.assertTrue(r['urgent'])
    def test_condition_unknown_older(self):
        r=self.evaluate(anio=1980,reforma='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        # Toda respuesta desconocida se registra como información pendiente
    def test_unknown_detector_yields_provisional(self):
        r=self.evaluate(detectores='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
    def test_unknown_material_but_good_everything_else(self):
        r=self.evaluate(estructura='unknown')
        self.assertEqual((r['level'],r['provisional']),('medio',True))


    def test_wood_without_report_is_provisional(self):
        r=self.evaluate(estructura='madera',proteccion_madera='si',informe_madera='sin_informe')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        self.assertIn('informe_madera',[x['id'] for x in r['missing']])
        self.assertNotIn('R01',[x['id'] for x in r['triggered_rules']])

    def test_wood_completely_unknown_is_provisional(self):
        r=self.evaluate(estructura='madera')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        self.assertEqual({x['id'] for x in r['missing']},{'proteccion_madera','informe_madera'})

    def test_wood_documented_positive_allows_low(self):
        r=self.evaluate(estructura='madera',proteccion_madera='si',informe_madera='favorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))

    def test_exposed_wood_favorable_report_not_automatically_risky(self):
        r=self.evaluate(estructura='madera',proteccion_madera='no',informe_madera='favorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))
        self.assertNotIn('R16',[x['id'] for x in r['triggered_rules']])

    def test_known_unprotected_no_report_precaution(self):
        r=self.evaluate(estructura='madera',proteccion_madera='no',informe_madera='sin_informe')
        self.assertEqual((r['level'],r['provisional']),('medio',True))
        self.assertIn('R16',[x['id'] for x in r['triggered_rules']])

    def test_report_negative_high_regardless_protections(self):
        r=self.evaluate(estructura='madera',proteccion_madera='si',informe_madera='desfavorable')
        self.assertEqual((r['level'],r['provisional']),('alto',False))
        self.assertIn('R01',[x['id'] for x in r['triggered_rules']])

    def test_favorable_report_unknown_protection_does_not_block_low(self):
        r=self.evaluate(estructura='madera',proteccion_madera='unknown',informe_madera='favorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))
        self.assertNotIn('proteccion_madera',[x['id'] for x in r['missing']])

    def test_mixed_wood_favorable_allows_low(self):
        r=self.evaluate(estructura='mixta',material_mixto='si',proteccion_madera='si',informe_madera='favorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))

    def test_mixed_without_wood_skips_wood_followups(self):
        q={x['id'] for x in visible_questions({'estructura':'mixta','material_mixto':'no'})}
        self.assertNotIn('proteccion_madera',q)
        self.assertNotIn('informe_madera',q)
        r=self.evaluate(estructura='mixta',material_mixto='no',informe_madera='desfavorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))
        self.assertNotIn('R02',[x['id'] for x in r['triggered_rules']])

    def test_wood_followups_are_visible(self):
        for attrs in [{'estructura':'madera'},{'estructura':'mixta','material_mixto':'si'}]:
            q={x['id'] for x in visible_questions(attrs)}
            self.assertIn('proteccion_madera',q)
            self.assertIn('informe_madera',q)

    def test_wood_other_high_still_overrides(self):
        r=self.evaluate(estructura='madera',proteccion_madera='si',informe_madera='sin_informe',electricidad='defectuosa')
        self.assertEqual((r['level'],r['provisional']),('alto',False))
        self.assertIn('informe_madera',[x['id'] for x in r['missing']])

    def test_wood_question_answers_ignored_when_non_wood(self):
        r=self.evaluate(estructura='hormigon',proteccion_madera='no',informe_madera='desfavorable')
        self.assertEqual((r['level'],r['provisional']),('bajo',False))

    def test_knowledge_and_prolog_rule_ids_agree(self):
        import re
        from engine import KB
        src=(Path(__file__).resolve().parents[1]/'rules.pl').read_text()
        prolog_ids=set(re.findall(r'regla\((r\d+),\s*(?:alto|medio)\)',src))
        kb_ids={r['id'].lower() for r in KB['rules']}
        self.assertEqual(prolog_ids,kb_ids)

if __name__=='__main__':unittest.main()
