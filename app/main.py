from PyQt5.QtWidgets import QApplication, QMessageBox
from service.api.api_service import ApiService
from service.offline.Service.offlineApiService import OfflineCapableApiService  # ← NEW
from service.offline.Database.localDatabase import init_db                       # ← NEW
from util.toolfix_util import install_custom_tooltips
from ui import theme
import sys
import os
import traceback
from datetime import datetime

from intro.intro import IntroWindow
from login.login import LoginWindow
from dashboard.dashboard import DashboardWindow
from service.connections.syncEngine import SyncManager
from recycle.recycle_bin import RecyclBinWindow
from dashboard.viewer.actual_chemical_viewer import ActualChemViewerWindow
from dashboard.viewer.chemical_used_viewer import ChemUseViewerWindow


LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error.log")


def install_crash_guard():
    """
    Keep one bad code path from taking the whole app down.

    PyQt5 calls qFatal() when a Python exception escapes a slot — the process
    dies on the spot, with no message and no chance to save.  Installing our own
    sys.excepthook means Qt hands the exception here instead: we log it, tell
    the user, and the event loop carries on.
    """
    reported = set()          # error signatures already shown to the user

    def handle(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return

        detail = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        print(detail, file=sys.stderr)
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as log:
                log.write(f"\n===== {datetime.now():%Y-%m-%d %H:%M:%S} =====\n{detail}")
        except Exception:
            pass

        # Always log, but only ever show one dialog per distinct error: a fault
        # inside a repeating handler (paint, timer) would otherwise stack modal
        # dialogs faster than they can be dismissed.
        signature = (exc_type.__name__, str(exc_value),
                     tuple(traceback.extract_tb(exc_tb).format()[-3:]))
        if signature in reported or len(reported) >= 12:
            return
        reported.add(signature)

        try:
            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle("Something went wrong")
            box.setText("The last action could not be completed.")
            box.setInformativeText(
                "The system is still running — you can keep working or try again.\n"
                f"Details were saved to:\n{LOG_PATH}"
            )
            box.setDetailedText(detail)
            box.setStandardButtons(QMessageBox.Ok)
            box.exec_()
        except Exception:
            pass          # never let the handler itself raise

    sys.excepthook = handle


class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        install_crash_guard()
        theme.install(self.app)
        install_custom_tooltips(self.app)

        # ── Init SQLite tables (creates local_database.db if not exists) ──────
        init_db()

        # ── Wrap ApiService with offline capability ───────────────────────────
        _online_api  = ApiService()                        # real MySQL/FastAPI
        self.api     = OfflineCapableApiService(_online_api)  # offline-aware wrapper
        self.sync_manager = SyncManager(_online_api)       # uses real api for syncing

        self.intro     = IntroWindow(self.sync_manager, self.api)
        self.login     = LoginWindow(self.api)
        self.dashboard = DashboardWindow(self.api)
        self.recycle_bin = RecyclBinWindow(
            self.api,
            self.dashboard.load_table_data_dashboard,
            parent=self.dashboard
        )

        self.actual_chem_viewer = ActualChemViewerWindow()
        self.chem_use_viewer    = ChemUseViewerWindow()

        self._bind_viewer(
            viewer=self.chem_use_viewer,
            dashboard_table=self.dashboard.ui.chemicalUsed
        )
        self._bind_viewer(
            viewer=self.actual_chem_viewer,
            dashboard_table=self.dashboard.ui.actualchemicalUsed
        )

        self.intro.intro_service.finished.connect(self.show_login)
        self.login.login_success.connect(self.show_dashboard)
        self.dashboard.ui.recycle_bin.clicked.connect(self.recycle_bin.show)
        self.dashboard.ui.ViewChem.clicked.connect(self.chem_use_viewer.show)
        self.dashboard.ui.ViewActChem.clicked.connect(self.actual_chem_viewer.show)

        self.dashboard.ui.actionPDF_STORAGE.triggered.connect(
            self.dashboard.open_docx_viewer)
        self.dashboard.ui.actionPDF_STORAGE_3.clicked.connect(
            self.dashboard.open_docx_viewer)

        self.intro.show()

        self.dashboard.logged_out.connect(self.return_to_login)
        self.dashboard.record_saved.connect(self._on_record_saved)

    def _bind_viewer(self, viewer, dashboard_table):
        viewer.data_changed.connect(
            lambda data: self.dashboard.update_table_inputs_dashboard(
                dashboard_table, data)
        )

    def _sync_table_to_viewer(self, source_table, viewer):
        data = []
        for row in range(source_table.rowCount()):
            name    = source_table.item(row, 0).text().strip() if source_table.item(row, 0) else ""
            qty     = source_table.item(row, 1).text().strip() if source_table.item(row, 1) else ""
            remarks = source_table.item(row, 2).text().strip() if source_table.item(row, 2) else ""
            if name or qty or remarks:
                data.append({"name": name, "qty": qty, "remarks": remarks})
        viewer.load_data(data)

    def show_login(self):
        self.intro.close()
        # Sync any offline records now that we know connectivity status
        if self.api.check_connection_service():
            ok, msg = self.sync_manager.sync_pending_records()
            print(f"[Sync on startup] {msg}")
        self.login.show()

    def show_dashboard(self):
        self.login.close()
        # Sync after login while token is fresh
        if self.api.check_connection_service():
            ok, msg = self.sync_manager.sync_pending_records()
            print(f"[Sync after login] {msg}")
        self.dashboard.load_table_data_dashboard()
        self.dashboard.show()

    def return_to_login(self):
        self.dashboard.hide()
        self.dashboard.clear_inputs_dashboard()
        self.dashboard.table_renderer.clear()
        self.api.logout_service()
        self.login.ui.usernameEdit.clear()
        self.login.ui.passwordEdit.clear()
        self.login.show()

    def _on_record_saved(self):
        self.chem_use_viewer.clear_table()
        self.actual_chem_viewer.clear_table()


if __name__ == "__main__":
    try:
        manager = MainApp()
    except Exception:
        # Startup failed before the event loop existed — report, don't vanish.
        detail = traceback.format_exc()
        print(detail, file=sys.stderr)
        try:
            with open(LOG_PATH, "a", encoding="utf-8") as log:
                log.write(f"\n===== STARTUP {datetime.now():%Y-%m-%d %H:%M:%S} =====\n{detail}")
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(
                None, "Raionn could not start",
                f"The system failed to start.\n\nDetails were saved to:\n{LOG_PATH}\n\n{detail}"
            )
        except Exception:
            pass
        sys.exit(1)

    sys.exit(manager.app.exec_())