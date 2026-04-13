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
    },

    "suzuka": {
        "event_overview": """
Round 2 of the SRCS Grand Prix Season 2026 moves to one of the most iconic circuits in the world — Suzuka, Japan.

This round continues the championship battle following Round 1, with early momentum becoming critical.

Race format includes:
- Practice
- Qualifying
- Grand Prix race simulation

Race conditions:
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

Momentum note:
Drivers who performed well in Round 1 can consolidate early championship advantage here.
""",

        "circuit_breakdown": """
**Track Length:** 5.807 km  
**Turns:** 18  
**Circuit Type:** High-speed technical circuit  
**Layout:** Figure-eight (unique crossover design)

**Track Characteristics**
Suzuka is one of the most demanding driver circuits in the world:
- High-speed flowing sections
- Rapid direction changes
- Limited margin for error
- Heavy emphasis on rhythm and precision

This is not a stop-start circuit — it rewards smooth, committed driving.

**Sector 1 – Flow & Commitment (Esses)**
- Continuous left-right sequence
- Requires perfect rhythm and balance
- Small errors compound rapidly
- Overdriving destroys lap time

**Sector 2 – Power & Precision**
- Degner corners require precision entry
- Hairpin provides overtaking opportunity
- Spoon Curve exit is critical for straight-line speed

**Sector 3 – High-Speed Courage**
- 130R is a high-speed commitment corner
- Final chicane is key overtaking zone
- Mistakes here affect main straight performance

**Critical Corners**
**Esses (Turns 3–7)**
- Rhythm section — smooth inputs only
- Avoid aggressive steering corrections

**Degner 1 & 2**
- Precision braking required
- Easy to invalidate lap or pick up penalties

**Hairpin**
- Best overtaking opportunity mid-lap
- Requires clean braking and traction exit

**Spoon Curve**
- Long double-apex corner
- Exit speed defines straight-line performance

**130R**
- High-speed commitment
- Confidence corner — hesitation costs time

**Final Chicane**
- Heavy braking zone
- Primary late-race overtaking opportunity
""",

        "strategic_guidance": """
Suzuka is a rhythm and tire-management circuit where consistency beats aggression.

**Tire Management Model**
- Front tire load is significant through high-speed corners
- Rear stability critical on corner exits
- Overheating occurs from aggressive steering inputs

Key risks:
- Overdriving Sector 1 (Esses)
- Excessive curb usage
- Losing rear stability in Spoon exit

**Engineer Directive**
- Prioritize smooth steering inputs
- Maintain rhythm over outright aggression
- Build pace progressively through the stint

**Pit Strategy Considerations**
Undercut:
- Powerful if stuck in traffic
- Clean air advantage is significant

Overcut:
- Works if maintaining consistent lap times
- Avoids rejoining into traffic

**Critical Strategy Factor**
- Clean laps matter more than peak pace
- Errors cost more time than small pace deficits

**Penalty Risks**
- Track limits at Esses and Spoon
- Late braking into chicane
- Over-aggressive defending
""",

        "lap1_survival": """
**Objective:** Survive Lap 1 without damage while maintaining competitive position.

**Key Risk Areas**
- Turn 1/2 opening sequence
- Esses congestion
- Hairpin compression zone

**Key Principles**
- Expect reduced grip on cold tires
- Avoid side-by-side through Esses
- Brake earlier than normal into heavy zones
- Prioritize exit over entry

**Critical Advice**
- The Esses are NOT an overtaking zone on Lap 1
- Be patient — opportunities come later in the lap

**Priority Hierarchy**
Survival → Position → Aggression

A clean Lap 1 sets up your entire race at Suzuka.
""",

        "overtaking_defending": """
**Primary Overtake Zones**

**Hairpin**
- Best mid-lap opportunity
- Requires strong braking control

**Final Chicane**
- Highest probability move
- Late braking zone
- Critical for final laps

**Main Straight (Turn 1 setup)**
- Depends on chicane exit
- Slipstream opportunity

**Defensive Protocol**
- One defensive move only
- Protect inside line into chicane
- No reactive weaving
- Maintain predictable positioning

**Key Insight**
Most overtakes at Suzuka are set up 2–3 corners earlier — especially through Spoon.
""",

        "championship_mindset": """
Round 2 is about momentum and control.

**Strategic Thinking**
- Strong result here builds early championship pressure
- Back-to-back consistency > one-off result
- Team scoring becomes increasingly important

**Risk Management**
- Suzuka punishes mistakes heavily
- Over-aggression leads to large time loss or incidents

**Mindset Model**
- Precision over aggression
- Consistency over heroics
- Patience over desperation

Drivers who master rhythm here gain a long-term advantage.
""",

        "common_mistakes": """
- Overdriving the Esses (losing rhythm)
- Excessive steering corrections
- Poor Spoon exit compromising straight speed
- Track limits violations in Sector 1
- Late dive attempts into chicane
""",

        "preparation_checklist": """
**Pre-Practice**
- Study corner flow (especially Sector 1)
- Identify braking references for Hairpin & Chicane
- Define realistic race pace

**During Practice**
- Focus on consistency, not peak lap
- Test tire behavior over multiple laps
- Practice clean Spoon exits
- Simulate pit entry

**Pre-Qualifying**
- Build rhythm progressively
- Avoid pushing too early in lap
- Commit fully once flow is established

**Pre-Race**
- Reset mindset
- Focus on clean execution
- Visualize Lap 1 survival
- Confirm pit strategy

Execution wins races at Suzuka — not aggression.
"""
    },
    "miami": {
        "event_overview": """
Round 3 of the SRCS Grand Prix Season 2026 heads to Miami — a circuit that blends long straights, heavy braking zones, and a technical middle sector.

This round comes at an important stage of the championship:
- Early title contenders can strengthen momentum
- Midfield drivers can reset their campaign
- Teams begin to show whether their early results were pace or circumstance

Race format includes:
- Practice
- Qualifying
- Grand Prix race simulation

Race conditions:
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

Momentum note:
Miami rewards drivers who can combine raw speed with discipline under braking.
""",

        "circuit_breakdown": """
**Track Length:** 5.412 km  
**Turns:** 19  
**Circuit Type:** Permanent street-style circuit  
**Layout:** Long straights + technical low-speed section

**Track Characteristics**
Miami is a hybrid challenge:
- Strong overtaking potential on the straights
- Heavy braking zones
- Slow, technical sector in the middle of the lap
- Traction and stability are both critical

This is a circuit where lap time comes from linking together very different corner types cleanly.

**Sector 1 – Launch & Commitment**
- Fast opening sequence
- Confidence under direction change matters
- Good exit speed sets up the long run ahead

**Sector 2 – Precision & Patience**
- Tightest and slowest section of the lap
- Rear traction is heavily tested
- Mistakes here cost both lap time and tire life

**Sector 3 – Straight-Line Opportunity**
- Heavy braking into overtaking zones
- Strong exits are essential
- Drivers can attack or defend aggressively here — but must stay controlled

**Critical Corners**
**Turn 1**
- Lap 1 compression risk
- Important for early positioning
- Easy to lose time with over-caution or over-commitment

**Turns 11–16 complex**
- Slow-speed technical section
- Traction-sensitive
- Overdriving leads to rear instability and poor exits

**End-of-straight braking zones**
- Prime overtaking areas
- Lockup risk is high
- Precision matters more than desperation

**Final corner**
- Crucial for defending and attacking into the next lap
- Clean traction exit creates straight-line advantage
""",

        "strategic_guidance": """
Miami is a race of braking discipline, traction control, and timing your attacks properly.

**Tire Management Model**
- Rear tires are stressed in the slow technical section
- Front tires take punishment under repeated heavy braking
- Excessive wheelspin will hurt stint consistency quickly

Key risks:
- Rear overheating out of slow corners
- Front lockups into major braking zones
- Losing rhythm in the middle sector and overheating tires while recovering

**Engineer Directive**
- Be decisive under braking, but not optimistic
- Prioritize traction over corner-entry heroics
- Build pressure on rivals through exits, not just divebomb attempts

**Pit Strategy Considerations**
Undercut:
- Strong if trapped behind a slower driver
- Useful if clean air is available after the stop

Overcut:
- Can work if your tire wear is under control
- Valuable if rivals are likely to rejoin in traffic

**Critical Strategy Factor**
- A clean out-lap and in-lap can swing the race
- Penalties and lockups are often more costly than slightly conservative pace

**Penalty Risks**
- Late braking into overtaking zones
- Track limits while chasing exit speed
- Moving under braking during defense
""",

        "lap1_survival": """
**Objective:** Survive the opening lap with a clean car and usable strategy options.

**Key Risk Areas**
- Turn 1 compression
- Midfield bunching into heavy braking zones
- Concertina effect in the technical middle sector

**Key Principles**
- Brake earlier than qualifying references
- Expect chaos into Turn 1
- Avoid forcing side-by-side fights through the tighter middle section
- Focus on exits and positioning rather than winning every corner

**Critical Advice**
- Miami rewards patience early and punishment later
- Lap 1 over-aggression often creates race-ending damage or penalties

**Priority Hierarchy**
Survival → Position → Aggression

A clean first lap gives you multiple strategic paths later in the race.
""",

        "overtaking_defending": """
**Primary Overtake Zones**

**Turn 1**
- Viable with a strong launch and good prior exit
- High risk on Lap 1, better later in the race

**Heavy braking zones at the end of the long straights**
- Best overtaking opportunities
- Requires stable braking and early commitment

**Main straight**
- Exit quality from the previous corner determines move success
- Slipstream can create pressure even without full overlap

**Defensive Protocol**
- One defensive move only
- Protect the inside early
- No weaving under braking
- Stay predictable under pressure
- Prioritize strong exits to break tow range

**Key Insight**
In Miami, many passes are created one corner earlier through superior traction, not just braking bravery.
""",

        "championship_mindset": """
Round 3 is where patterns start becoming meaningful.

**Strategic Thinking**
- By Miami, the table begins to reflect genuine form
- A strong finish here can establish championship identity
- Teams should begin maximizing combined points, not just individual attacks

**Risk Management**
- Miami offers overtaking, but also invites overconfidence
- Smart aggression beats reckless ambition

**Mindset Model**
- Attack with structure
- Defend with clarity
- Think in sequences, not isolated corners

The drivers who stay calm under pressure usually leave Miami with the strongest result.
""",

        "common_mistakes": """
- Locking fronts into major braking zones
- Overheating rears in the slow middle sector
- Overcommitting to low-probability overtakes
- Poor traction out of slow corners
- Defending too late and picking up penalties
""",

        "preparation_checklist": """
**Pre-Practice**
- Study the biggest braking zones
- Identify best overtaking opportunities
- Learn where traction matters most

**During Practice**
- Test braking consistency under fuel load
- Monitor rear tire behavior in the technical section
- Practice clean pit entry
- Build a realistic race pace target

**Pre-Qualifying**
- Maximize tire preparation for braking confidence
- Build speed progressively through the lap
- Avoid overdriving the middle sector

**Pre-Race**
- Confirm pit plan
- Visualize Lap 1 survival
- Commit to a risk profile
- Focus on exits, not just entries

Miami rewards control under pressure.
"""
    },
}


def get_driver_assistant(track_key: str) -> dict:
    return DRIVER_ASSISTANTS.get(track_key, {})
