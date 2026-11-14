"""
Startup smoke tests for the Raionn desktop client.

These build the real windows through the real main.MainApp wiring, with only
the network stubbed, and guard the failures that have actually bitten us:

  * a document payload shape that crashed the viewer on open
  * an exception inside a Qt slot silently killing the whole process
  * the PATCH payload quietly erasing a record's chemicals

Run them with:

    cd frontend/app
    pytest tests -v

No server, no MySQL and no Qt window are needed — every window is built
off-screen and every HTTP call is answered by a stub.
"""
import os
import sys
import tempfile
from pathlib import Path

import pytest

# ── Isolation, before anything imports the app ───────────────────────────────
# localDatabase reads SQLITE_URL at import time, so point it at a scratch file
# now; otherwise the suite would write into the developer's real offline cache.
_TEST_DB = Path(tempfile.gettempdir()) / "raionn_smoke_test.db"
os.environ.setdefault("SQLITE_URL", f"sqlite:///{_TEST_DB}")

APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import requests  # noqa: E402


# ── Fixtures: stub the network, then build the app once ──────────────────────

#: Every shape the documents endpoint can hand us.  The first mirrors the live
#: API (DocumentSummaryResponse.Filename serialises to "filename"), the second
#: the offline SQLite cache, the third a row with only a title, the fourth a
#: row with no name at all.  All four must list without raising.
DOCUMENTS = [
    {"id": 7, "title": "Inventory Report",
     "filename": "inventory_20261114_0915.docx",
     "created_at": "2026-11-14T09:15:00"},
    {"id": 8, "title": "Inventory Report",
     "file_name": "inventory_20261112_1402.docx"},
    {"id": 9, "title": "legacy_report.docx"},
    {"id": 10},
]

RECORDS = [{
    "id": 1, "admin_under": "ryuken", "category": "treatment",
    "client_name": "Mandaue Foam", "date": 14, "month": 11, "year": 2026,
    "start_time": "09:00", "end_time": "11:30",
    "start_meridiem": "AM", "end_meridiem": "AM", "remarks": "-",
    "chemicals_use": [
        {"chemical_name": "Solfac", "quantity": "2 L", "remarks": ""}],
    "actual_chemicals_used": [
        {"actual_chemicals_name": "Solfac", "quantity": "1.4 L", "remarks": ""}],
}]


class StubResponse:
    status_code = 200
    text = "{}"
    content = b""
    headers: dict = {}

    def __init__(self, url):
        self._url = url

    def json(self):
        if "/documents" in self._url:
            return DOCUMENTS
        if "/inventory" in self._url:
            return RECORDS
        if "login" in self._url:
            return {"access_token": "test-token", "token_type": "bearer"}
        return {"message": "Code sent to r****n@gmail.com"}


@pytest.fixture(scope="session", autouse=True)
def stub_network():
    """Answer every HTTP call locally and report the app as online."""
    requests.Session.request = lambda self, method, url, *a, **kw: StubResponse(url)
    requests.get = lambda url, *a, **kw: StubResponse(url)
    requests.post = lambda url, *a, **kw: StubResponse(url)

    # Each module imported is_online by value, so patch all three bindings.
    import service.connections.connectionChecker as connection_checker
    import service.connections.syncEngine as sync_engine
    import service.offline.Service.offlineApiService as offline_service

    for module in (connection_checker, sync_engine, offline_service):
        module.is_online = lambda *a, **kw: True

    yield


@pytest.fixture(scope="session")
def qapp(stub_network):
    """One QApplication for the whole session, with modals neutralised."""
    from PyQt5.QtWidgets import QApplication, QMessageBox

    QMessageBox.exec_ = lambda self, *a, **kw: QMessageBox.Ok
    QMessageBox.information = staticmethod(lambda *a, **kw: QMessageBox.Ok)
    QMessageBox.warning = staticmethod(lambda *a, **kw: QMessageBox.Ok)
    QMessageBox.critical = staticmethod(lambda *a, **kw: QMessageBox.Ok)
    QMessageBox.question = staticmethod(lambda *a, **kw: QMessageBox.No)

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture(scope="session")
def manager(qapp):
    """The real MainApp, built exactly as main.py builds it."""
    original_excepthook = sys.excepthook
    import main

    app = main.MainApp()
    app.intro.hide()
    yield app

    # MainApp installs a global crash guard; don't leave it on for other suites.
    sys.excepthook = original_excepthook


# ── Startup ──────────────────────────────────────────────────────────────────

def test_mainapp_constructs_every_window(manager):
    assert manager.intro is not None
    assert manager.login is not None
    assert manager.dashboard is not None
    assert manager.recycle_bin is not None
    assert manager.chem_use_viewer is not None
    assert manager.actual_chem_viewer is not None


# ── Crash guard ──────────────────────────────────────────────────────────────

def test_crash_guard_is_installed(manager):
    """
    Without a custom excepthook PyQt5 calls qFatal() on any exception that
    escapes a slot: the process dies instantly, with no message and no log.
    """
    assert sys.excepthook is not sys.__excepthook__


def test_event_loop_survives_an_exception_in_a_slot(manager, qapp):
    from PyQt5.QtCore import QTimer

    reached_second_timer = []

    def raise_in_slot():
        raise KeyError("file_name")

    def run_after():
        reached_second_timer.append(True)
        qapp.quit()

    QTimer.singleShot(0, raise_in_slot)
    QTimer.singleShot(150, run_after)
    qapp.exec_()

    assert reached_second_timer, "the event loop died with the slot exception"


def test_repeated_faults_prompt_only_once(manager, qapp):
    """A fault in a repeating handler must not stack modal dialogs."""
    from PyQt5.QtCore import QTimer
    from PyQt5.QtWidgets import QMessageBox

    shown = []
    original_exec = QMessageBox.exec_
    QMessageBox.exec_ = lambda self, *a, **kw: (shown.append(1), QMessageBox.Ok)[1]

    main_module = sys.modules["main"]
    main_module.install_crash_guard()          # fresh guard, empty history

    timer = QTimer()
    fired = []

    def repeat():
        fired.append(1)
        if len(fired) > 20:
            timer.stop()
            qapp.quit()
            return
        raise RuntimeError("same fault every time")

    timer.timeout.connect(repeat)
    timer.start(1)
    qapp.exec_()
    QMessageBox.exec_ = original_exec

    assert len(fired) > 10, "the repeating timer stopped early"
    assert len(shown) == 1, f"expected 1 dialog for {len(fired)} faults, got {len(shown)}"


# ── Dashboard ────────────────────────────────────────────────────────────────

def test_dashboard_loads_records(manager):
    manager.dashboard.load_table_data_dashboard()
    assert manager.dashboard.ui.tableListahan.rowCount() == len(RECORDS)


def test_dashboard_switches_category(manager):
    manager.dashboard.switch_mode_category_dashboard("inspection")
    manager.dashboard.switch_mode_category_dashboard("treatment")


def test_dashboard_search_does_not_raise(manager):
    manager.dashboard.ui.searchDate.setText("Mandaue")
    manager.dashboard.handle_search_input_dashboard()
    manager.dashboard.ui.searchDate.setText("")
    manager.dashboard.handle_search_input_dashboard()


# ── Document viewer ──────────────────────────────────────────────────────────

def test_viewer_opens_with_every_document_shape(manager):
    """
    Regression: the live API returns "filename" while the offline cache returns
    "file_name".  Reading only one of them raised KeyError and, with no crash
    guard, closed the whole app.
    """
    manager.dashboard.open_docx_viewer()
    viewer = manager.dashboard._docx_viewer
    assert viewer is not None
    assert viewer.ui.filesList.count() == len(DOCUMENTS)


def test_refresh_file_list_is_idempotent(manager):
    viewer = manager.dashboard._docx_viewer
    viewer.refresh_file_list()
    viewer.refresh_file_list()
    assert viewer.ui.filesList.count() == len(DOCUMENTS)


def test_parser_returns_a_list_for_unreadable_input():
    """It used to fall through and return None, which callers then iterated."""
    from docs_viewer.docs_viewer import DocxViewer

    assert DocxViewer._parse_docx_to_records(b"not a docx file") == []


# ── Authentication ───────────────────────────────────────────────────────────

def test_auth_dialogs_build(manager):
    from login.register_dialog import RegisterDialog
    from login.forgot_password_dialog import ForgotPasswordDialog

    assert RegisterDialog(manager.api).usernameEdit.text() == ""
    assert ForgotPasswordDialog(manager.api).usernameEdit.text() == ""


@pytest.mark.parametrize("message, expected", [
    ("Code sent to r****n@gmail.com", "r****n@gmail.com"),
    ("Code sent to a@b.co.", "a@b.co"),
    ("no address here", ""),
    (None, ""),
])
def test_masked_email_is_extracted(message, expected):
    """The server message already reads 'Code sent to ...'; we show it once."""
    from login.forgot_password_dialog import _extract_email

    assert _extract_email(message) == expected


# ── Inventory update ─────────────────────────────────────────────────────────

class CapturingSession:
    """Records the JSON body instead of sending it."""

    def __init__(self):
        self.sent = None

    def patch(self, url, json=None, timeout=None):
        self.sent = json
        return StubResponse(url)


def test_update_sends_the_keys_the_api_binds():
    """
    PATCH /inventory/{id} binds RecordUpdateRequest.ChemicalUse and
    .ActualChemicalUsed — the SINGULAR keys — and both list items bind
    ChemicalName -> "chemical_name".

    Sending the plural "chemicals_use" / "actual_chemicals_used" does not fail
    loudly: those properties default to an empty list, so the server's
    `if (request.ChemicalUse is not null)` guard still passes and it clears the
    record's chemicals, then returns 200.  Editing a record silently erased
    both chemical lists.
    """
    from service.api.inventory_api_service import InventoryApiService

    session = CapturingSession()
    service = InventoryApiService("http://testing", session)

    # The dict EditRecordDialog._on_save() builds, keys and all.
    service.update_inventory_record(1, {
        "client_name": "Mandaue Foam",
        "chemicals_use": [{"chemical_name": "Solfac", "quantity": "2 L"}],
        "actual_chemicals_used": [
            {"actual_chemicals_name": "Solfac", "quantity": "1.4 L"}],
    })

    sent = session.sent
    assert "chemical_use" in sent, f"wrong outer key: {sorted(sent)}"
    assert "actual_chemical_used" in sent, f"wrong outer key: {sorted(sent)}"
    assert "chemicals_use" not in sent, "plural key would wipe the chemicals"
    assert "actual_chemicals_used" not in sent, "plural key would wipe the chemicals"

    assert len(sent["chemical_use"]) == 1
    assert len(sent["actual_chemical_used"]) == 1
    assert sent["chemical_use"][0]["chemical_name"] == "Solfac"

    actual = sent["actual_chemical_used"][0]
    assert "chemical_name" in actual, f"wrong item key: {sorted(actual)}"
    assert actual["chemical_name"] == "Solfac"
    assert actual["quantity"] == "1.4 L"


def test_edit_dialog_save_survives_a_blank_combo(manager):
    """int() on an empty combo used to raise inside a slot, killing the app."""
    from util.edit_record_dialog_util import EditRecordDialog

    dialog = EditRecordDialog(dict(RECORDS[0]))
    dialog.month_cb.setEditable(True)
    dialog.month_cb.setCurrentText("")
    dialog._on_save()          # must warn and return, not raise


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
