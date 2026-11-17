"""David Burns' cognitive restructuring methods and belief testing techniques.

Based on David D. Burns, M.D. ("Feeling Good: The New Mood Therapy",
"When Panic Attacks", "Feeling Great" / TEAM-CBT).
Strictly NO emojis. Clean ASCII typography.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class BurnsMethod:
    code: str
    name: str
    category: str
    summary: str
    description: str
    when_to_use: str
    guided_prompts: List[str]
    example: str

BURNS_METHODS: Dict[str, BurnsMethod] = {
    "double_standard": BurnsMethod(
        code="double_standard",
        name="The Double-Standard Technique",
        category="Compassion & Perspective",
        summary="Talk to yourself with the same compassion and realism you would offer a dear friend.",
        description=(
            "We frequently judge ourselves with brutal harshness while treating others with empathy and reason. "
            "Ask yourself: Would I say this to a friend or colleague in the exact same situation? "
            "If not, why am I applying a cruel double standard to myself?"
        ),
        when_to_use="When experiencing severe self-criticism, guilt, shame, or feeling like an imposter.",
        guided_prompts=[
            "If a close friend came to you with this exact problem, would you say these harsh words to them?",
            "What would you tell your friend to support, comfort, and guide them objectively?",
            "Why do you hold yourself to a punitive standard that you would never impose on someone else?",
            "How can you apply that same friend-advice to yourself right now?",
        ],
        example=(
            "Thought: 'I made a mistake in the report. I am completely stupid.'\n"
            "Double Standard Test: If a colleague made a typo, I would say: 'It's a minor error in a 40-page deck; "
            "we'll fix it in 2 minutes. You did great work overall.' I deserve that same objective standard."
        ),
    ),
    "cost_benefit": BurnsMethod(
        code="cost_benefit",
        name="Cost-Benefit Analysis (Advantages & Disadvantages)",
        category="Motivation & Decision Making",
        summary="List the advantages and disadvantages of holding onto a negative thought, belief, or habit.",
        description=(
            "Negative thoughts and rigid rules (e.g. 'I must be 100% perfect') survive because we unconsciously "
            "believe they protect us or make us productive. Weighing the concrete costs against the benefits "
            "reveals that the costs almost always overwhelmingly outweigh the benefits."
        ),
        when_to_use="When dealing with perfectionism, procrastination, anger, guilt, or reluctance to let go of a thought.",
        guided_prompts=[
            "What are the perceived advantages of holding this thought or belief? (How do you think it helps you?)",
            "What are the real disadvantages and costs? (Emotional toll, stress, relationship strain, burnout?)",
            "Looking at the two sides objectively, does this belief cost you more than it gives you?",
        ],
        example=(
            "Belief: 'I must work 14 hours a day without rest or I am a failure.'\n"
            "Advantages: Keeps me on guard, avoids feeling lazy (score: 20%).\n"
            "Disadvantages: Chronic exhaustion, insomnia, anxiety, reduced creativity, strained relationships (score: 80%).\n"
            "Conclusion: The belief undermines the very success it claims to protect."
        ),
    ),
    "downward_arrow": BurnsMethod(
        code="downward_arrow",
        name="The Downward / Vertical Arrow Technique",
        category="Core Belief Deconstruction",
        summary="Uncover deep-seated silent assumptions and core schemas by repeatedly asking 'If that were true, what would it mean to me?'.",
        description=(
            "Surface automatic thoughts are often symptoms of deeper 'silent assumptions' (e.g., 'My worth depends on being loved by everyone'). "
            "By drawing a downward arrow under the thought and asking 'If that were true, what would that mean to me? Why would that be a tragedy?', "
            "you pinpoint the core belief and can test its foundation."
        ),
        when_to_use="When surface thoughts seem disproportionately terrifying, or when anxiety/depression has persistent underlying roots.",
        guided_prompts=[
            "If this automatic thought were 100% true, what would that mean about you as a person?",
            "And if that were true, what is the worst consequence that would happen next?",
            "What silent rule or assumption ('I must...', 'I can only be happy if...') is driving this reaction?",
            "Is that underlying assumption realistic, healthy, and universally valid?",
        ],
        example=(
            "Surface Thought: 'I might get criticized during the review.'\n"
            "-> If true, what does that mean? 'It means I am not good at my job.'\n"
            "-> And if that were true? 'Then my boss will lose respect for me and I could get fired.'\n"
            "-> And if that were true? 'Then I am a worthless human being who cannot take care of himself.'\n"
            "Core Assumption Identified: 'My worth as a human depends entirely on flawless job approval.'"
        ),
    ),
    "shades_of_grey": BurnsMethod(
        code="shades_of_grey",
        name="Thinking in Shades of Grey (The Continuum Technique)",
        category="Nuance & Perspective",
        summary="Plot situations and performance on a 0-100 continuum rather than viewing them in binary black-and-white terms.",
        description=(
            "All-or-Nothing thinking forces you to categorize everything as either a 100% triumph or a 0% disaster. "
            "Real-world events and human endeavors exist on a continuum. Even on your worst day, your performance is rarely 0%, "
            "and imperfection does not equate to total failure."
        ),
        when_to_use="When trapped in black-and-white thinking, perfectionism, or experiencing intense defeat after a minor setback.",
        guided_prompts=[
            "Are you viewing this outcome as either 100% perfect or 0% failure?",
            "What would absolute zero (0%) look like in this situation? (e.g. not even showing up, setting the building on fire)",
            "What would 100% look like? (Flawless perfection, which rarely exists in human life)",
            "Where does your actual outcome realistically land on a scale from 0 to 100? (e.g. 65%, 80%)",
        ],
        example=(
            "Thought: 'My speech was a total disaster because I paused for 5 seconds on slide 3.'\n"
            "Continuum: 0% = Fainting or saying nothing. 100% = World-class oratorical perfection.\n"
            "Actual: I conveyed 90% of the material clearly and answered questions well. Realistic score: 82/100."
        ),
    ),
    "semantic_method": BurnsMethod(
        code="semantic_method",
        name="The Semantic Method",
        summary="Substitute emotionally charged, rigid language ('should', 'must', 'have to') with realistic preferences.",
        category="Linguistic & Cognitive Reframing",
        description=(
            "'Should' statements produce guilt, shame, and rebellious procrastination. When you tell yourself 'I should have known better', "
            "you imply you possess omniscience. Replace 'should', 'must', and 'ought' with 'It would have been preferable if', "
            "'I would like to', or 'It would be beneficial for me to'."
        ),
        when_to_use="When experiencing guilt, resentment, procrastination, or anger driven by unwritten rigid rules.",
        guided_prompts=[
            "Identify the 'should', 'must', 'ought to', or 'have to' in your thought.",
            "Who created this law? Is it physically possible to adhere to it 100% of the time?",
            "Rewrite the statement replacing 'should' with: 'It would be preferable if...', 'I want to...', or 'I choose to...'.",
            "Notice how the emotional tone shifts from self-flagellation to conscious preference.",
        ],
        example=(
            "Original: 'I should never feel anxious when meeting new clients.'\n"
            "Semantic Reframe: 'I would prefer to feel calm, but feeling some anxiety is natural and human. "
            "I can still communicate effectively even with elevated adrenaline.'"
        ),
    ),
    "define_terms": BurnsMethod(
        code="define_terms",
        name="Define Terms",
        category="Clarity & Logic",
        summary="Demand precise operational definitions for vague derogatory labels like 'loser', 'failure', or 'incompetent'.",
        description=(
            "Derogatory labels dissolve when scrutinized under basic logic. What is a 'loser'? Someone who always loses at everything? "
            "Does such a biological creature exist? When you define your terms, you discover that labels describe non-existent myths, "
            "while human beings are complex, evolving organisms who perform specific behaviors."
        ),
        when_to_use="When labeling yourself or others ('I'm an idiot', 'I'm a failure', 'He is a jerk').",
        guided_prompts=[
            "What derogatory label did you attach to yourself or someone else?",
            "How would you objectively and rigorously define that term in a dictionary?",
            "Can any living human being meet that absolute definition 100% of the time?",
            "What is the specific, factual behavior you are actually trying to describe?",
        ],
        example=(
            "Label: 'I am a failure.'\n"
            "Definition: A failure would be a person who fails at 100% of all actions throughout their lifespan, including breathing, eating, walking, and speaking.\n"
            "Reality: That is absurd. I failed at this specific coding challenge, which is an event, not an identity."
        ),
    ),
    "reattribution": BurnsMethod(
        code="reattribution",
        name="Reattribution / The Responsibility Pie Chart",
        category="Attribution & Responsibility",
        summary="Brainstorm all contributing factors to an undesirable outcome and distribute percentages realistically.",
        description=(
            "Personalization causes you to assume 100% blame for negative events. In reality, almost every complex outcome "
            "is influenced by multiple factors: external environment, other people's choices, timing, biology, past history, and randomness. "
            "Distributing responsibility across a pie chart dispels irrational guilt."
        ),
        when_to_use="When overwhelmed with guilt, self-blame, or conversely, when blaming others entirely without examining your part.",
        guided_prompts=[
            "List all the distinct factors and actors that contributed to this outcome (e.g. circumstances, other people, timing, lack of information, stress).",
            "What percentage of the overall outcome was realistically due to factors beyond your direct control?",
            "What percentage represents your specific, realistic portion of responsibility?",
            "What constructive step can you take regarding your portion, without taking responsibility for the rest?",
        ],
        example=(
            "Scenario: The project missed the quarterly deadline. Thought: 'It's all my fault.'\n"
            "Responsibility Pie:\n"
            "  - Client changed requirements at the last minute: 40%\n"
            "  - Two team members were sick with flu: 25%\n"
            "  - Budget constraints prevented hiring contractors: 15%\n"
            "  - My initial timeline estimation was overly optimistic: 20%\n"
            "Insight: I own 20% of the timeline issue to improve next time, but I am not 100% at fault."
        ),
    ),
    "experimental_technique": BurnsMethod(
        code="experimental_technique",
        name="The Experimental Technique (Empirical Testing)",
        category="Action & Behavioral Verification",
        summary="Design a small, concrete real-world behavioral experiment to test whether your negative thought is factually accurate.",
        description=(
            "Instead of arguing endlessly in your mind, treat your negative thought as a scientific hypothesis. "
            "Design a small, low-risk test to observe what actually happens versus what you predict will happen."
        ),
        when_to_use="When paralyzed by fortune-telling, mind reading, avoidance, or catastrophizing.",
        guided_prompts=[
            "State your negative prediction as a clear, testable scientific hypothesis: 'If I do X, then catastrophic Y will occur.'",
            "What is a simple, safe experiment you can perform to test this?",
            "What is your predicted outcome and confidence level (0-100%)?",
            "Run the experiment. What were the actual observed empirical results?",
        ],
        example=(
            "Hypothesis: 'If I eat lunch alone in the cafeteria, people will stare at me and think I am an outcast (90% belief).'\n"
            "Experiment: Eat lunch alone for 20 minutes and count how many people actually stare or point.\n"
            "Outcome: Exactly zero people paid attention; everyone was looking at their phones or talking to their friends.\n"
            "Belief drop: Dropped to 5%."
        ),
    ),
    "what_if_decatastrophize": BurnsMethod(
        code="what_if_decatastrophize",
        name="The 'What-If' Technique (Decatastrophizing)",
        category="Anxiety & Worst-Case Mastery",
        summary="Follow your catastrophic fear to its ultimate conclusion and formulate a concrete coping strategy.",
        description=(
            "Anxiety thrives on vague, terrifying ambiguities ('What if I lose everything?!'). "
            "By systematically asking 'And if that happened, what is the realistic worst? What would I actually do? How would I cope?', "
            "you discover that you possess coping resources even in difficult circumstances."
        ),
        when_to_use="When gripped by panic, irrational worries, health anxiety, or dread of worst-case scenarios.",
        guided_prompts=[
            "What is the exact worst-case catastrophe you are fearing?",
            "If that worst-case scenario actually happened, what concrete actions would you take in the first 24-48 hours?",
            "Who or what resources could support you in that situation?",
            "Have you or others survived difficult setbacks before? Would your life eventually recover?",
        ],
        example=(
            "Fear: 'What if I fail this client pitch?'\n"
            "Worst Case: The client says no and hires a competitor.\n"
            "Coping Plan: I would ask for feedback, review our weak points, pitch the other 3 prospective clients in the pipeline, and refine the offer.\n"
            "Conclusion: It would be disappointing, but completely survivable and non-lethal."
        ),
    ),
    "positive_reframing": BurnsMethod(
        code="positive_reframing",
        name="Positive Reframing (TEAM-CBT Secret)",
        category="Values & Motivation",
        summary="Identify the positive values, strengths, and noble intentions revealed by your negative thought or emotion.",
        description=(
            "Before challenging a negative emotion, honor what it reveals about your core values. "
            "Anxiety shows you care deeply about doing well. Guilt shows you have a strong moral compass. "
            "Anger shows you value fairness. Once you appreciate the noble motive, you can choose to keep the positive value "
            "while letting go of the crippling suffering."
        ),
        when_to_use="When feeling stuck, resistant to change, or beating yourself up for experiencing negative emotions.",
        guided_prompts=[
            "What does this negative emotion or concern reveal about what you deeply care about?",
            "What positive virtues, ethics, or strengths does this thought reflect? (e.g. conscientiousness, loyalty, dedication)",
            "How can you honor those positive virtues without subjecting yourself to misery and cognitive distortions?",
        ],
        example=(
            "Emotion: Deep anxiety before delivering a presentation.\n"
            "Positive Reframing: This anxiety shows that I care profoundly about my team, value providing accurate information, and take my responsibilities seriously.\n"
            "Shift: I can keep 100% of my dedication and care without the debilitating terror."
        ),
    ),
}
