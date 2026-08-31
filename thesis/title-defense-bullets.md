# Title Defense: Talking Points

One page. Bullets, not a script. Say them in your own words.

**Every description must contain three things, in this order:**
1. What it is (the problem, then what the system does)
2. How I will build it
3. How it will be used

Time: T1 about 60 seconds, T2 and T3 about 40 seconds each.

---

## OPENING

- Three proposed titles
- All in cybersecurity, area of detecting attacks
- One minute each, plain terms
- Panel chooses which one I take forward

---

## T1. Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment of Pre- and Post-Change Security Event Streams

### The picture
- Every computer keeps a logbook
- Writes down what happens
- Security team reads it to spot an attacker

### What hardening is
- Turning off risky features to make a computer safer
- Like closing doors and windows you never use
- Normal, required work. Companies do it all the time

### The twist
- Some of those same settings control the logbook
- Close one door, computer quietly stops recording certain things

### Why it is dangerous
- Alarm still switched on
- On paper it still looks like it is working
- But it cannot see anything
- No error, no warning, nobody is told
- Found out only after a break-in

### What my system does
- Records what the computer writes, before
- Applies the security setting
- Records again, same conditions
- Compares the two
- Reports exactly what stopped being recorded
- Then names which alarms went blind, and which attacks are now invisible

### How I will build it
- Python program
- Small laboratory: two virtual machines on my own computer
- Free open-source security software
- My computer is already checked and passed. Setup files downloaded
- Building the laboratory is the first two weeks
- **Do not say the laboratory is already built**

### How it will be used
- Company runs it before applying a security setting
- Gets back a simple report
- Either: this change is safe
- Or: this change just blinded these three alarms, here is what to fix

### If you blank out
> "Making a computer safer can quietly stop it from recording the very things the security team needs to see. My system detects that, at the moment the change is made."

---

## T2. Automated Analytic-Robustness Scoring of Sigma and Wazuh Detection Rules Using a Rule-Feature Dependency Model Based on the Summiting the Pyramid Methodology

### The picture
- Security monitoring software works from a list of rules
- Each rule has an urgency number
- Low number: filed quietly
- High number: wakes somebody up at night

### The problem
- Rules are connected to each other, like a family tree
- Urgency numbers typed in by hand, one rule at a time
- Different people, over many years
- Nobody can see the whole tree
- So a serious alert can get a low number, and nobody ever reads it

### What my tool does
- Reads all the rules
- Draws the family tree
- Checks each urgency number against the rules above and below it
- Lists the ones that look wrong, worst first

### How I will build it
- Python program that reads the rule files
- No laboratory, no special hardware
- Runs on a laptop

### How it will be used
- The software maker or a company runs it on their rule list
- Corrects the wrong numbers before an important alert gets missed

### If you blank out
> "An alert that is marked less urgent than it really is never reaches a person. My tool finds those."

---

## T3. Automated Detection of Severity Inversion in the Wazuh Default Ruleset Using Parent-Child Dependency-Graph Analysis and Topological Consistency Scoring


### The picture
- Security rules work by looking for clues
- Some clues are easy for an attacker to change. A file name, for example
- Rename the file and the rule is useless
- Other clues are hard to change, such as how the program behaves

### The problem
- Companies count how many attacks they can detect
- They do not measure how easy it is to fool each detection
- So the report looks better than the reality

### What my tool does
- Reads each rule
- Works out which clue it depends on
- Scores how hard that clue is to change
- Tells the engineer which rules are weak, and which stronger clue to use instead

### How I will build it
- Python program that reads rule files
- No laboratory
- Runs on a laptop

### How it will be used
- Engineer runs it on the whole rule library
- Gets a list of weak rules with suggested fixes

### If you blank out
> "Counting how many attacks you can detect is not the same as knowing how easily each detection can be fooled. My tool measures the second one."

---

## CLOSING

- Those are the three
- All three are software I build and test myself
- Free tools, no cost
- Ready to take whichever the panel prefers
- **Then stop talking. Let the silence sit.**

### If asked which you prefer (one sentence, then stop)
- The first one
- Only one that produces new measurements, not analysis of files that already exist
- My computer is already verified as able to run it

### If they push a second time
- Closest to how a company actually works day to day
- They change security settings constantly
- Nobody checks what it did to their monitoring

---

## "HOW DO YOU KNOW IT WILL WORK IF NOTHING IS TESTED YET?"

Split it into two. Never answer it as one question.

**Half one: is the problem real?**
- Not a guess
- Windows settings exist where switching them off stops a specific record being written
- Documented by Microsoft
- Can be shown on one computer in a few minutes
- Example: setting called Audit Process Creation. Turn it off and Windows stops writing the record that a program was started. The alarm stays on and still looks healthy

**Half two: will my system measure it well?**
- That is the research question
- Cannot be claimed in advance. That is what the thesis is for
- What I control is finding out early
- First two weeks: small test, two questions, both answered with numbers
- So I know in September, not November

**If pushed again: what if the test fails?**
- Then I know in September and still have the whole schedule to adjust
- That is the point of putting the test first instead of last
- **Do not volunteer that the other two titles need no laboratory.** Only if asked directly

---

## WORD SWAPS

| Never say | Say |
|---|---|
| SIEM, XDR, telemetry | the security monitoring system, the records the computer writes |
| detection rule | an alarm setting, a rule that raises an alert |
| hardening | turning off risky features to make a computer safer |
| endpoint, host | a computer, a laptop, a server |
| false positive | a false alarm |
| statistical significance | checking the difference is real, not random |
| chi-square, Poisson, variance | say nothing. Skip it entirely |
| dependency graph, topological ordering | a family tree of rules |
| static analysis | reading the files without running them |
| severity inversion | an alert marked less urgent than it should be |
| analytic robustness | how hard the rule is to fool |

---

## THREE RULES FOR THE ROOM

1. Say the picture before the problem. They cannot follow a problem in a world they cannot see.
2. One idea per sentence. Stop between ideas.
3. When you finish an answer, stop. Do not add more because nobody spoke.
