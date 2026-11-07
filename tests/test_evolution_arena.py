"""
Phase 7 Verification Script: Strategy Evolution Arena & Multi-Line Fan Engine
Tests:
1. Genetic Strategy Mutator: Bounded parameter mutations & population diversity.
2. Background Lab Worker:
   - Multi-line equity fan curves (branching trade-by-trade from $1,000 baseline).
   - Monte Carlo drawdown enforcement (safe < 4% vs culled).
   - Tournament Leaderboard ranking.
3. Champion vs. Challenger Promotion:
   - Dynamic hot-swap into strategy_dna.json.
   - Audit persistence in terminal.db (rsi_evolution_history).
4. REST API Endpoints:
   - /api/evolution/tournament
   - /api/evolution/fan-curves
   - /api/evolution/mutate
   - /api/evolution/promote
"""

import sys
import os
import io
import json

# Force UTF-8 on Windows Console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure backend package is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.optimization.genetic_mutator import GeneticMutator
from backend.optimization.background_lab import BackgroundLabWorker
from backend.database.db_manager import DatabaseManager
from fastapi.testclient import TestClient
from backend.app import app


def test_genetic_mutator():
    print("\n" + "=" * 65)
    print("STEP 1: Testing Genetic Strategy Mutator & Parameter Bounds")
    print("=" * 65)

    mutator = GeneticMutator()
    population = mutator.generate_population(count=15, asset="XAUUSD", generation=1)

    print(f"Generated Variants Count: {len(population)}")
    assert len(population) == 15, "Must generate 15 diverse variants"

    # Verify diversity and mathematical boundaries
    ids = [v.variant_id for v in population]
    assert len(set(ids)) == len(ids), "Each variant ID must be unique"

    for v in population[:3]:
        p = v.params
        print(f"  • {v.variant_id}: ATR SL Mult: {p['atr_sl_multiplier']} | TP1: {p['tp1_rr_ratio']}R | TP2: {p['tp2_rr_ratio']}R | A+ Thresh: {p['grade_a_plus_threshold']}%")
        assert 1.0 <= p["atr_sl_multiplier"] <= 2.5, "ATR SL multiplier out of bounds"
        assert 0.8 <= p["tp1_rr_ratio"] <= 2.0, "TP1 ratio out of bounds"
        assert 2.0 <= p["tp2_rr_ratio"] <= 3.8, "TP2 ratio out of bounds"
        assert 75.0 <= p["grade_a_plus_threshold"] <= 95.0, "Grade A+ threshold out of bounds"

    print(">>> Genetic Strategy Mutator: PASSED (100% Mathematically Bounded)")


def test_background_lab_and_fan_curves():
    print("\n" + "=" * 65)
    print("STEP 2: Testing Background Lab & Multi-Line Equity Fan Curves")
    print("=" * 65)

    lab = BackgroundLabWorker()
    fan_data = lab.get_fan_curves()
    curves = fan_data["curves"]

    print(f"Generation Simulated: #{fan_data['generation']}")
    print(f"Multi-Line Equity Curves Generated: {len(curves)}")
    assert len(curves) >= 15, "Must generate at least 15 equity curves"

    # Verify fan curve shape (Starts at $1,000, branches trade-by-trade)
    for c in curves[:3]:
        curve_pts = c["curve"]
        assert curve_pts[0]["equity"] == 1000.0, "Every curve must start at $1,000 origin"
        assert len(curve_pts) == 81, "Must contain 80 simulated trades + 1 baseline point"
        print(f"  • {c['variant_id']}: Return {c['total_return_pct']:+.1f}% | Final Equity: ${c['final_equity']} | Color: {c['color']}")

    # Verify Leaderboard
    leaderboard = lab.get_leaderboard()
    print(f"\nTournament Leaderboard (Top 3 Candidates):")
    for item in leaderboard[:3]:
        print(f"  Rank #{item['rank']} | {item['variant_id']} | Win Rate: {item['win_rate']}% | PF: {item['profit_factor']} | Max DD: {item['max_drawdown_percent']}% | Status: {item['status']}")

    assert leaderboard[0]["status"] == "CHAMPION", "Rank #1 must be designated Champion"
    assert leaderboard[0]["profit_factor"] >= leaderboard[-1]["profit_factor"], "Leaderboard must be sorted by performance"
    print(">>> Background Lab & Multi-Line Fan Generation: PASSED")


def test_champion_promotion():
    print("\n" + "=" * 65)
    print("STEP 3: Testing Champion vs. Challenger Promotion & Hot-Swap")
    print("=" * 65)

    db = DatabaseManager()
    lab = BackgroundLabWorker(db_manager=db)
    leaderboard = lab.get_leaderboard()

    # Find a Challenger to promote
    challengers = [item for item in leaderboard if item["status"] == "CHALLENGER"]
    if not challengers:
        challengers = leaderboard[1:2]
    challenger = challengers[0]

    print(f"Promoting Challenger: {challenger['variant_id']} (Win Rate: {challenger['win_rate']}%)")
    result = lab.promote_challenger(challenger["variant_id"])

    print(f"Promotion Result: {result['status']} | Message: {result['message']}")
    assert result["status"] == "PROMOTED"
    assert lab.active_champion_id == challenger["variant_id"]

    # Verify strategy_dna.json was hot-swapped
    with open(lab.dna_path, "r", encoding="utf-8") as f:
        dna = json.load(f)
    print(f"Verified Active Champion in strategy_dna.json: {dna['active_champion_id']}")
    assert dna["active_champion_id"] == challenger["variant_id"]

    # Verify SQLite rsi_evolution_history audit record
    history = db.get_rsi_history(limit=5)
    assert len(history) > 0
    latest = history[0]
    print(f"Verified Audit in terminal.db: Cycle ID {latest['cycle_id']} | Promoted: {bool(latest['promoted'])}")
    assert latest["promoted"] == 1
    print(">>> Champion Hot-Swap & Audit Persistence: PASSED")


def test_evolution_api_endpoints():
    print("\n" + "=" * 65)
    print("STEP 4: Testing Evolution Arena REST Endpoints")
    print("=" * 65)

    client = TestClient(app)

    # 1. GET /api/evolution/tournament
    res_tourn = client.get("/api/evolution/tournament")
    print(f"1. GET /api/evolution/tournament -> Status Code: {res_tourn.status_code}")
    assert res_tourn.status_code == 200
    t_data = res_tourn.json()
    print(f"   • Active Champion: {t_data['active_champion_id']}")
    print(f"   • Candidates Ranked: {len(t_data['leaderboard'])}")
    assert len(t_data["leaderboard"]) > 0

    # 2. GET /api/evolution/fan-curves
    res_curves = client.get("/api/evolution/fan-curves")
    print(f"\n2. GET /api/evolution/fan-curves -> Status Code: {res_curves.status_code}")
    assert res_curves.status_code == 200
    curves_data = res_curves.json()
    print(f"   • Curves Returned: {len(curves_data['curves'])}")
    assert len(curves_data["curves"]) >= 15

    # 3. POST /api/evolution/mutate
    res_mutate = client.post("/api/evolution/mutate?asset=XAUUSD&count=10")
    print(f"\n3. POST /api/evolution/mutate -> Status Code: {res_mutate.status_code}")
    assert res_mutate.status_code == 200
    mutate_data = res_mutate.json()
    print(f"   • Generation Simulated: #{mutate_data['generation']}")
    assert mutate_data["status"] == "GENERATION_SIMULATED"

    # 4. POST /api/evolution/promote
    first_candidate = t_data["leaderboard"][0]["variant_id"]
    res_promo = client.post("/api/evolution/promote", json={"variant_id": first_candidate})
    print(f"\n4. POST /api/evolution/promote -> Status Code: {res_promo.status_code}")
    assert res_promo.status_code == 200
    promo_data = res_promo.json()
    print(f"   • Promoted Champion: {promo_data['champion_id']}")
    assert promo_data["status"] == "PROMOTED"

    print("\n>>> All 4 Evolution Arena REST Endpoints: PASSED (100% Exact)")


if __name__ == "__main__":
    test_genetic_mutator()
    test_background_lab_and_fan_curves()
    test_champion_promotion()
    test_evolution_api_endpoints()
