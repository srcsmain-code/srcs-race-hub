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

"red_bull_ring": {
        "event_overview": """
Round 4 of the SRCS Grand Prix Season 2026 takes us to the Red Bull Ring in Spielberg, Austria.

This is the first race of the revised second phase of the SRCS calendar and carries its own identity:

**The Sprint Battle**

Flat-out racing. No excuses. Constant pressure.

The Red Bull Ring is short, fast, aggressive, and deceptively simple. Because the lap is so short, the field compresses quickly. Small mistakes become big losses. A poor exit, one missed braking point, or a track-limits warning can immediately pull another driver into range.

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
- SRCS start tire compound: Soft

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

Round identity:
The field compresses here. There is nowhere to hide. You survive the battlefield.
""",

        "circuit_breakdown": """
**Track Length:** 4.318 km  
**Turns:** 10  
**Circuit Type:** Permanent racing circuit  
**Layout:** Short lap, heavy braking zones, long straights, elevation change

**Track Characteristics**
The Red Bull Ring is built around:
- Heavy braking
- Traction exits
- Slipstream battles
- Short-lap pressure
- Repeated overtaking opportunities
- Constant pack racing

This circuit looks simple, but that is the trap. With fewer corners, every braking zone matters more. Every exit matters more. Every mistake is visible.

**Sector 1 – Launch, Turn 1, and the uphill drag**
- Turn 1 exit is critical
- Poor traction here compromises the long climb
- Drivers behind can use the slipstream immediately
- Track limits and exit kerbs can punish overcommitment

**Sector 2 – The combat zone**
- Turns 3 and 4 are the main battle areas
- Heavy braking creates overtaking chances
- Late braking is tempting, but running deep destroys exit speed
- Side-by-side racing is likely here throughout the race

**Sector 3 – Rhythm, precision, and penalties**
- Faster, more flowing section
- Easy to overdrive while chasing
- Track limits can become a serious problem
- Final-corner exit decides whether you attack or defend on the next lap

**Critical Corners**

**Turn 1**
- Important exit onto the uphill section
- Easy to run wide
- Avoid excessive kerb use
- Strong exit creates attacking potential

**Turn 3**
- Prime overtaking zone
- Heavy braking after uphill run
- High risk of divebombs
- Defenders must be clear and early

**Turn 4**
- Another major braking zone
- Great for switchbacks
- Poor exit opens the door into the next sequence

**Final Corner**
- Critical for the main straight
- Track limits risk
- Exit speed decides the next-lap battle
""",

        "strategic_guidance": """
The Red Bull Ring rewards controlled aggression.

Because SRCS starts on Soft tires, the opening phase will be intense. The grip will be high, the pack will be close, and drivers will feel like they can attack everywhere. That is where mistakes happen.

**Tire Management Model**
Primary tire risks:
- Rear wheelspin out of Turns 1, 3 and 4
- Front lockups into the heavy braking zones
- Sliding through the final sector
- Overheating tires while fighting in traffic

**Engineer Directive**
- First 3 laps: survive the compression
- Do not burn the Soft tires fighting every car immediately
- Prioritize exits over heroic entries
- Stay close and force mistakes rather than forcing desperate moves
- Keep penalties under control

**Pit Strategy Considerations**

Undercut is viable if:
- You are stuck behind a slower car
- You can rejoin into clean air
- Your out-lap can be clean and aggressive

Overcut is viable if:
- Your tire wear is under control
- The cars ahead are fighting
- You can keep consistent lap times while others lose time battling

**Critical Strategy Factor**
Because the lap is short, traffic matters. Rejoining into a pack can ruin a good strategy. Clean air is powerful, but only if you can use it immediately.

**Penalty Risks**
- Track limits at Turn 1
- Track limits in the final sector
- Late braking contact into Turn 3
- Moving under braking while defending
""",

        "lap1_survival": """
**Objective:** Survive Lap 1 without damage, penalties, or unnecessary position loss.

The Red Bull Ring opening lap is dangerous because the field reaches the first braking zones quickly and remains tightly packed.

**Key Risk Areas**
- Turn 1 compression
- Uphill run into Turn 3
- Late braking into Turn 4
- Cars rejoining after running wide
- Side-by-side exits onto traction zones

**Key Principles**
- Brake earlier than qualifying reference
- Expect cars to appear late on the inside
- Leave space on corner exit
- Do not force three-wide situations into Turn 3
- Avoid panic if you lose one position early
- Think about the next straight, not only the current corner

**Critical Advice**
Turn 1 does not win the race. Turn 3 can lose it.

The field will compress. Stay calm, keep the car clean, and attack once the race settles.

**Priority Hierarchy**
Survival → Exit Speed → Position → Aggression

A clean Lap 1 gives you many chances to fight back.
""",

        "overtaking_defending": """
**Primary Overtake Zones**

**Turn 3**
- Best overtaking opportunity
- Heavy braking after the uphill straight
- Strong slipstream effect
- Requires decisive but controlled braking

**Turn 4**
- Excellent secondary attack zone
- Useful for switchbacks after Turn 3
- Easy to overcommit and run deep

**Turn 1**
- Possible if the car ahead has poor final-corner exit
- Higher risk on Lap 1
- Better used as a pressure point than a desperation move

**Attacking Protocol**
- Set up the pass one corner earlier
- Prioritize exit speed
- Use slipstream patiently
- Force the defender to choose a line early
- Commit only when overlap is realistic
- If the move is not on, live to attack at the next braking zone

**Defensive Protocol**
- One clear defensive move only
- Defend early, not reactively
- Do not weave on the uphill run
- Protect the inside but preserve exit speed
- Avoid parking the car on the apex
- Think two corners ahead

**Key Insight**
At Red Bull Ring, a bad defence can cost more than simply conceding the corner and fighting back on the next straight.
""",

        "championship_mindset": """
Round 4 starts the next phase of the SRCS season.

By this point, championship patterns are forming:
- Front-runners are defending momentum
- Midfield drivers are trying to break through
- New or reserve drivers can influence the team battle
- Every point is starting to matter more

**Strategic Thinking**
The Red Bull Ring will tempt drivers into constant fighting. But the smartest drivers will know when to attack and when to let the race come back to them.

This is a short lap. If you lose touch, it hurts. If you stay close, opportunities keep coming.

**Risk Management**
- Avoid penalties
- Avoid emotional retaliation
- Avoid low-percentage lunges
- Avoid destroying the tires in early fights
- Keep the car in points contention

**Mindset Model**
Aggressive, but not reckless.  
Fast, but not frantic.  
Brave, but not desperate.

The driver who wins here will be the one who survives pressure without losing discipline.

**Round 4 Identity**
You survived the battlefield.
""",

        "common_mistakes": """
- Braking too late into Turn 3
- Running deep and losing exit speed
- Overusing kerbs at Turn 1
- Picking up track-limit warnings in the final sector
- Fighting too hard during the first five laps
- Defending reactively instead of early
- Burning the Soft tires with wheelspin
- Trying to win every straight-line battle
- Forgetting that the car behind will likely get another chance on the next straight
""",

        "preparation_checklist": """
**Pre-Practice**
- Learn braking references for Turns 1, 3 and 4
- Identify safe overtaking zones
- Review track-limit danger areas
- Decide your aggression level before driving

**During Practice**
- Test heavy braking consistency
- Practise clean exits from Turns 1, 3 and 4
- Run several laps without track-limit warnings
- Practise following another car closely if possible
- Simulate pit entry and pit exit rhythm

**Pre-Qualifying**
- Build tire temperature gradually
- Focus on exit speed, not only late braking
- Avoid invalidating laps through overcommitment
- Give yourself space for a clean lap

**Pre-Race**
- Confirm pit strategy
- Visualize Lap 1 into Turn 1 and Turn 3
- Prepare for close racing
- Stay calm if boxed in early
- Remember: clean pressure beats chaos

Red Bull Ring rewards drivers who can fight hard without losing control.
"""
    },
    "silverstone": {
        "event_overview": """
Round 5 of the SRCS Grand Prix Season 2026 takes the championship to Silverstone — one of the fastest and most demanding circuits on the calendar.

Silverstone rewards confidence more than anything, rhythm and precision. Drivers must balance high-speed commitment with tire management and disciplined racecraft.

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

Championship Points:
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

+1 point for Fastest Lap when finishing in the Top 10.

Silverstone is a circuit where one small mistake can affect several corners. Smoothness and consistency are more valuable than forcing every entry.
""",

        "circuit_breakdown": """
**Track Length:** 5.891 km  
**Turns:** 18  
**Circuit Type:** High-speed permanent circuit  
**Primary Challenge:** Sustained cornering load and high-speed direction changes

**Track Characteristics**
Silverstone combines:
- Very high-speed corners
- Long, loaded corner sequences
- Heavy braking zones
- Multiple overtaking opportunities
- Significant front-tire stress

The circuit rewards drivers who can carry speed without creating excessive understeer or tire temperature.

**Sector 1 – Braking and Positioning**
- Abbey is fast and requires confidence
- Village is one of the main overtaking zones
- The Loop is slow and traction-limited
- A poor exit from The Loop compromises the run through Aintree

**Sector 2 – Rhythm and Commitment**
- Brooklands and Luffield require patience
- Woodcote exit determines speed onto the old pit straight
- Copse is a high-speed confidence corner
- Entry mistakes at Copse create large time loss

**Sector 3 – Maximum Commitment**
- Maggotts, Becketts and Chapel form the defining sequence
- Rhythm is more important than aggressive steering
- Chapel exit determines speed down Hangar Straight
- Stowe is a major overtaking and defensive zone
- Club exit is vital for the run to the finish line

**Critical Corners**

**Village**
- Heavy braking
- Strong overtaking opportunity
- High risk of Lap 1 contact
- Avoid turning in too early

**The Loop**
- Slowest part of the circuit
- Rear traction is critical
- Patience on throttle prevents wheelspin

**Brooklands**
- Long braking zone
- Inside line useful for defending
- Easy to carry too much speed and miss Luffield

**Copse**
- High-speed commitment corner
- Small steering corrections cost speed
- Avoid forcing the car beyond front-grip limits

**Maggotts–Becketts–Chapel**
- Most important rhythm section
- First input determines the entire sequence
- Smooth direction changes reduce tire stress
- Chapel exit is more important than attacking every apex

**Stowe**
- Primary overtaking opportunity after Hangar Straight
- Late braking is possible, but overshooting ruins the run into Vale

**Vale and Club**
- Heavy braking followed by traction demand
- Important final-lap overtaking zone
- Club exit determines start-finish straight speed
""",

        "strategic_guidance": """
Silverstone places high loads on the tires, especially the front axle.

**Tire Management Model**
Main risks:
- Front-left overheating
- Persistent understeer through long corners
- Sliding through Maggotts and Becketts
- Rear wheelspin from slow corners
- Excessive curb use destabilising the car

**Engineer Directive**
- Build pace progressively
- Avoid forcing the front tires during the opening laps
- Prioritise clean exits over maximum entry speed
- Use smooth steering through sustained corners

**Pit Strategy Considerations**
The undercut can be effective if:
- Tire performance has clearly dropped
- You are trapped behind slower traffic
- You can rejoin in clean air

The overcut may work if:
- Your tires remain stable
- Rivals rejoin in traffic
- You can maintain consistent pace without sliding

Practice:
- Pit entry positioning
- Braking for the pit lane
- Pit exit under cold-tire conditions
- Rejoining safely near the racing line

**Race Pace Guidance**
- Avoid qualifying-style commitment on every lap
- Protect front tires in long loaded corners
- Accept a small time loss rather than creating a large slide
- Consistency through Sector 3 creates better race pace than isolated fast corners

**Penalty Risk**
High-risk areas include:
- Track limits at Copse
- Maggotts and Becketts cut warnings
- Stowe exit
- Vale and Club
- Late contact under braking into Village
""",

        "lap1_survival": """
**Objective:** Complete Lap 1 with the car intact and without penalties.

**Turn 1 – Abbey**
- Expect cars to arrive side-by-side
- Do not assume the normal qualifying line is available
- Leave room on corner exit

**Village**
- Brake earlier than your normal reference
- Expect concertina effects
- Avoid diving into a disappearing gap

**The Loop**
- Low-speed contact is common
- Prioritise rotation and traction
- Do not accelerate into the rear of a slower car

**Brooklands**
- Cars may arrive in groups
- Protect the inside only if fully alongside
- Avoid squeezing another driver off the circuit

**Lap 1 Principle**
Silverstone offers several overtaking opportunities. There is no need to settle the race in the opening sector.

Survival → Position → Pace.
""",

        "overtaking_defending": """
**Primary Overtaking Zones**

**Village**
- Strong braking opportunity
- Best attempted with clear overlap before turn-in
- Defending driver should choose a line early

**Brooklands**
- Good overtaking zone after the Wellington Straight
- Inside line controls corner entry
- Exit remains important for Luffield and Woodcote

**Stowe**
- Best high-speed overtaking opportunity
- Strong exit from Chapel is essential
- Late braking carries risk of running wide

**Vale**
- Effective late-race overtaking location
- Heavy braking creates opportunity
- Contact risk increases when cars arrive side-by-side

**Defensive Protocol**
- Make one clear defensive move
- Do not move under braking
- Protect the inside early
- Avoid forcing rivals onto grass or outside circuit limits
- Focus on exit speed when defending through a sequence

**Racecraft Principle**
At Silverstone, a good exit often creates a better overtaking opportunity than a desperate entry.
""",

        "championship_mindset": """
Round 5 marks the midpoint of the SRCS Grand Prix Season.

At this stage:
- Championship gaps begin to matter
- Consistency becomes increasingly valuable
- Team points can change significantly in one race
- Drivers must balance aggression with season objectives

**Strategic Questions**
- Are you racing for the win, podium or points?
- Is the driver ahead a direct championship rival?
- Is defending the position worth the tire cost?
- Would a clean result strengthen your season more than a high-risk move?

**Mindset**
Silverstone rewards confident drivers, but confidence must remain controlled.

A driver who finishes every lap strongly will usually outperform a driver chasing one spectacular sector.
""",

        "common_mistakes": """
- Carrying too much speed into Village
- Applying throttle too early through The Loop
- Missing the Brooklands braking point
- Forcing Copse entry and creating understeer
- Overdriving Maggotts and Becketts
- Sacrificing Chapel exit for an aggressive apex
- Late braking into Stowe without control
- Track-limit penalties through high-speed corners
- Excessive front-tire wear from repeated steering corrections
""",

        "preparation_checklist": """
**Pre-Practice**
- Review Village, Brooklands and Stowe braking references
- Learn the Maggotts–Becketts–Chapel sequence
- Decide where overtaking attempts are realistic
- Identify track-limit risk areas

**During Practice**
- Build confidence through Copse
- Test several lines through Maggotts and Becketts
- Focus on Chapel exit speed
- Practise pit entry and pit exit
- Test race pace with controlled steering inputs
- Monitor front-tire behaviour

**Pre-Qualifying**
- Create space before starting the lap
- Build tire temperature progressively
- Avoid overcommitting at Copse
- Prioritise a clean Sector 3
- Remember that a valid lap is better than a faster deleted lap

**Pre-Race**
- Confirm pit strategy
- Visualise the Lap 1 braking zones
- Decide your opening-lap aggression level
- Prepare for side-by-side racing
- Stay patient through traffic
"""
    },
}


def get_driver_assistant(track_key: str) -> dict:
    return DRIVER_ASSISTANTS.get(track_key, {})
