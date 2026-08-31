# Title Proposal Defense: Script and Notes

**Tuesday 25 August 2026, 4:00 to 5:00 pm. Business casual.**

This is the **title stage only**. The panel is choosing which of the three titles becomes your
thesis. Most of them are not cybersecurity people. So the whole job tomorrow is: make them
understand, in ordinary words, what each system is, how you will build it, and who would use it.

Goal: they pick T1.

Total speaking time for the three descriptions: about three minutes. Keep it there.

---

## Part 1. How to make them pick T1, honestly

Six levers. All of them are truthful. None of them require you to make T2 or T3 sound worse
than they are.

1. **T1 goes first.** It is already number 1 on your slide. People remember the first one.
2. **Only T1 gets a picture.** A panel picks the idea they can imagine. Give T1 a short everyday
   story. Give T2 and T3 a plain, accurate, shorter description. Shorter is not unfair. It is
   just proportionate.
3. **Call T1 a system. Call T2 and T3 tools.** Your professor's own words were "what system it
   is." T1 has several working parts, a laboratory, and a workflow. T2 and T3 are programs that
   read files. That is an accurate difference, and it matters to a panel.
4. **Say you have already verified that your computer can run it.** The only real objection to T1
   is that it needs equipment. You ran the readiness checks and they passed, so the objection is
   answered. **Do not say the laboratory is built. It is not.** What is true: the computer is
   ready, the virtualization software is installed and working, and the installation files are
   downloaded. The virtual machines themselves have not been built yet.
5. **Say your preference once, when asked.** One sentence. Do not campaign.
6. **Do not run down T2 and T3.** Describe them fairly. If a panelist prefers one, take it
   gracefully. Both are real work.

---

## Part 2. Opening line

> "Good afternoon. I have three proposed titles. All three are in cybersecurity, in the area of
> detecting attacks. 

Then go straight to number 1. Do not explain the field first. They will get lost.

---

## Part 3. The three descriptions

Each one answers the three things your professor asked for: **what it is, how I will build it,
how it will be used.**

### Title 1. Detection of Hardening-Induced Blind Spots via Differential Sequence Alignment of Pre- and Post-Change Security Event Streams

> "Every computer keeps a logbook. Whenever something happens, it writes it down. A security team
> reads that logbook to spot an attacker.
>
> Now, part of security work is called hardening. It means turning off risky features so the
> computer is safer. It is like closing the doors and windows you never use.
>
> Here is the problem. Some of those same settings also control what the computer writes in its
> logbook. So when you close one of those doors, the computer quietly stops recording certain
> things. The security team's alarm is still switched on, and on paper it still looks like it is
> working, but it can no longer see anything. No error appears. Nobody is told. They usually find
> out only after a break-in.
>
> My system catches that at the moment it happens. It records what the computer writes, applies
> the security setting, records again under the same conditions, compares the two, and reports
> exactly what stopped being recorded. Then it tells you which alarms just went blind and which
> attacks you can no longer see.
>
> How I will build it. It is a program written in Python. It runs a small laboratory of two
> virtual machines on my own computer, using free open-source security software. I have already
> checked that my computer can run it, and the setup files are downloaded. Building the
> laboratory is the first two weeks of my schedule.
>
> How it will be used. Before a company applies a security setting to its computers, it runs
> this. It gets back a simple report: this change is safe, or this change just blinded these
> three alarms, and here is what to fix."

**If you only have 30 seconds:** keep the logbook, the closing doors, the alarm that looks on but
sees nothing, and the report at the end. Drop the rest.

### Title 2. Automated Analytic-Robustness Scoring of Sigma and Wazuh Detection Rules Using a Rule-Feature Dependency Model Based on the Summiting the Pyramid Methodology

> "Security monitoring software works from a list of rules. Each rule has an urgency number. A
> low number is filed quietly. A high number wakes somebody up at night.
>
> These rules are connected to each other, like a family tree. But the urgency numbers are typed
> in by hand, one rule at a time, by different people over many years, and nobody can see the
> whole tree. So sometimes a serious alert is given a low number, and nobody ever reads it.
>
> This tool reads all the rules, draws the family tree, checks whether each urgency number makes
> sense compared to the rules above and below it, and produces a list of the ones that look
> wrong, worst first.
>
> How I will build it. A Python program that reads the rule files. No laboratory and no special
> hardware. It runs on a laptop.
>
> How it will be used. The software maker or a company runs it on their rule list and corrects
> the wrong numbers before an important alert gets missed."

### Title 3. Automated Detection of Severity Inversion in the Wazuh Default Ruleset Using Parent-Child Dependency-Graph Analysis and Topological Consistency Scoring

> "Security rules work by looking for clues. Some clues are very easy for an attacker to change.
> A file name, for example. Rename the file and the rule is useless. Other clues are hard to
> change, such as how the program actually behaves.
>
> Today companies count how many attacks they can detect. They do not measure how easy it is to
> fool each detection. So the report looks better than the reality.
>
> This tool reads each rule, works out which clue it depends on, and scores how hard that clue is
> to change. Then it tells the engineer which rules are weak, and which stronger clue to use
> instead.
>
> How I will build it. A Python program that reads rule files. Again no laboratory. It runs on a
> laptop.
>
> How it will be used. An engineer runs it on their whole rule library and gets back a list of
> the weak rules with suggested fixes."

---

## Part 4. Closing

> "Those are the three. All three are software I will build and test myself, using free tools, at
> no cost. I am ready to take whichever the panel prefers."

Then stop and wait. Do not fill the silence.

**If they ask which you prefer**, one sentence, then stop:

> "The first one. It is the only one of the three that produces new measurements rather than
> analyzing files that already exist, and I have already verified that my computer can run the
> laboratory it needs."

**If they ask a second time, or push back**, add only this:

> "It is also the one closest to how a company actually works day to day. They change security
> settings all the time and nobody checks what it did to their monitoring."

---

## Part 5. Words to avoid, and what to say instead

The panel is not technical. Every word on the left costs you the room.

| Do not say | Say |
|---|---|
| SIEM, XDR | the security monitoring system |
| telemetry, event log, log data | the records the computer writes |
| detection rule, analytic | an alarm setting, a rule that raises an alert |
| hardening | turning off risky features to make a computer safer |
| blind spot | something the security team can no longer see |
| endpoint, host | a computer, a laptop, a server |
| Sysmon | a free Microsoft tool that makes Windows keep more detailed records |
| Wazuh | free security monitoring software |
| Sigma rules | rules written in a shared format |
| MITRE ATT&CK | a public catalogue of the methods attackers use |
| CIS Benchmark, DISA STIG | published security checklists |
| adversary emulation, Atomic Red Team | safe scripted tests that imitate an attack |
| static analysis | reading the files without running them |
| false positive | a false alarm |
| precision and recall | how often it is right, and how much of the problem it finds |
| statistical significance | checking the difference is real and not just random |
| coefficient of variation, chi-square, Poisson | do not say these tomorrow at all |
| topological ordering, dependency graph | a family tree of rules |
| severity inversion | an alert marked less urgent than it should be |
| analytic robustness | how hard the rule is to fool |

---

## Part 6. Questions a non-technical panel actually asks

Short answers. Say the short answer, then stop.

**Q. In simple terms, what will you submit at the end?**
A working program, the written thesis, and the results of testing it.

**Q. Is this a system or just a program?**
The first one is a system. It has several parts that work together and it controls a small
laboratory. The other two are single analysis tools that read files.

**Q. Who would use this?**
The security team of a company. In the first one, the person who applies the security setting
and the person who watches for attacks.

**Q. Is this like antivirus?**
No. Antivirus tries to block an attack. Mine checks whether the alarm that is supposed to warn
you still works.

**Q. Where will you get your data?**
I generate it myself in my own laboratory, using free scripted tests that safely imitate an
attack. No company data and no personal data is involved.

**Q. Is it safe? Is it legal?**
Yes. Everything runs inside virtual machines on my own computer, with the internet disconnected
during tests. Nothing touches any other organization.

**Q. How much will it cost?**
Nothing. All the software is free and open source and I use my own computer.

**Q. Do you have the equipment?**
Yes. I own the computer and I have already run the readiness checks on it. Processor, memory,
disk space, virtualization support, and the virtualization software all passed, and the
installation files are downloaded. For the other two titles, a laptop is enough.

**Q. How far along are you? Have you started building?**
I have finished the readiness checks on my computer and I have written the full build plan, step
by step. I have not built the laboratory yet and I have not written code yet. That is on
purpose. The title has to be chosen first, and two of the three titles need no laboratory at
all.

**Q. So you are starting from zero?**
No. The plan is written, the equipment is verified, the software is chosen, and the reference
material is collected. What is left is building it, and that is what the schedule from August to
December is for.

**Q. How long will it take?**
The plan runs from August to December, with the system built and tested before the final
defense.

**Q. Can you do this alone?**
Yes. It is one person's work. The programming is in Python and I have the environment ready.

**Q. Has anyone done this already?**
There is related work. A 2024 study at a major security conference showed that many widely used
detection rules can be fooled easily. But nobody has built a tool that checks what a security
change does to your own monitoring, which is what my first title does.

**Q. Why is this important here in the Philippines?**
Because the software involved is free. That is what schools, small companies, and government
offices here can actually afford, and they have no way to check whether their monitoring still
works.

**Q. What is your contribution? You are using existing tools.**
The tools collect the records. My contribution is the method that compares them and works out
what was lost and what it means. That part does not exist today.

**Q. What if it does not work?**
I have an early test planned in the first two weeks that tells me whether the approach holds. If
it fails, I switch to one of the other titles, and I still report the honest result.

**Q. Why three titles?**
So the panel can choose. They are alternatives, not parts of one project. Only one gets built.

---

## Part 7. What NOT to bring up tomorrow

This is a title session with a non-technical panel. Detail is not a virtue tomorrow. It costs
you attention and invites questions that do not help you.

1. **Do not raise the hardening-change catalogue correction.** That is a Chapter 3 methodology
   detail. It does not affect the title or whether the topic is viable. Raise it with your
   research professor separately, not with the panel tomorrow.
2. **Do not explain the statistics.** No chi-square, no Poisson, no variance. If pushed, say
   "the system checks the difference is real and not just random variation."
3. **Do not volunteer the SigmaHQ annotation problem in title 3** unless the panel starts
   leaning toward title 3. If they do lean that way, say this and nothing more:

   > "If you choose the third one, I should tell you one thing first. I planned to check my
   > scores against a set of expert-made reference labels. When I checked, there were only six of
   > them, which is too few. I can still do it, but I would have to create those labels myself
   > with a second reviewer, which adds manual work."

4. **Do not read the proposal document out loud.** They have it. Talk to them instead.
5. **Do not apologize for anything.** Nothing needs an apology.

---

## Part 8. Practical checklist for tomorrow

- [ ] Business casual. Collared shirt, slacks, closed shoes.
- [ ] The one slide: `thesis/topic-proposal-titles.pptx`. The three descriptions are in the
      speaker notes.
- [ ] Open it once tonight and check Presenter View works, so the notes show on your screen.
- [ ] Bring the Topic Proposal Document. That is what you are actually presenting.
- [ ] Say each description out loud three times tonight. Time yourself. Three minutes total.
- [ ] Practice the closing line and then practice staying quiet after it.
- [ ] Know your own repository address in case they ask to see your work.
- [ ] Water. Arrive fifteen minutes early. Test the display before 4:00.

---

## Part 9. The two sentences to have ready at all times

If you lose your place, fall back to these.

**What the first title is:**
> "Making a computer safer can quietly stop it from recording the very things the security team
> needs to see. My system detects that, at the moment the change is made."

**Why it matters:**
> "The alarm still looks switched on. That is the danger. Nobody knows it went blind until there
> is a break-in."
