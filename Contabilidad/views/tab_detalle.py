"""
views/tab_detalle.py – Tab "Detalle completo".
"""
import pandas as pd
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped


def render(dff: pd.DataFrame) -> None:
    st.subheader("Datos completos")

    det = dff.copy()
    det["Fecha"] = det["Fecha"].dt.strftime("%d/%m/%Y")

    per_det = st.selectbox(
        "Filtrar empleado (detalle)",
        ["Todos"] + sorted(dff["Nombre"].unique()),
        key="sel_det",
    )
    if per_det != "Todos":
        det = det[det["Nombre"] == per_det]

    det_sorted = det.sort_values(["Nombre", "Fecha"]).reset_index(drop=True)
    _num_det = [c for c in det_sorted.columns if det_sorted[c].dtype.kind in ("f", "i") and c != "Fecha"]
    _fmt_det = {c: "{:.2f}" for c in _num_det}

    if per_det != "Todos":
        st.markdown(f"#### {per_det}")
        st.dataframe(
            det_sorted.drop(columns=["Nombre"]).style.format(_fmt_det),
            use_container_width=True, height=500,
        )
    else:
        st.dataframe(det_sorted.style.format(_fmt_det), use_container_width=True, height=500)

    xlsx_det = df_to_excel_grouped(det_sorted, "Detalle completo")
    st.download_button(
        label="Descargar Excel",
        icon=":material/download:",
        data=xlsx_det,
        file_name="reporte_labor_detalle.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
