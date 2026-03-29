import tempfile

from ofxstatement_upday.upday import UpDayPlugin


def test_sample() -> None:
    plugin = UpDayPlugin(None, {})

    sample_content = """data,ora,descrizione_operazione,tipo_operazione,numero_buoni,valore,luogo_utilizzo,indirizzo,codice_riferimento,pagina_origine
01/03/2026,13:05,Utilizzo buoni,usage,2,-16.80,Bar Centrale,Via Roma 1,,1
"""

    with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=True, encoding="utf-8") as handle:
        handle.write(sample_content)
        handle.flush()

        parser = plugin.get_parser(handle.name)
        statement = parser.parse()

        assert statement is not None
        assert len(statement.lines) == 1
        assert statement.lines[0].trntype == "PAYMENT"
