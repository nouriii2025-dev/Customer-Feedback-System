"""Keeps ONE shared Excel analysis sheet up to date.

The workbook at settings.FEEDBACK_ANALYSIS_XLSX is created on first export and
re-used afterwards: only the "Feedback" sheet is refreshed. Any other sheets,
charts or notes the team adds to the file are left untouched.
"""
import os
import threading
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HEADERS = ["ID", "Submitted", "Customer", "Company", "Email",
            "Quality Rating (1-5)",
            "Timely Delivery Rating (1-5)",
            "Communication Rating (1-5)",
           "Rating (1-5)", "Would recommend", "Feedback"]
WIDTHS = [7, 18, 24, 24, 30, 20, 24, 26, 13, 17, 70]
LAST_ROW = 100000
_lock = threading.Lock()


class WorkbookLocked(Exception):
    """The file is open in Excel (or otherwise locked) and cannot be replaced."""


def analysis_path() -> Path:
    return Path(settings.FEEDBACK_ANALYSIS_XLSX)


def _fill_feedback_sheet(ws, rows):
    ws.delete_rows(1, ws.max_row + 1)
    ws.append(HEADERS)
    head_fill = PatternFill("solid", fgColor="14202B")
    thin = Side(style="thin", color="E3E8ED")
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
        c.fill = head_fill
        c.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 24

    for f in rows:
        ws.append([
            f.id,
            timezone.localtime(f.created_at).replace(tzinfo=None),
            f.customer_name, f.company, f.email,
            f.quality_rating,
            f.timely_delivery_rating,
            f.communication_rating,
            f.rating, f.get_recommend_display(), f.comments,
        ])
    for r in ws.iter_rows(min_row=2):
        for c in r:
            c.font = Font(name="Calibri", size=11)
            c.border = Border(bottom=thin)
            c.alignment = Alignment(vertical="top", wrap_text=(c.column == 8))
        r[1].number_format = "yyyy-mm-dd hh:mm"
        r[5].alignment = Alignment(horizontal="center", vertical="top")

    for i, w in enumerate(WIDTHS, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{max(ws.max_row, 2)}"


def _ensure_summary(wb):
    if "Summary" in wb.sheetnames:
        return wb["Summary"]
    ws = wb.create_sheet("Summary")
    rng = lambda col: f"Feedback!{col}2:{col}{LAST_ROW}"
    ws["A1"], ws["A1"].font = "Feedback summary", Font(bold=True, size=14, name="Calibri")
    rows = [
        ("Total responses", f"=COUNTA({rng('A')})"),
        ("Average rating", f"=IFERROR(ROUND(AVERAGE({rng('F')}),2),0)"),
        ("Would recommend", f'=IFERROR(COUNTIF({rng("G")},"Yes")/COUNTA({rng("A")}),0)'),
        (None, None),
        *[(f"{n}-star ratings", f"=COUNTIF({rng('F')},{n})") for n in (5, 4, 3, 2, 1)],
    ]
    for i, (label, formula) in enumerate(rows, start=3):
        if label:
            ws.cell(i, 1, label)
            ws.cell(i, 2, formula)
    ws["B5"].number_format = "0%"
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["B"].width = 20
    return ws


def sync_workbook(queryset):
    """Rewrite the Feedback sheet in the shared workbook. Returns (path, row_count)."""
    path = analysis_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(queryset.order_by("created_at"))

    with _lock:
        if path.exists():
            wb = load_workbook(path)
        else:
            wb = Workbook()
            wb.active.title = "Feedback"
        ws = wb["Feedback"] if "Feedback" in wb.sheetnames else wb.create_sheet("Feedback", 0)
        _fill_feedback_sheet(ws, rows)
        summary = _ensure_summary(wb)
        summary["A14"], summary["B14"] = "Last updated", timezone.localtime().strftime("%Y-%m-%d %H:%M")

        tmp = path.with_name(path.stem + ".tmp.xlsx")
        wb.save(tmp)
        try:
            os.replace(tmp, path)
        except PermissionError as exc:
            tmp.unlink(missing_ok=True)
            raise WorkbookLocked from exc
    return path, len(rows)
