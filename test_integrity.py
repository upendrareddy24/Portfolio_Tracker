import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

print("--- Testing Imports ---")
try:
    from portfolio_engine import TickerData, OptionsSnapshot, analyze_ticker, build_plan
    print("✅ portfolio_engine imported successfully")
except Exception as e:
    print(f"❌ Failed to import portfolio_engine: {e}")
    sys.exit(1)

print("\n--- Testing Logic Execution ---")
try:
    # Create dummy data
    td = TickerData(
        symbol="TEST",
        price=150.0,
        high=155.0,
        low=148.0,
        open=149.0,
        close=150.0,
        prevClose=145.0,
        changePct=3.45,
        volume=1000000,
        avgVol20=800000,
        avgVol50=900000,
        sma50=140.0,
        sma200=130.0,
        ema9=148.0,
        ema21=145.0,
        rsTrend="rising",
        recentHigh20=152.0,
        recentLow20=140.0,
        daysToEarnings=20
    )
    
    opt = OptionsSnapshot(hasOptions=True, spreadPct=0.01, openInterest=2000)
    
    print("Running analyze_ticker...")
    decision = analyze_ticker(td, opt)
    print(f"✅ analyze_ticker success. Score: {decision.score}, State: {decision.state}")
    
    print("Plans:")
    print(f"Entry: {decision.entryPlan}")
    
except Exception as e:
    print(f"❌ Logic execution failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Integrity Test PASSED")
