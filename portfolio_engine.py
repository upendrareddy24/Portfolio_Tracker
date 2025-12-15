from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import datetime
import math

# -------------------------------------------------------------------------
# 0) Data Contracts
# -------------------------------------------------------------------------

@dataclass
class TickerData:
    symbol: str
    price: float
    high: float
    low: float
    open: float
    close: float
    prevClose: float
    changePct: float
    volume: float
    avgVol20: float
    avgVol50: float
    sma50: float
    sma200: float
    ema9: float
    ema21: float
    rsTrend: str  # "rising" | "flat" | "falling"
    recentHigh20: float
    recentLow20: float
    daysToEarnings: Optional[int] = None
    earningsMoveFlag: bool = False
    gapPctToday: float = 0.0
    gapPctPrevDay: float = 0.0
    candlesDaily: List[dict] = field(default_factory=list)

@dataclass
class OptionsSnapshot:
    hasOptions: bool = False
    spreadPct: float = 0.0
    openInterest: int = 0
    totalVolume: int = 0

@dataclass
class PatternResult:
    name: str = "None"
    confidence: float = 0.0
    pivotPrice: Optional[float] = None
    notes: str = ""

@dataclass
class SetupDecision:
    accountId: int
    ticker: str
    grade: str
    score: int
    entryPlan: List[str]
    stopPlan: List[str]
    exitPlan: List[str]
    tags: List[str]
    pattern: PatternResult
    reasons: List[str]
    price: float
    changePct: float


# -------------------------------------------------------------------------
# 1) Global Constants
# -------------------------------------------------------------------------
EARNINGS_DAYS_BLOCK_SHORT = 7
EARNINGS_DAYS_BLOCK_OPTIONS = 10
EXTENDED_FROM_SMA50_WARN = 0.20
EXTENDED_FROM_EMA21_WARN = 0.15
OPT_MIN_GRADE_SCORE = 70
OPT_MAX_SPREAD_PCT = 0.05
OPT_MIN_OI = 1000

# -------------------------------------------------------------------------
# 2) Helper Functions
# -------------------------------------------------------------------------

def is_earnings_noise(td: TickerData) -> bool:
    if td.earningsMoveFlag:
        return True
    if td.daysToEarnings and td.daysToEarnings <= 3 and abs(td.gapPctToday) >= 0.06:
        return True
    # Simplified check for previous day gap
    if abs(td.gapPctPrevDay) >= 0.08: 
        return True
    return False

def earnings_penalty(td: TickerData) -> int:
    if not is_earnings_noise(td):
        return 0
    penalty = 12
    if td.daysToEarnings and td.daysToEarnings <= 3:
        penalty += 6
    if abs(td.gapPctToday) >= 0.10:
        penalty += 6
    return penalty

def trend_score(td: TickerData) -> int:
    s = 0
    if td.price > td.sma50: s += 8 
    else: s -= 8
    
    if td.price > td.sma200: s += 10 
    else: s -= 10
    
    if td.sma50 > td.sma200: s += 10 
    else: s -= 10
    
    if td.ema9 > td.ema21: s += 5
    
    return max(-25, min(25, s))

def rs_score(td: TickerData) -> int:
    if td.rsTrend == "rising": return 12
    if td.rsTrend == "flat": return 4
    return -10

def volume_score(td: TickerData) -> int:
    # Simplified volume analysis since we might not have full history in this iteration
    s = 0
    if td.volume >= 1.5 * td.avgVol20: s += 8
    
    # Placeholder for detailed up/down volume analysis
    # Assuming slight bullish bias if price is up
    if td.changePct > 0: s += 7
    else: s -= 5
    
    return max(-15, min(15, s))

def extended_penalty(td: TickerData) -> int:
    p = 0
    if td.sma50 > 0:
        dist50 = (td.price - td.sma50) / td.sma50
        if dist50 >= EXTENDED_FROM_SMA50_WARN: p += 10
        
    if td.ema21 > 0:
        dist21 = (td.price - td.ema21) / td.ema21
        if dist21 >= EXTENDED_FROM_EMA21_WARN: p += 8
        
    today_range_pct = (td.high - td.low) / td.low if td.low > 0 else 0
    if today_range_pct >= 0.07 and td.volume >= 2.0 * td.avgVol20:
        p += 6
        
    return p

def detect_pattern(td: TickerData) -> PatternResult:
    # Simplified pattern detection hooks
    # In a real engine, this would analyze candlesDaily
    
    pr = PatternResult()
    
    # Simple proxies for patterns
    if td.price > td.recentHigh20 and td.volume > td.avgVol20:
        pr.name = "Breakout"
        pr.confidence = 0.70
        pr.pivotPrice = td.recentHigh20
    
    elif td.price > td.sma50 and abs(td.price - td.sma50) / td.sma50 < 0.03:
        pr.name = "Support Bounce"
        pr.confidence = 0.60
        pr.pivotPrice = td.sma50
        
    return pr

def options_liquidity_tag(opt: OptionsSnapshot) -> Tuple[bool, List[str]]:
    tags = []
    if not opt.hasOptions:
        return False, ["NoOptions"]
    
    if opt.spreadPct <= OPT_MAX_SPREAD_PCT: tags.append("TightSpread")
    else: tags.append("WideSpread")
    
    if opt.openInterest >= OPT_MIN_OI: tags.append("GoodOI")
    else: tags.append("LowOI")
    
    good = (opt.spreadPct <= OPT_MAX_SPREAD_PCT) and (opt.openInterest >= OPT_MIN_OI)
    return good, tags

# -------------------------------------------------------------------------
# 3) Scoring Engine
# -------------------------------------------------------------------------

def compute_score(td: TickerData, opt: OptionsSnapshot, pattern: PatternResult) -> Tuple[int, List[str], List[str]]:
    tags = []
    reasons = []
    
    base = 60
    
    t = trend_score(td)
    r = rs_score(td)
    v = volume_score(td)
    
    base += (t + r + v)
    
    if pattern.name != "None":
        base += round(8 * pattern.confidence)
        reasons.append(f"Pattern: {pattern.name}")
        
    # Penalties
    ep = extended_penalty(td)
    if ep > 0:
        base -= ep
        tags.append("Extended/Climactic")
        reasons.append(f"Extended penalty: -{ep}")
        
    earnP = earnings_penalty(td)
    if earnP > 0:
        base -= earnP
        tags.append("EarningsNoise")
        reasons.append(f"Earnings noise penalty: -{earnP}")
        
    reasons.append(f"RS: {td.rsTrend}")
    
    optGood, optTags = options_liquidity_tag(opt)
    tags.extend(optTags)
    if optGood:
        tags.append("OptionsOK")
        
    score = max(0, min(100, int(base)))
    
    # Add score breakdown to reasons for visibility
    reasons.append(f"Trend:{t} RS:{r} Vol:{v}")
    
    return score, tags, reasons

def grade_from_score(score: int) -> str:
    if score >= 90: return "A+"
    if score >= 80: return "A"
    if score >= 70: return "B+"
    if score >= 60: return "B"
    if score >= 50: return "C"
    return "D"

# -------------------------------------------------------------------------
# 5) Account Assignmnet
# -------------------------------------------------------------------------
def assign_account(td: TickerData, opt: OptionsSnapshot, score: int, tags: List[str], pattern: PatternResult) -> int:
    
    # Check "Avoid" conditions first? 
    # Logic based on user pseudo-code
    
    near_earnings = False
    if td.daysToEarnings is not None and td.daysToEarnings <= EARNINGS_DAYS_BLOCK_SHORT:
        near_earnings = True
        
    optGood, _ = options_liquidity_tag(opt)
    
    # 1) Options Swing (Account 7)
    if optGood and score >= OPT_MIN_GRADE_SCORE and "EarningsNoise" not in tags:
        if "Extended/Climactic" not in tags:
            return 7
            
    # 2) Short Swing (Account 1)
    # Trigger: reclaim EMA9/21
    is_short_swing = td.close > td.ema9 and td.close > td.ema21 
    if score >= 70 and not near_earnings and is_short_swing:
        return 1
        
    # 3) Swing/SQ (Account 2)
    # Trigger: Pullback
    is_swing = td.close > td.sma50
    if score >= 60 and not near_earnings and is_swing:
        return 2
        
    # 4) POS Breakout (Account 3)
    if score >= 70 and pattern.name == "Breakout":
        return 3
        
    # 5) POS High Vol (Account 4)
    if score >= 65 and td.volume > 2 * td.avgVol20:
        return 4
        
    # 6) POS Pattern (Account 5)
    if score >= 70 and pattern.name in ["CupAndHandle", "FlatBase", "AscTriangle", "Flag", "Support Bounce"]:
        return 5
        
    # 7) Long-term INV (Account 6)
    if score >= 60 and td.price > td.sma200 and td.sma50 > td.sma200:
        return 6
        
    # 8) Lottery (Account 8)
    if opt.hasOptions and "WideSpread" not in tags and "NoOptions" not in tags:
        if td.daysToEarnings is None or td.daysToEarnings > EARNINGS_DAYS_BLOCK_OPTIONS:
             return 8
             
    return 0 # Watchlist

# -------------------------------------------------------------------------
# 6) Plan Generator
# -------------------------------------------------------------------------
def build_plan(account_id: int, td: TickerData, pattern: PatternResult) -> Tuple[List[str], List[str], List[str]]:
    
    entry = []
    stop = []
    exit_plan = []
    
    pivot = pattern.pivotPrice if pattern.pivotPrice else td.recentHigh20
    
    if account_id == 1: # SH Swing
        entry = [
            "Entry1: reclaim EMA9/EMA21 + green candle close",
            "Entry2: break above prior day high",
            "Volume confirm: today vol >= 1.5x avg20"
        ]
        stop = ["Stop: close below EMA9", "Hard stop: -2R or below last swing low"]
        exit_plan = ["Take profit: +3% to +7%", "Exit: close below EMA9"]
        
    elif account_id == 2: # Swing
        entry = ["Entry: pullback to EMA21 or SMA50", "Trigger: break of pullback trendline"]
        stop = ["Stop: close below EMA21; deep pullback below SMA50"]
        exit_plan = ["Target: +10% to +20%", "Exit: breakdown below EMA21"]
        
    elif account_id == 3: # POS BO
        entry = [f"Entry: buy breakout above pivot {pivot:.2f} with vol >= 1.4x", "Add: if holds pivot"]
        stop = ["Stop: -7% to -8% (O'Neil rule)", "Exit early: fail back into base"]
        exit_plan = ["Take profit: partial +20%", "Hold: while price above EMA21"]
        
    elif account_id == 4: # POS HVOL
        entry = ["Entry: after HV demand day, buy tight pullback", "Confirm: supply dry up"]
        stop = ["Stop: close below EMA21 or demand-day low"]
        exit_plan = ["Exit: distribution spike or RS roll over"]
        
    elif account_id == 5: # POS PAT
        entry = ["Entry: pattern pivot breakout", "Confirm: volume expansion"]
        stop = ["Stop: -7% to -8% or pattern invalidation"]
        exit_plan = ["Exit: failure back into base"]
        
    elif account_id == 6: # INV
        entry = ["Entry: add on pullbacks to SMA50", "Prefer: rising RS"]
        stop = ["Stop: major trend break (SMA50 down + price < SMA200)"]
        exit_plan = ["Exit: RS deteriorates", "Trim: climactic run"]
        
    elif account_id == 7: # OPT Swing
        entry = ["Entry: breakout/pullback near SMA50", "Options: spread <=5%, OI>=1000"]
        stop = ["Stop: underlying closes below SMA50", "Opt Stop: -30% premium"]
        exit_plan = ["Take profit: +30%-50% option gain", "Time stop: 3-5 days no move"]
        
    elif account_id == 8: # Lottery
        entry = ["Entry: intraday break + RVOL spike", "Rules: NO earnings"]
        stop = ["Hard stop: underlying loses VWAP", "Opt Stop: -20% premium"]
        exit_plan = ["Exit quickly: +15% to +30%", "Time stop: end of day"]
        
    else:
        entry = ["Watch only"]
        
    return entry, stop, exit_plan

# -------------------------------------------------------------------------
# 7) Main Interface
# -------------------------------------------------------------------------

def analyze_ticker(td: TickerData, opt: OptionsSnapshot) -> SetupDecision:
    pattern = detect_pattern(td)
    score, tags, reasons = compute_score(td, opt, pattern)
    grade = grade_from_score(score)
    
    # Options suitability/warning
    optGood, optTags = options_liquidity_tag(opt)
    if not optGood:
        tags.append("OptionsNotIdeal")
        
    # Explicit warnings
    if "Extended/Climactic" in tags:
        reasons.append("High spike risk: likely consolidation")
    if "EarningsNoise" in tags:
        reasons.append("Move likely earnings-driven; wait for base")
        
    account_id = assign_account(td, opt, score, tags, pattern)
    entry, stop, exit_p = build_plan(account_id, td, pattern)
    
    return SetupDecision(
        accountId=account_id,
        ticker=td.symbol,
        grade=grade,
        score=score,
        entryPlan=entry,
        stopPlan=stop,
        exitPlan=exit_p,
        tags=list(set(tags)), # unique
        pattern=pattern,
        reasons=reasons,
        price=td.price,
        changePct=td.changePct
    )
