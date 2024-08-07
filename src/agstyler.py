# src/agstyler.py

from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

def get_numeric_style_with_precision(precision: int) -> dict:
    return {"type": ["numericColumn", "customNumericFormat"], "precision": precision}

PRECISION_ZERO = get_numeric_style_with_precision(0)
PINLEFT = {"pinned": "left"}

css = {
    ".center-header .ag-header-cell-label": {"justify-content": "center", "display": "flex"},
    ".ag-header-cell": {"text-align": "center"},
    ".ag-cell": {"text-align": "center"}
}

def draw_grid(
        df,
        max_height,
        formatter: dict = None,
        selection="multiple",
        use_checkbox=False,
        fit_columns=False,
        theme="streamlit",
        wrap_text: bool = False,
        auto_height: bool = False,
        grid_options: dict = None,
        key=None,
        css=css
):

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        filterable=True,
        groupable=False,
        editable=False,
        wrapText=True,
        autoHeight=True,
        headerClass='center-header',  # Center the header text
        cellStyle={"textAlign": "center", "whiteSpace": "normal"}  # Center the cell text and allow wrap text
    )

    if grid_options is not None:
        gb.configure_grid_options(**grid_options)

    if formatter:
        for latin_name, (cyr_name, style_dict) in formatter.items():
            gb.configure_column(latin_name, header_name=cyr_name, **style_dict)

    gb.configure_column("patient_details", cellStyle={"textAlign": "center", "whiteSpace": "normal"})  # Center-align and wrap text for patient_details
    gb.configure_selection(selection_mode=selection, use_checkbox=use_checkbox)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination configuration

    return AgGrid(
        df,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=fit_columns,
        height=min(max_height, (1 + len(df.index)) * 29),
        theme=theme,
        key=key,
        custom_css=css
    )

def highlight(color, condition):
    code = f"""
        function(params) {{
            if ({condition}) {{
                return {{
                    'backgroundColor': '{color}'
                }};
            }}
            return null;
        }};
    """
    return JsCode(code)
