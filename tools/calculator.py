# tools/calculator.py

def run_calculation(
    calculation_type: str,
    inputs: dict
) -> dict:
    """
    Supports: growth_rate, margin, ratio, dcf, cagr
    """
    
    if calculation_type == "growth_rate":
        current = inputs.get("current_value")
        previous = inputs.get("previous_value")
        if previous and previous != 0:
            rate = ((current - previous) / abs(previous)) * 100
            return {
                "calculation": "growth_rate",
                "result": round(rate, 2),
                "unit": "%",
                "formula": "(current - previous) / |previous| × 100"
            }
    
    elif calculation_type == "margin":
        numerator = inputs.get("numerator")
        revenue = inputs.get("revenue")
        if revenue and revenue != 0:
            margin = (numerator / revenue) * 100
            return {
                "calculation": "margin",
                "result": round(margin, 2),
                "unit": "%"
            }
    
    elif calculation_type == "cagr":
        start = inputs.get("start_value")
        end = inputs.get("end_value")
        years = inputs.get("years")
        if all([start, end, years]) and start > 0:
            cagr = ((end / start) ** (1 / years) - 1) * 100
            return {
                "calculation": "cagr",
                "result": round(cagr, 2),
                "unit": "%",
                "formula": "(end/start)^(1/years) - 1"
            }
    
    elif calculation_type == "pe_ratio":
        price = inputs.get("stock_price")
        eps = inputs.get("eps")
        if eps and eps != 0:
            pe = price / eps
            return {
                "calculation": "pe_ratio",
                "result": round(pe, 2),
                "unit": "x"
            }
    
    return {"error": f"Unknown calculation type: {calculation_type}"}