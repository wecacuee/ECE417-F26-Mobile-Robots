# -*- coding: utf-8 -*-
"""Single source of truth for the RIT talk: slide content + speaker notes."""

import os
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")

SLIDES = [

dict(
    type="title",
    title="Uncertainty-aware learning for safe robotics",
    subtitle="The biggest bottleneck to safety in learning-based robots?",
    footer="Vikas Dhiman  -  CVAR Lab, University of Maine  -  RIT  -  August 6, 2026",
    notes="""Good morning / afternoon, and thank you for having me at RIT. Today I want to talk about
where I think AI, machine learning, and robotics are headed, and about three ideas I believe
have to be first-class citizens in that future — not afterthoughts — if we want autonomous
systems that people can actually trust: uncertainty estimation, active learning, and safe
control. I'll ground this in the work my lab has been doing, and I'll spend extra time on
why I think drones are the platform where all three of these ideas matter most, and where
they are hardest to get right."""
),

# dict(
#     type="section",
#     title="State of Robotics in 2026",
#     subtitle="VLAs, Gemini Robotics, and humanoids",
#     notes="""Let's start with the elephant in the room, because I guarantee some of you are
# already thinking it: haven't Gemini Robotics, RT-2, pi-zero, and this wave of humanoid robots
# already solved robotics? Generalist foundation-model policies that watch a scene and just act?
# Let's look at that honestly for a few minutes before I get to my own lab's work."""
# ),

dict(
    type="videos",
    #title="Robots can (sometimes) clean, do laundry",
    title="State of Robotics in 2026",
    subtitle="VLAs, Gemini Robotics, and humanoids",
    bullets=[],
    # bullets=[
    #     "VLA models — RT-2, OpenVLA, π0, Helix, GR00T, Gemini Robotics — merge perception, language, and low-level action in one network",
    #     "Trained on internet-scale data plus large teleoperated demonstration corpora",
    #     "Paired with humanoid platforms marketed as the matching generalist body: Figure 03, Tesla Optimus, 1X NEO, Unitree",
    #     "Public demos: folding laundry, making salad, unloading a dishwasher, autonomously",
    # ],
    videos=[
        dict(thumb=f"{MEDIA}/humanoid_games_thumb.jpg", 
        caption="CNN: Physical Intelligence gets $400M from Jeff Bezos",
             url="", video=f"{MEDIA}/videos/laundry-folding.webm"),
        dict(thumb=f"{MEDIA}/gemini_robotics_thumb.jpg", caption="Gemini Robotics 2 — Google DeepMind",
             url="https://www.youtube.com/watch?v=4lSQnrMC6nY", video=f"{MEDIA}/videos/gemini_robotics.mp4"),
        dict(thumb=f"{MEDIA}/figure03_thumb.jpg", caption="Figure 03 — delivery & laundry demo",
             url="https://www.youtube.com/watch?v=nRS-iB8YRJQ", video=f"{MEDIA}/videos/figure03.mp4"),
        # dict(thumb=f"{MEDIA}/humanoid_games_thumb.jpg", caption="World Humanoid Games — falls & repairs",
        #      url="https://www.youtube.com/watch?v=8pfAC4f2aV0", video=f"{MEDIA}/videos/humanoid_games.mp4"),
    ],
    notes="""2025 and 2026 have been the years of vision-language-action models and humanoids
going mainstream. Gemini Robotics, RT-2 and its descendants, OpenVLA, pi-zero, NVIDIA's
GR00T, Figure's Helix — the pitch is one generalist policy that watches the scene, reads a
language instruction, and directly emits low-level actions, across many embodiments. Paired
with humanoid hardware like Figure 03, Tesla Optimus, and 1X's NEO, the marketing is a
generalist brain finally matched with a generalist body. Click through and you'll find
impressive reels: folding laundry, making a salad, unloading a full dishwasher autonomously.
These models are capable. That capability is exactly why the gap on the next slide matters —
capable and safe are different claims."""
),

dict(
    type="content",
    title="Uncertainty estimation and safe control are missing",
    bullets=[
        "No released VLA technical report — RT-2, OpenVLA, π0, Gemini Robotics, GR00T, Helix — publishes calibrated, distance-aware uncertainty over its own actions",
        "Where confidence exists, it's a token-level softmax — high-confidence errors far from training data are a documented failure mode (Nguyen et al., 2015)",
        # "Public “safety” = curated environment + human on the e-stop + selectively shown rollouts, not a provable constraint",
        "Failure-detection add-ons exist because base VLAs don't self-report failure: SAFE (Gu et al., 2025), VLA-FAIL (Seligmann et al., 2026), ProbeAct (Zhang et al., 2026), FPC-VLA (Yang et al., 2025)",
        # "Same gap in world-model RL: dynamics uncertainty is anti-correlated with actual collision risk, r < 0.15 (Wang, 2026)",
        "Scaling data and parameters lowers the failure rate — it does not certify zero failures in the one deployment that matters",
    ],
    notes="""Here's the part the demo reels don't show. Go read the technical reports for
RT-2, OpenVLA, pi-zero, Gemini Robotics, GR00T, Helix — none of them publish a calibrated,
distance-aware uncertainty over the actions the policy is about to take. Where a confidence
number exists at all, it is typically a token-level softmax over the action-as-language-token
output. Nguyen, Yosinski, and Clune showed back in 2015 that deep networks report high
confidence on inputs that look nothing like their training data — the same non-distance-aware
failure mode I'll show you concretely later in this talk, except here it's steering a
thirty-kilogram humanoid. 'Safety' in the public demos, as far as anyone outside these
companies can verify, means a curated environment, a human standing by the e-stop, and a reel
that shows you the takes that worked. This isn't just my opinion: the robotics research
community's own 2025-2026 output says the same thing. SAFE (Gu et al., 2025, NeurIPS),
VLA-FAIL (Seligmann et al., 2026), ProbeAct (Zhang et al., 2026), and FPC-VLA (Yang et al.,
2025) all exist for one reason — to bolt failure detection onto an already-trained VLA, because
the base model doesn't tell you when it's wrong. And it isn't unique to VLAs: Wang (2026) shows
that dynamics-based uncertainty in model-based RL world models is nearly uncorrelated with
actual collision risk under partial observability. Same gap, different architecture. The
headline point: scaling data and parameters makes the model fail less often, on average. It
does not certify the absence of failure in the one deployment you actually care about. Those
are different claims, and safety-critical robotics needs the second one."""
),

# dict(
#     type="content",
#     title="Where the three pillars fit around a VLA",
#     bullets=[
#         "Reframe, don't reject: a VLA is a learned prior over actions, not the safety-critical controller",
#         "Wrap its proposed actions in distance-aware uncertainty estimation — not the model's internal softmax",
#         "Feed that uncertainty into active learning: flag exactly when the policy leaves its comfort zone",
#         "Filter every action through a safe-control layer that can veto or project it back to the safe set",
#         "No published system adds this calibrated, distance-aware wrapper to a VLA-controlled robot yet",
#     ],
#     notes="""So where does this leave the vision I want to spend the rest of the talk on?
# Not a rejection of VLAs — they're a genuinely powerful way to get a broad, flexible prior over
# what action to try next. The reframing is this: a VLA is a proposal generator, not a
# safety-critical controller. Wrap its proposed action with distance-aware uncertainty
# estimation, applied to the VLA's output rather than trusting its internal softmax. Use that
# uncertainty as an active-learning signal — it tells you exactly when the policy has wandered
# outside its comfort zone and needs a human in the loop, a safe fallback behavior, or targeted
# new demonstration data. Then run every proposed action through a safety filter that can veto or
# project it back onto the safe set, no matter how the action was generated upstream. As far as
# I've found, nobody has published a wrapper like this for a VLA-controlled physical system —
# not for a humanoid, not for a drone. That gap is exactly where I think the next several years
# of this research should go, and it's the throughline for everything else I'll show you today:
# uncertainty estimation, active learning, and safe control, worked out first on ground robots and
# manipulators, headed toward exactly this problem."""
# ),

dict(
    type="bio",
    title="Who I am / CVAR Lab",
    img=f"{MEDIA}/vikas_headshot.png",
    bullets=[
        "Assistant Professor, Electrical & Computer Engineering, University of Maine",
        "Runs the CVAR Lab — Computer Vision and Autonomous Robotics",
        "PhD, University of Michigan (2019); MS, University at Buffalo (2014); BE, IIT Roorkee (2008)",
        "Postdoc: Contextual Robotics Institute / Existential Robotics Lab, UC San Diego",
        # "Funded by NSF Award #2218063",
        #"My co-author on this uncertainty-estimation work, Mohammad Javad Khojasteh, is now faculty here at RIT",
    ],
    notes="""A quick intro. I'm an assistant professor in ECE at the University of Maine, where I run
the CVAR lab — Computer Vision and Autonomous Robotics. My path went through IIT Roorkee,
University at Buffalo, a PhD at Michigan on mapping and control, and a postdoc at UC San
Diego's Existential Robotics Lab. Our work is funded by NSF. One fun connection to today's
audience: a good chunk of the safety-critical uncertainty estimation work I'll show you is
co-authored with Mohammad Javad Khojasteh, who is now on the faculty here at RIT — so some
of this is quite literally RIT research."""
),

dict(
    type="content",
    title="AI/ML pushes accuracy but leaves out uncertainty as an open problem",
    bullets=[
        # "AI/ML is leaving the benchmark and entering the physical world: self-driving cars, warehouse robots, delivery drones, surgical assistants",
        #"The real world is unstructured, non-stationary, and unforgiving of mistakes",
        "A model that is 95% accurate on a test set can still be catastrophically wrong on the 5% — and in robotics, wrong outputs become physical consequences",
        "The bottleneck to deployment is no longer just “can it learn?” — it's “can we trust it enough to let it act?”",
    ],
    notes="""We are in the middle of a huge transition: AI and ML are moving out of static
benchmarks and into physical, embodied systems that act in the world — self-driving cars,
warehouse robots, delivery drones. But the real world doesn't look like a curated test set.
It's unstructured, it changes over time, and mistakes have physical consequences, not just a
lower accuracy number. Increasingly, the hard problem in robotics isn't raw learning capability —
we have very capable models — it's trust. Can we let this learned system actually act, with
consequences we're willing to accept?"""
),

dict(
    type="content_img",
    title="When learning meets the real world",
    img=f"{MEDIA}/crash.jpg",
    bullets=[
        "2018, Chandler, AZ: a Waymo self-driving vehicle crash after a human-driven car ran a red light",
        "Perception and prediction misjudged an edge case outside its training distribution",
        "The lesson isn't “autonomy is unsafe” — it's that we deployed learned components without an explicit, verifiable model of what they don't know",
        "Without safety guarantees, ML-based control is useless in safety-critical applications",
    ],
    notes="""Here's a concrete example. This is a Waymo vehicle involved in a crash in Chandler,
Arizona. The point of this slide isn't to pick on any one company — every AV program has
examples like this. The point is structural: these systems were making decisions based on
learned perception and prediction, and when the scenario drifted from what the model had
seen, there was no explicit signal saying 'I'm not confident here, be conservative.' My
thesis, and the thesis of my lab, is simple: without safety guarantees, machine-learning-based
control is not useful in safety-critical applications — no matter how good the average-case
accuracy is."""
),

dict(
    type="pillars",
    title="My vision: three pillars of trustworthy autonomy",
    lead="A learning-enabled autonomous system should never act on a belief it can't quantify, "
         "never explore blindly, and never violate a safety constraint — even while it is still learning.",
    pillars=[
        ("Uncertainty\nEstimation", "Know what you don't know — and how confident to be, everywhere in state space"),
        ("Active\nLearning", "Choose what to learn next based on where uncertainty (and value) is highest"),
        ("Safe\nControl", "Guarantee constraints are respected online, using that same uncertainty"),
    ],
    outcome="Trustworthy, adaptive autonomy",
    notes="""Here's the vision I want to leave you with today, distilled into three pillars.
First, uncertainty estimation: a system has to know what it doesn't know, and that estimate
has to be meaningful everywhere in the state space, not just near its training data. Second,
active learning: instead of passively hoovering up whatever data comes its way, a system
should use its own uncertainty to decide what to learn next — where to look, where to explore,
what data is actually valuable. Third, safe control: all of that uncertainty has to feed
directly into the controller, so that constraints — collision avoidance, actuator limits,
whatever the safety spec is — are guaranteed to hold even while the system is still learning
online. These three are not independent research topics for me — they're one pipeline, and
today's talk is organized around showing you that pipeline, and then extending it toward
drones specifically."""
),

dict(
    type="content_img",
    title="Why drones raise the stakes",
    img=f"{MEDIA}/drone-delivery.png",
    bullets=[
        "Higher relative degree: force -> acceleration -> velocity -> position; errors compound through more integrators than a ground robot",
        "Disturbances are structural, not incidental: wind gusts, prop-wash, ground effect, payload shifts mid-flight",
        "Often GPS-denied or contested (indoors, urban canyons, under tree canopy, contested airspace)",
        "Severe compute/energy budget: the uncertainty method has to run onboard, in real time, on a power-constrained platform",
        "No graceful failure mode: a mistake is a fall, not a slow rollback",
    ],
    notes="""So why lean so hard on drones for this vision? A few reasons, and they compound.
First, math: for a ground robot you can often get away with treating velocity or even
position as directly controllable. For a quadrotor, control acts on rotor forces, which
integrate up through attitude and velocity before they show up as position — that's a system
of high relative degree, and every one of those integrators is a place where a wrong model
or an unmodeled disturbance accumulates error. Second, the disturbances aren't rare edge
cases — wind, prop-wash, ground effect, and shifting payloads are just what flying is like.
Third, a lot of the interesting drone applications — indoor inspection, search and rescue,
delivery in urban canyons — are exactly where GPS is unreliable, so the robot has to trust its
own learned state estimate. Fourth, whatever uncertainty method we use has to run onboard, in
real time, on a platform with a fraction of the compute and battery budget of a ground
vehicle. And finally, there's no soft failure mode — a ground robot that's uncertain can slow
down and stop; a drone that's uncertain still has to stay in the air. That's why I think
drones are the platform that will really stress-test whether these three pillars work."""
),

dict(
    type="section",
    title="Pillar 1",
    subtitle="Uncertainty Estimation",
    notes="""Let's start with the first pillar: uncertainty estimation."""
),

dict(
    type="content",
    title="Two kinds of “I don't know”",
    bullets=[
        "Aleatoric uncertainty — irreducible noise in the data/process itself (sensor noise, turbulence). More data doesn't remove it.",
        "Epistemic uncertainty — the model's own ignorance from limited data/coverage. More relevant data reduces it.",
        "A safe controller needs both, separated: aleatoric tells you the floor risk you can never eliminate; epistemic tells you where to be cautious, or where to go learn more",
        "Desired properties for any estimator we deploy: (1) captures both kinds of uncertainty, (2) is distance-aware, (3) is computationally efficient enough to run online",
    ],
    notes="""There are two fundamentally different kinds of uncertainty. Aleatoric uncertainty is
noise baked into the process itself — sensor noise, gusty air — no amount of extra data
removes it. Epistemic uncertainty is the model's own ignorance — it shrinks as you collect
more relevant data. This distinction matters enormously for control: aleatoric uncertainty
tells you the safety margin you must always keep, no matter what; epistemic uncertainty tells
you where the model might simply be wrong, and where it might be worth actively going to
learn. Any uncertainty estimator we're going to trust in the loop needs three properties:
it has to capture both kinds, it has to be distance-aware, and it has to be cheap enough to
run online. Let's look at that middle property next, because it's the one people get wrong
most often."""
),

dict(
    type="image_full",
    title="Property 2: distance-awareness",
    img=f"{MEDIA}/distance_aware.png",
    caption="Left: many popular deep uncertainty methods report LOW uncertainty far from any training data. "
            "Right: a distance-aware estimator correctly reports HIGH uncertainty far from training data, "
            "regardless of direction.",
    notes="""This figure is the crux of it. Red dots are training data — two clusters. On the
left, a typical deep-learning uncertainty method: notice the uncertainty (the blue shading)
actually goes back down far away from the data, in these wing-shaped low-uncertainty regions.
That's a real, well-documented failure mode of softmax and even many Bayesian neural nets —
they can be confidently wrong far outside their training distribution. This is exactly the
'demos don't show you' failure mode from the VLA discussion, made concrete on a toy problem.
On the right is what we actually want: uncertainty that grows monotonically with distance from
any training point, in every direction. If your uncertainty estimate can be fooled like the
left panel, then your safety controller can be fooled too — it will confidently steer into
territory it has never seen. This is the property we specifically designed our methods
around."""
),

dict(
    type="triad",
    title="The Goldilocks problem in safe control",
    items=[
        ("Underestimate\n/ ignore uncertainty", "Unpredictable, unsafe behavior — the controller acts confident where it shouldn't"),
        ("Well-calibrated\nuncertainty", "Uncertainty-aware controller: safe AND still capable of making progress"),
        ("Overestimate\nuncertainty", "Overly conservative controller — technically “safe” by refusing to do anything useful"),
    ],
    notes="""And here's why calibration itself matters, not just having *some* uncertainty
number. If you underestimate or ignore uncertainty, you get exactly the Waymo-crash failure
mode — confident, unsafe behavior. If you overestimate uncertainty, you get a robot that's
technically safe because it refuses to move — useless in practice, and in the drone case,
often that means just hovering and burning battery. The entire point of our uncertainty work
is to land in that narrow middle band: well-calibrated uncertainty that lets the controller
be both safe and capable."""
),

dict(
    type="content",
    title="DADEE: combining the two uncertainty types",
    bullets=[
        "Ataei & Dhiman (2024) — Direct Aleatoric + Deep Epistemic Ensembles",
        "Key empirical finding: model-variance methods (anchored ensembles) are accurate far from data but collapse to near-zero uncertainty in-domain; direct-estimation methods (DEUP) are accurate in-domain but underestimate out-of-distribution",
        "DADEE trains an anchored ensemble for epistemic/OOD uncertainty, plus a direct estimator trained on the ensemble's own residuals for aleatoric/in-domain uncertainty",
        "Deployed inside a probabilistic CLF-CBF safe controller for a robot navigating with online-learned, unknown dynamics",
    ],
    notes="""Our first system, DADEE, is built on exactly that observation. We found that
variance-based ensemble methods are great far from the data but collapse toward zero
confidence right where you have plenty of data — which is backwards. Direct-estimation
methods like DEUP are accurate in-domain but underestimate risk out of distribution. DADEE
combines both: an anchored ensemble supplies the epistemic, distance-aware signal, and we
train a second, direct estimator on the ensemble's residual errors to capture the in-domain
aleatoric noise. We then feed that combined uncertainty into a probabilistic control-Lyapunov,
control-barrier-function controller, so the robot can learn its own dynamics online while
staying provably safe."""
),

dict(
    type="content_img",
    title="DADEE — the cost of ignoring uncertainty",
    img=f"{MEDIA}/dadee_table.png",
    bullets=[
        "Husky robot circling an obstacle with unknown, online-learned dynamics",
        "Baseline controller with NO uncertainty accounting: 24.2% error rate",
        "DADEE at high required safety level (p=0.9): 0.3% error rate",
        "That's roughly an 80x reduction in the safety-violation rate, just from modeling uncertainty honestly",
    ],
    notes="""This table is the punchline of the pillar-one story. Same robot, same task —
navigating around an obstacle while learning its own dynamics online — the only thing that
changes is how uncertainty is accounted for in the controller. Ignore uncertainty entirely
and you get roughly a 1-in-4 error rate. Use DADEE with a well-calibrated, high safety
requirement, and that drops to about 3-in-1000 — roughly an 80-times reduction. This is the
central argument of my whole talk in one table: uncertainty-awareness is not a nice-to-have,
it is the difference between a system that mostly works and one you'd actually trust near
people or expensive equipment."""
),

dict(
    type="content_img",
    title="DAREK: worst-case, distance-aware bounds",
    img=f"{MEDIA}/kdarek_bands.png",
    bullets=[
        "Ataei, Khojasteh & Dhiman (2025), IEEE ICASSP",
        "Some safety cases want a deterministic, worst-case guarantee, not just a calibrated probability",
        "DAREK builds on Kolmogorov-Arnold-style spline networks: closed-form interpolation-error bounds (Newton's polynomial remainder) plus Lipschitz-constant propagation give a provable error band, not a sampled one",
        "Shown here: DAREK vs. our follow-up K-DAREK error bands around a hard, oscillatory function",
    ],
    notes="""Sometimes a calibrated probability isn't enough — you want an actual worst-case
guarantee, the kind a certifier or a regulator would accept. That's DAREK, published at
ICASSP 2025 with Javad Khojasteh. It's built on spline-based networks — related to the
Kolmogorov-Arnold network idea — where each piece has a closed-form interpolation error bound
from classical numerical analysis, and we propagate Lipschitz constants layer to layer to get
a provable, distance-aware error band, not something we had to estimate by sampling. This
plot shows DAREK's band in red on a deliberately hard, oscillatory test function — notice how
the band widens correctly wherever the function does something the model hasn't seen enough
of. The blue band is our next-generation version, K-DAREK, which I'll get to in a second."""
),

dict(
    type="content_img",
    title="K-DAREK: making it fast enough to deploy",
    img=f"{MEDIA}/kdarek_loss.jpg",
    bullets=[
        "Ataei, Dhiman & Khojasteh (2025), IEEE ACSSC",
        "DAREK's pure-spline architecture was hard to train — oscillation and hyperparameter sensitivity",
        "K-DAREK: a two-block hybrid — a spectrally-normalized MLP block (known Lipschitz constant) + a spline block (tight closed-form error bounds) — trains faster and much more smoothly",
        "~4x faster and ~10x more compute-efficient than deep ensembles; ~8.6x more scalable than Gaussian Processes",
        "Reduces safety-bound violation rate from 1.8% (DAREK) to 1.1% (K-DAREK) in multi-agent safe navigation",
    ],
    notes="""DAREK worked, but it was genuinely painful to train — the pure spline
architecture is prone to oscillation and is sensitive to hyperparameters, visible here as the
spiky blue training curve. K-DAREK fixes that with a hybrid two-block architecture: an MLP
block with a spectrally-normalized, provably-known Lipschitz constant, feeding a spline block
that still gives us the tight closed-form error bounds. You can see the orange K-DAREK
training curve converges faster and far more smoothly. The efficiency numbers matter for
deployment: about 4 times faster and 10 times more compute-efficient than deep ensembles, and
roughly 8.6 times more scalable than Gaussian processes — GPs scale cubically in the number of
data points, which is a non-starter for a system streaming sensor data continuously, which is
exactly the drone use case. And in a multi-agent safe-navigation benchmark, K-DAREK cuts the
safety-bound violation rate almost in half versus DAREK, from 1.8% to 1.1%."""
),

dict(
    type="section",
    title="From uncertainty to action",
    subtitle="Safe Control",
    notes="""So we have well-calibrated, distance-aware, efficient uncertainty. Now, how does
that actually make the robot safe? That's the safe-control piece."""
),

dict(
    type="content_img",
    title="CBF-CLF-SOCP: safety as an online optimization",
    img=f"{MEDIA}/multiagent_success.png",
    bullets=[
        "Control Barrier Functions (CBFs) encode “stay safe” as a constraint: h(x) >= 0",
        "Control Lyapunov Functions (CLFs) encode “make progress toward the goal”",
        "We fold the learned dynamics' uncertainty into a chance constraint, P(safe) >= 1-δ, solved as a second-order cone program (SOCP) at every control step",
        "Works for systems of arbitrary relative degree — this is exactly what lets the same theory cover a quadrotor, not just a ground robot",
        "Multi-agent navigation: uncertainty-aware control (GP or DAREK) beats the “nominal” controller across every safety level tested",
    ],
    notes="""Mechanically, here's how uncertainty becomes a guarantee. A control barrier
function defines a safety boundary as an inequality; a control Lyapunov function defines
progress toward the goal. We combine them, insert the learned dynamics' uncertainty as a
chance constraint — probability of staying safe at least 1 minus delta — and solve that as a
second-order cone program at every timestep, fast enough for real-time control. The
theoretical piece I want to highlight: this formulation handles systems of arbitrary relative
degree. That detail is exactly why this generalizes cleanly from a ground robot to a
quadrotor, where you're several integrators away from the control input. This plot shows the
payoff in a multi-agent navigation benchmark: as you increase the required safety level along
the x-axis, both GP-based and our DAREK-based uncertainty-aware controllers track upward in
success rate, while a nominal, uncertainty-blind controller stays flat and actually degrades —
being safety-aware doesn't just avoid collisions, it makes the whole system more successful at
its actual task."""
),

dict(
    type="section",
    title="Pillar 2",
    subtitle="Active Learning",
    notes="""Uncertainty estimation and safe control tell you how to act, and how to act
safely, given what you currently know. Active learning is about deciding what to go find out
next."""
),

dict(
    type="content",
    title="Don't just collect data — choose it",
    bullets=[
        "Passive learning: log whatever the robot happens to see and retrain offline",
        "Active learning: use the model's own uncertainty, online, to decide where to look, where to move, or which map region needs more data",
        "The same distance-aware uncertainty from Pillar 1 becomes the acquisition signal for Pillar 2 — one estimate, two jobs",
        "For a resource-constrained platform like a drone, this isn't a luxury: every extra sample costs flight time and battery",
    ],
    notes="""Active learning is the natural next step once you have a good uncertainty
estimate: instead of passively logging whatever data streams by, use that same distance-aware
uncertainty signal online to decide what's worth learning next — where to fly, where to look,
which part of a map is still poorly known. This is efficient by construction: the same
uncertainty estimate we built for safety now doubles as the acquisition function for
exploration. And for a drone specifically, this isn't just elegant, it's necessary — every
extra sample you collect costs flight time and battery, so you cannot afford to explore
randomly."""
),

dict(
    type="content",
    title="Active learning in practice: uncertainty-driven mapping",
    bullets=[
        "“Sparse Topological Maps for Navigation Using Policy Uncertainty” — submitted to CoRL 2026",
        "Idea: only add a new node to the navigation map when the policy's own uncertainty/decision-confidence signals a genuinely new decision state — not on a fixed distance or image-similarity schedule",
        "Result (CARLA, outdoor): a map with 276 nodes matches the success rate and path efficiency of a similarity-based map with 1,493 nodes — a 5x reduction",
        "This is active learning applied to memory itself: don't remember everything, remember what matters",
    ],
    notes="""Here's a direct example from a paper we just submitted to CoRL 2026. The setting
is topological navigation: a robot builds a graph of place-nodes as it explores, and later
uses that graph plus a local policy to navigate. The standard approach adds a node every fixed
distance, or whenever the visual appearance changes enough. We instead add a node only when
the policy's own uncertainty signals that this is a genuinely new decision point — a place
where the low-level policy would actually behave differently. In outdoor CARLA experiments,
that gets us a map with only 276 nodes that matches the success rate and path efficiency of a
1,493-node map built the conventional way — a 5x reduction in memory, for free, just by using
uncertainty as the acquisition signal. That's active learning applied to what to remember, not
just what to sample — and it's directly the kind of memory budget a small onboard drone
computer needs."""
),

dict(
    type="content_img",
    title="Fast reactive planning: a safety enabler",
    img=f"{MEDIA}/sdf_quadrotor.png",
    bullets=[
        "Eiyike et al. (2026), IEEE IROS — “SE(3) Neural Potential Fields for 6-DoF Trajectory Planning Directly from Images”",
        "Learns a continuous potential field directly from images (YOLO-detected goal = attractive, obstacles = repulsive) — no explicit 3D reconstruction step",
        "Planning time: 0.16s vs. 20+s for an explicit-3D-reconstruction + RRT* baseline — a 126–173x speedup, while matching success rate",
        "Trajectories fall out of gradient descent on the learned field — this is exactly the kind of onboard, real-time reactive layer a flying vehicle needs",
    ],
    notes="""This is a different but complementary thread from my student Jeffrey Eiyike,
headed to IROS 2026. Classical pipelines reconstruct an explicit 3D model of the scene and
then run a search-based planner like RRT* over it — accurate, but slow, tens of seconds per
plan. Instead, we learn a continuous potential field directly from images — a YOLO detector
marks the goal object as attractive and obstacles as repulsive, and we train a NeRF-style
network to represent that field in 3D without ever building an explicit 3D map. A trajectory
just falls out of gradient descent on the field. The result: planning time drops from twenty
seconds to about 0.16 seconds — over a hundred times faster — while matching the success rate
of the baseline that was handed a perfect 3D model as an unfair advantage. This is a manipulator
result today, but a controller that has to replan in under 200 milliseconds using only onboard
images is precisely the reactive layer a drone needs to dodge a branch or a gust in real time.
The graphic here, by the way, is from an earlier signed-distance-function experiment in the
same line of work — one of the few places a quadrotor already shows up directly in our figures."""
),

dict(
    type="pipeline",
    title="Putting it together: a vision for the next drone",
    steps=[
        "Learn dynamics online",
        "with distance-aware,\nwell-calibrated\nuncertainty (DADEE /\nK-DAREK)",
        "Actively choose\nwhat to sense /\nwhere to fly\n(uncertainty-driven\nexploration)",
        "React in real time\nwith a learned\npotential field\n(no explicit 3D map)",
        "Stay provably safe\nvia CBF-CLF-SOCP,\nany relative degree",
    ],
    loop_label="all four run continuously, onboard, in the flight-control loop",
    notes="""So here's the vision, stitched into one loop, and this is genuinely how I think
about the next several years of my lab's work. A drone learns its own dynamics online — wind
response, payload-shifted inertia, ground-effect near a landing surface — using a K-DAREK-style
estimator that's cheap enough and distance-aware enough to trust. That same uncertainty signal
drives active learning: where should it fly next to reduce dangerous ignorance, or where does
the map need another node. A fast, image-native potential-field-style planner reacts to what
it sees in well under the time it takes to react to a gust. And underneath all of it, a
CBF-CLF-SOCP safety layer — one that doesn't care about relative degree — guarantees the
vehicle never actually violates a hard constraint, no matter what the learned pieces are still
getting wrong. None of these four pieces is hypothetical; we've built and validated every one
of them on ground robots and manipulators. The vision is to close this loop, onboard, on a
flying vehicle."""
),

dict(
    type="content",
    title="Why drones, why now",
    bullets=[
        "Application pull: delivery, infrastructure/bridge inspection, precision agriculture, search & rescue, contested-environment surveying",
        "Regulatory pull: BVLOS (beyond-visual-line-of-sight) rules are loosening worldwide, but explicitly conditioned on demonstrable safety cases",
        "The safety mathematics already generalizes to quadrotor dynamics (arbitrary relative degree) — what's missing is the systems integration, not new theory",
        "This is, deliberately, an area where academic research (safety-first, published, reproducible) can lead before industry commits",
    ],
    notes="""Why put so much weight on drones specifically, right now? Two forces are
converging. On the application side, the demand is real and growing — delivery, bridge and
infrastructure inspection, precision agriculture, search and rescue. On the regulatory side,
beyond-visual-line-of-sight rules are loosening across the world, but every regulator is
asking for a demonstrable, quantifiable safety case, not just a track record of not crashing
yet. The good news, from where I sit: the hard math — the CBF-CLF-SOCP formulation handling
arbitrary relative degree — already covers quadrotor dynamics. What's missing isn't new
theory, it's the systems work of actually closing that loop onboard, in real time, on
constrained hardware. That's exactly the kind of problem where safety-first, published,
reproducible academic research can and should lead before industry locks in an approach."""
),

dict(
    type="content",
    title="Roadmap / future directions",
    bullets=[
        "Probabilistic (not just worst-case) bounds for spline/KAN networks — worst-case bounds can be needlessly conservative",
        "Real robot deployment: uncertainty-aware CBF + VSLAM on a mobile platform navigating crowded, unstructured spaces — generalizing next to wind/gust disturbance and 3D airspace",
        "Multi-agent settings: safe coexistence with pedestrians / other agents under mutual uncertainty",
        "Target venues: RSS, UAI, IROS; real-robot demonstrations moving from ground robot toward small aerial platforms",
    ],
    notes="""Concretely, here's the near-term roadmap. First, moving from worst-case bounds to
calibrated probabilistic bounds for the spline and KAN-style networks, since worst-case can be
needlessly conservative — recall the Goldilocks slide. Second, we're actively deploying this
uncertainty-aware CBF stack, combined with visual SLAM, on a real mobile robot navigating
crowded, unstructured indoor spaces — slippery floors, tight hallways — as the proving ground
before we take the same stack to wind gusts and full 3D airspace. Third, extending to
multi-agent settings where the robot has to stay safe around pedestrians or other agents who
are themselves uncertain. We're targeting RSS, UAI, and IROS for these results, and the plan
is to move our physical demonstrations from ground robot toward small aerial platforms over
the next year."""
),

dict(
    type="content",
    title="The broader vision for the field",
    bullets=[
        "Uncertainty estimation, active learning, and safe control shouldn't be a bolt-on safety layer added after a model is deployed",
        "They should be a standard stack, designed in from the start, for any AI/ML system that is allowed to act in the physical world",
        "The methods are general — the same math that works for a ground robot's CBF, generalizes to a quadrotor's higher relative degree, and even to a power-grid inverter's current limits",
        "The next generation of autonomous systems will be judged less by how well they perform on average, and more by how honestly they know their own limits",
    ],
    notes="""Zooming back out, here's the broader claim I want to make about the field, beyond
my own lab's results. Uncertainty estimation, active learning, and safe control shouldn't be a
safety patch bolted onto a model after the fact — they should be part of the standard stack
for any AI or ML system that gets to act in the physical world, designed in from day one. And
the encouraging thing is that this math is genuinely general — the same CBF-CLF safety
formulation we validated on a ground robot generalizes to a quadrotor's higher relative
degree, and honestly even to a completely different domain like a grid-connected power
inverter's current limits, which is a project in my lab as well. I think the next generation
of autonomous systems is going to be judged less by their average-case benchmark score, and
more by how honestly and efficiently they know the limits of what they know."""
),

dict(
    type="team",
    title="The CVAR Lab",
    imgs=[f"{MEDIA}/team1.png", f"{MEDIA}/team2.png", f"{MEDIA}/team3.png"],
    bullets=[
        "PhD students: Jeffrey Eiyike, Masoud Ataei, Arman Kiani",
        "MS students: Ata Turgut",
        "Also: Shihab Ahamad, Karun Varghese",
        "Funded by NSF Award #2218063",
        "Thank you to my committee/collaborators, including Mohammad Javad Khojasteh (RIT)",
    ],
    notes="""None of this is solo work. This is the CVAR lab at UMaine — PhD students Jeffrey
Eiyike, Masoud Ataei, and Arman Kiani, MS student Ata Turgut, and also Shihab Ahamad and Karun
Varghese. Supported by NSF award 2218063, and built in close collaboration with Mohammad
Javad Khojasteh, now here at RIT."""
),

dict(
    type="pubs",
    title="Selected publications",
    pubs=[
        "M. Ataei, V. Dhiman. DADEE: Well-calibrated uncertainty quantification in neural networks for barriers-based robot safety. arXiv, 2024.",
        "M. Ataei, M.J. Khojasteh, V. Dhiman. DAREK — Distance-Aware Error for Kolmogorov Networks. IEEE ICASSP, 2025.",
        "M. Ataei, V. Dhiman, M.J. Khojasteh. K-DAREK — Distance-Aware Error for Kurkova-Kolmogorov Networks. IEEE ACSSC, 2025.",
        "J. Eiyike et al. SE(3) Neural Potential Fields for 6-DoF Trajectory Planning Directly from Images. IEEE IROS, 2026.",
        "Sparse Topological Maps for Navigation Using Policy Uncertainty. Submitted, CoRL, 2026.",
        "S. Ahamad, M. Ataei, V. Devabhaktuni, V. Dhiman. Omobot: a low-cost mobile robot for autonomous search and fall detection. IEEE ICAIM, 2024.",
    ],
    notes="""Here's a short list of the publications this talk draws from, for anyone who
wants to go deeper — I'm happy to share the papers and code afterward."""
),

dict(
    type="end",
    title="Thank you",
    subtitle="Questions & discussion",
    contact="Vikas Dhiman  –  vikas.dhiman@maine.edu  –  CVAR Lab, University of Maine",
    notes="""Thank you very much. I'd love to take questions — and I'm especially interested
in what problems you all here at RIT are running into with safety and learning, since I
suspect quite a few of them line up with what I've shown today."""
),

]
