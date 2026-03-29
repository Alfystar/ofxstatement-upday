from unittest.mock import MagicMock

import pytest

from ofxstatement_upday import download


def test_sanitize_filename_normalizes_name():
    assert download.sanitize_filename("estrazione settembre?.csv") == "estrazione_settembre.csv"


def test_setup_browser_uses_selenium_manager(monkeypatch):
    fake_driver = MagicMock()
    fake_chrome = MagicMock(return_value=fake_driver)
    monkeypatch.setattr(download.webdriver, "Chrome", fake_chrome)

    driver = download.setup_browser()

    assert driver is fake_driver
    fake_chrome.assert_called_once()
    assert "options" in fake_chrome.call_args.kwargs
    fake_driver.execute_script.assert_called_once_with(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    fake_driver.implicitly_wait.assert_called_once_with(10)


def test_setup_browser_reports_selenium_manager_failure(monkeypatch):
    monkeypatch.setattr(download.webdriver, "Chrome", MagicMock(side_effect=Exception("boom")))

    captured = {}

    def fake_handle_fatal_error(driver, error_message, exception=None):
        captured["driver"] = driver
        captured["error_message"] = error_message
        captured["exception"] = exception
        raise RuntimeError("fatal")

    monkeypatch.setattr(download, "_handle_fatal_error", fake_handle_fatal_error)

    with pytest.raises(RuntimeError, match="fatal"):
        download.setup_browser()

    assert captured["driver"] is None
    assert "Selenium Manager" in captured["error_message"]
    assert "Chrome" in captured["error_message"]
    assert str(captured["exception"]) == "Avvio di Chrome fallito con Selenium Manager"

