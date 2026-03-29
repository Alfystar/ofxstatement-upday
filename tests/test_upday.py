import unittest
from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

from ofxstatement_upday.download import get_date_from_user
from ofxstatement_upday.upday import UpDayPlugin, UpDayParser


class TestUpDayPlugin(unittest.TestCase):
    def test_plugin_creation(self):
        """Test che il plugin si crei correttamente"""
        plugin = UpDayPlugin(None, {})
        self.assertIsInstance(plugin, UpDayPlugin)

    def test_get_parser(self):
        """Test che il plugin restituisca il parser corretto"""
        plugin = UpDayPlugin(None, {})
        import tempfile

        with tempfile.NamedTemporaryFile("w+", suffix=".csv", delete=True, encoding="utf-8") as tmp:
            tmp.write("data,ora,descrizione_operazione,tipo_operazione,numero_buoni,valore,luogo_utilizzo,indirizzo,codice_riferimento,pagina_origine\n")
            tmp.flush()

            parser = plugin.get_parser(tmp.name)
            self.assertIsInstance(parser, UpDayParser)


class TestUpDayParser(unittest.TestCase):
    def setUp(self):
        self.parser = UpDayParser(StringIO(""), "UPDAY_TEST")

    def test_parser_initialization(self):
        """Test inizializzazione del parser"""
        self.assertEqual(self.parser.statement.account_id, "UPDAY_TEST")

    @patch('builtins.input')
    def test_get_start_date_from_user(self, mock_input):
        """Test parsing della data utente"""
        valid_date = (date.today() - timedelta(days=30)).strftime('%d/%m/%Y')
        mock_input.return_value = valid_date

        parsed_date = get_date_from_user()

        self.assertEqual(parsed_date, valid_date)

    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_start_date_invalid_then_valid(self, mock_print, mock_input):
        """Test gestione data invalida seguita da data valida"""
        valid_date = (date.today() - timedelta(days=30)).strftime('%d/%m/%Y')
        mock_input.side_effect = ['invalid_date', valid_date]

        parsed_date = get_date_from_user()

        self.assertEqual(parsed_date, valid_date)
        mock_print.assert_called()

    def test_parse_record_usage(self):
        """Test parsing di una riga CSV di utilizzo"""
        line = [
            '01/03/2026',
            '13:05',
            'Utilizzo buoni',
            'usage',
            '2',
            '-16.80',
            'Bar Centrale',
            'Via Roma 1',
            '',
            '1'
        ]

        statement_line = self.parser.parse_record(line)

        self.assertEqual(str(statement_line.amount), '-16.80')
        self.assertEqual(statement_line.trntype, 'PAYMENT')
        self.assertIn('Bar Centrale', statement_line.memo)


if __name__ == '__main__':
    unittest.main()
