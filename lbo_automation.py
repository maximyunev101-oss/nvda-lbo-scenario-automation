import pandas as pd
import numpy as np

def run_lbo_model(symbol='NVDA', entry_multiple=10.0, scenario='base'):
    # Live Fetched Inputs (FMP API)
    rev_base = 215938.0  # $M
    ebitda_base = 149945.0  # $M
    
    # Model Assumptions
    if scenario == 'downside':
        rev_growth = 0.05
        ebitda_margin = 0.50
        exit_multiple = entry_multiple * 0.9
    else:
        rev_growth = 0.20
        ebitda_margin = 0.55
        exit_multiple = entry_multiple

    ev = ebitda_base * entry_multiple
    senior_debt = ev * 0.50
    sub_debt = ev * 0.15
    equity_entry = ev - (senior_debt + sub_debt)

    waterfall = []
    curr_rev = rev_base
    curr_senior = senior_debt
    curr_sub = sub_debt

    for y in range(1, 6):
        curr_rev *= (1 + rev_growth)
        ebitda = curr_rev * ebitda_margin
        
        senior_interest = curr_senior * 0.07
        sub_interest = curr_sub * 0.10
        ebit = ebitda * 0.85
        taxes = max(0, (ebit - senior_interest - sub_interest) * 0.21)
        capex = ebitda * 0.08
        
        fcf = ebitda - senior_interest - sub_interest - taxes - capex
        senior_paydown = min(curr_senior, max(0, fcf))
        curr_senior -= senior_paydown
        
        sub_paydown = min(curr_sub, max(0, fcf - senior_paydown))
        curr_sub -= sub_paydown
        
        waterfall.append({
            'Year': f'Year {y}',
            'Revenue': round(curr_rev, 1),
            'EBITDA': round(ebitda, 1),
            'FCF': round(fcf, 1),
            'Total_Debt_End': round(curr_senior + curr_sub, 1)
        })

    df = pd.DataFrame(waterfall)
    exit_ebitda = df.iloc[-1]['EBITDA']
    exit_ev = exit_ebitda * exit_multiple
    ending_debt = df.iloc[-1]['Total_Debt_End']
    equity_exit = max(0, exit_ev - ending_debt)
    
    moic = equity_exit / equity_entry if equity_entry > 0 else 0
    irr = ((moic ** (1/5)) - 1) * 100 if moic > 0 else 0

    return df, {'IRR': irr, 'MOIC': moic}

df, metrics = run_lbo_model()
