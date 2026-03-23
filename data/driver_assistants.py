# data/driver_assistants.py

DRIVER_ASSISTANTS = {
    "melbourne": {
        "event_overview": """
Round 1 of the SRCS Grand Prix Season 2026 marks the beginning of both the Drivers’ and Teams’ Championships.

This event follows the official SRCS race structure:
- Practice
- Qualifying
- Grand Prix race simulation

Race format includes:
- Tire wear ON
- Compulsory pit stop
- Collisions ON
- Penalties ON
- Dry weather conditions

Championship Points (Top 10):
1st – 25
2nd – 18
3rd – 15
4th – 12
5th – 10
6th – 8
7th – 6
8th – 4
9th – 2
10th – 1

+1 point for Fastest Lap (must finish in Top 10)
""",

        "circuit_breakdown": """
**Track Length:** 5.278 km  
**Turns:** 14  
**Circuit Type:** Semi-street  
**Surface:** Low initial grip, improves over session

**Track Characteristics**
Albert Park is a rhythm circuit. It combines:
- Heavy traction zones
- Long straights
- Medium-speed direction changes
- Limited run-off in key braking zones

Grip evolution is significant during Practice and Qualifying.

**Sector 1 – Attack & Positioning**
- Heavy braking into Turn 1 and Turn 3
- Highest probability of overtakes
- High Lap 1 incident risk
- Critical to maintain exit speed into the following straight

**Sector 2 – Flow & Commitment**
- Medium-speed direction changes
- Requires clean steering inputs
- Excess sliding here overheats rear tires

**Sector 3 – Traction & Patience**
- Technical final complex
- Rear stability determines main straight speed
- Poor exit compromises overtaking potential

**Critical Corners**
**Turn 1**
- Cold tires on Lap 1 = reduced braking stability
- Inside line defensive advantage
- Outside line high risk on opening lap

**Turn 3**
- Primary overtaking opportunity
- Late braking zone
- Protect inside if defending

**Turns 9/10**
- High-speed commitment
- Small mistakes cost large time
- Track limits risk

**Final Corner**
- Most important exit onto final straight
- Wheelspin here destroys straight-line advantage
""",

        "strategic_guidance": """
This race includes tire wear and compulsory pit stop — strategy matters.

**Tire Management Model**
Rear degradation is the primary performance limiter at Melbourne.

Key risks:
- Excessive wheelspin exiting T3 and final corner
- Over-rotating mid-corner in Sector 2
- Locking front-left under heavy braking

**Engineer Directive**
- First 3 laps: Controlled aggression
- Avoid sliding early
- Protect rear traction for final stint attack

**Pit Strategy Considerations**
Undercut viable if:
- Stuck behind slower car
- Clean air available after stop

Overcut viable if:
- Consistent lap pace
- Traffic expected ahead of rival

Important:
- Practice pit entry braking point
- Avoid crossing pit line under pressure
- Ensure clean rejoin

**Penalty Management**
High-risk areas:
- T9/10 track limits
- Late dive attempts into T3
- Moving under braking
""",

        "lap1_survival": """
**Objective:** End Lap 1 without damage or penalty.

**Key Principles**
- Brake earlier than qualifying reference
- Expect reduced grip on cold tires
- Assume drivers around you will be aggressive
- Leave margin at corner exit
- Avoid side-by-side into blind braking zones

**Priority Hierarchy**
Survival → Position → Aggression

**Remember**
You cannot win the championship in Turn 1.
You can severely damage it there.
""",

        "overtaking_defending": """
**Primary Overtake Zones**
**Turn 1**
- Requires strong launch
- Risk high on opening laps

**Turn 3**
- Best overtaking location
- Heavy braking opportunity
- Commit early or abort cleanly

**Main Straight**
- Dependent on final corner exit
- Exit traction determines move success

**Defensive Protocol**
- One clear defensive movement only
- Protect inside into T3
- No weaving under braking
- Signal intent early
- Late reactive defending increases incident probability
""",

        "championship_mindset": """
Round 1 sets psychological tone for the season.

**Points Structure Reminder**
25–18–15–12–10–8–6–4–2–1 + Fastest Lap (Top 10)

**Strategic Thinking**
- A P4 with no damage > DNF chasing P2
- Team points matter from race one
- Teammate cooperation increases championship probability

**Mindset Model**
- Conservative → Consistency Focus
- Balanced → Strategic Attack
- Aggressive → High Risk, High Reward

Choose before lights out.
""",

        "common_mistakes": """
- Front-left lockups into T1/T3
- Overusing curbs
- Overdriving heavy fuel
- Cold rear spins
- Overcommitting to low-probability overtakes
""",

        "preparation_checklist": """
**Pre-Practice**
- Review braking references
- Study overtaking zones
- Define race aggression profile

**During Practice**
- Test braking consistency into T1 & T3
- Simulate pit entry
- Identify safe race pace delta
- Monitor rear tire feel

**Pre-Qualifying**
- Clear traffic strategy
- Build tire temperature progressively
- Commit on final push lap

**Pre-Race**
- Hydrate
- Reset mindset
- Confirm pit plan
- Visualize Lap 1
"""
    }
}


def get_driver_assistant(track_key: str) -> dict:
    return DRIVER_ASSISTANTS.get(track_key, {})
