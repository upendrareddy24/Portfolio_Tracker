ACCOUNTS = [
    {
        "id": 1, 
        "name": "SH Swings", 
        "strategy": "SH Swing", 
        "holding_period": "1-5 Days", 
        "color": "text-blue-400",
        "description": "Short-term swings targeting immediate momentum.",
        "logic_summary": "Logic: Reclaim of EMA9/EMA21 with Volume > 1.5x Avg. Must not be extended. Score >= 70."
    },
    {
        "id": 2, 
        "name": "Swing/Sq", 
        "strategy": "Swing/Sq", 
        "holding_period": "2-20 Days", 
        "color": "text-green-400",
        "description": "Trend following pullbacks to moving averages.",
        "logic_summary": "Logic: Pullback to EMA21/SMA50 in uptrend. Score >= 60. Clean trend alignment."
    },
    {
        "id": 3, 
        "name": "POS BO/SQ", 
        "strategy": "POS- BO/SQ", 
        "holding_period": "20-60 Days", 
        "color": "text-purple-400",
        "description": "Position trading breakouts from sound bases.",
        "logic_summary": "Logic: Breakout above Pivot with Vol > 1.4x. Pattern: Cup/Flat Base. O'Neil rules."
    },
    {
        "id": 4, 
        "name": "POS HVOL", 
        "strategy": "POS-HVOL", 
        "holding_period": "5-20 Days", 
        "color": "text-yellow-400",
        "description": "High volume setups showing institutional footprint.",
        "logic_summary": "Logic: Score >= 65 + Volume > 2x Avg. Buying on tight pullback after demand day."
    },
    {
        "id": 5, 
        "name": "POS PAT", 
        "strategy": "POS-PAT", 
        "holding_period": "10-40 Days", 
        "color": "text-pink-400",
        "description": "Classical chart patterns.",
        "logic_summary": "Logic: Pattern (Cup, Flag, Triangle) with Confidence > 60%. Score >= 70."
    },
    {
        "id": 6, 
        "name": "INV", 
        "strategy": "INV", 
        "holding_period": "3M - 2Y", 
        "color": "text-indigo-400",
        "description": "Long term investment leaders.",
        "logic_summary": "Logic: Long term uptrend (Price > SMA200). Rising RS. Buying pullbacks."
    },
    {
        "id": 7, 
        "name": "OPT Swing", 
        "strategy": "OPT-Swing", 
        "holding_period": "3-20 Days", 
        "color": "text-orange-400",
        "description": "Options-specific swing setups.",
        "logic_summary": "Logic: Grade B+ or higher. Liquid Options (Spread <= 5%, OI >= 1000). Not Earnings."
    },
    {
        "id": 8, 
        "name": "Lottery", 
        "strategy": "Lot", 
        "holding_period": "1-5 Days", 
        "color": "text-red-400",
        "description": "High risk, high reward speculative plays.",
        "logic_summary": "Logic: Unusual Options Activity + Momentum Trigger. Speculative. No Earnings risk."
    },
    {
        "id": 9, 
        "name": "Reference", 
        "strategy": "Reference", 
        "holding_period": "N/A", 
        "color": "text-gray-400", 
        "description": "Market Indices",
        "logic_summary": "Market Context."
    }
]

def get_account_by_id(account_id: int):
    for account in ACCOUNTS:
        if account["id"] == account_id:
            return account
    return ACCOUNTS[0]
