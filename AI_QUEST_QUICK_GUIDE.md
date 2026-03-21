# AI Quest Generation - Quick Command Reference

## In-Game Commands (Chat - Press R)

### Quest Generation Commands

**!quest | !missao | !questao**
- Generates a contextual AI quest
- Based on: World prophecy, conflicts, YOUR origin, legacy, and motivation
- Each quest is unique and tied to world narrative
- Example: "Os guardiões antigos precisam de alguém com sua origem..."

**!profecia | !prophecy**
- Generates a quest specifically about the world prophecy
- Helps you move toward fulfilling the prophecy
- Higher difficulty and rewards
- Example: "A profecia diz que você quebrará a sétima selagem..."

**!conflito | !conflict**
- Generates a quest about the main world conflict
- Involves you in factional disputes
- Moral choices with consequences
- Example: "Os dragões rivais reclamam seu apoio..."

### History/Stats Commands (From Previous System)

**!history | !historico**
- View all your action statistics
- Shows total actions, action types, distance traveled, HP reached

**!stats | !estatisticas**  
- Show statistical summary of your gameplay

**!recent | !recentes**
- View your last 15 actions with positions and HP

---

## How Quests Connect to YOUR Story

### Your Origin + Quest
If you're from "ruins and ancient plantations":
→ Quests about exploring ancient structures, finding artifacts

If you're from "merchant roads and villages":
→ Quests about trading, meeting NPCs, political intrigue

**Your quest describes how your background makes you the perfect candidate.**

### Your Motivation + Quest
If motivated by "gathering 7 sacred keys":
→ Quests that offer discovery of keys
→ Prophecy steps toward that goal

If motivated by "uniting rival villages":
→ Quests that broker peace or reveal common enemies

**Your quest reinforces WHY you're the right person for this.**

### Your Secret + Quest
If carrying "an ancient symbol that reacts to mana":
→ Quests where that symbol becomes useful
→ Ancient places that respond to it

**Your secret becomes relevant to the quest.**

---

## How Quests Connect to YOUR WORLD

### World Prophecy
```
World has: "You will shatter the seventh seal and release chaos"
Your quest might: "Find 3 ancient guardians to learn how to handle chains of power"
```

### Main Conflict
```
World has: "Battle between Rival Dragons"
Your quest might: "Collect mana samples from BOTH dragons"
                  "Choose a side in the conflict"
                  "Negotiate peace between them"
```

### Raphael's Condition
```
World has: "Raphael is divided between mercy and justice"
Your quest might: "A moral choice: save innocents OR punish evil"
                  "Help Raphael find balance"
```

### Mystical Place
```
World has: "Forgotten library in crystal caves"
Your quest might: "Search the library for ancient knowledge"
                  "Retrieve a book for a scholar"
```

---

## Examples

### Example 1: Cartographer's Descendant
```
WORLD:
- Prophecy: "You will break bonds across empires"
- Conflict: "Border disputes between three kingdoms"
- Legend: "Ancient maps hold secrets to peace"

YOUR PROFILE:
- Origin: "came from a family of northern cartographers"
- Legacy: "heir to ancient explorer knowledge"
- Motivation: "complete your ancestors' maps"
- Secret: "carry an old compass that points to destiny"

GENERATED QUEST:
"As inheritor of cartographic knowledge, you're summoned.
 The three warring kingdoms would accept a neutral party
 who could map and connect their territories peacefully.
 Explore and document the 5 border regions."

REWARDS: Gold for mapping, reputation with all kingdoms
```

### Example 2: Prophecy-Driven
```
WORLD PROPHECY:
"Bentoira will shatter the seventh seal and liberate chaos"

YOUR PROFILE:
- Name: Bentoira
- Motivation: "live up to a destiny"

PROPHECY QUEST:
"The prophecy Raphael whispers about you returns to mind.
 To shatter the seventh seal, you must first understand
 the Seven Guardian Councils. Find the first guardian."

DIFFICULTY: ⭐⭐⭐⭐
REWARDS: +2000 EXP, spiritual awakening toward prophecy
```

### Example 3: Conflict Involvement
```
WORLD CONFLICT:
"Battle between Blue and Gold Dragons over domain"

YOUR PROFILE:
- Origin: "learned diplomacy in divided lands"
- Motivation: "understand all perspectives"

CONFLICT QUEST:
"Both dragons recognize your gift for understanding.
 They request neutral analysis: gather mana samples
 from BOTH of their territories and report findings.
 Your choice will influence the conflict's outcome."

DIFFICULTY: ⭐⭐⭐⭐
REWARDS: +1500 EXP, both dragons owe you a favor
```

---

## Tips for Best Experience

1. **Type !quest multiple times** - Each generates a NEW unique quest
   - No recycling; hundreds of possible quests based on context

2. **Try !profecia and !conflito** - Different perspectives on world lore
   - Prophecy quests offer higher stakes and rewards
   - Conflict quests offer moral choices

3. **Your profile shapes quests** - Changing how you play might generate different quest themes
   - High morale → quests about mercy and cooperation
   - Low morale → quests about redemption and balance

4. **Quests change with game progress** - As you level up and change:
   - Quests become more appropriate to your new power level
   - World conflicts might evolve based on your choices
   - Prophecy steps unlock as you progress

5. **Check your action history** - Use !history to see your playstyle
   - Helps you understand what kind of quests you're generating

---

## Behind the Scenes

### What Happens When You Request a Quest

1. **System Extracts Context**
   - Your full profile (origin, legacy, motivation, secret)
   - World lore (prophecy, conflicts, legends, eras)
   - Raphael's observations of you
   - Current game state (HP, food, progress)

2. **AI Prompt Constructed**
   - All context sent to Ollama
   - Instructions to make meaningful, narrative-rich quest
   - Temperature set for balanced creativity (0.7)

3. **Ollama Generates Quest**
   - Considers all context
   - Creates unique quest tied to YOUR story and WORLD lore
   - Returns JSON with quest details

4. **Quest Validated & Displayed**
   - Checked for proper format
   - Shown in chat with title, description, difficulty, rewards
   - Added to your quest log

5. **Offline Fallback**
   - If Ollama unavailable, still generates contextual quest
   - Uses templates that still consider your profile
   - No game crash or disconnection

---

## Troubleshooting

**"Raphael is silent about quests"**
- Try adding text after the command, like "hey raphael" or "please"
- The command might not be recognized; exact commands are: !quest, !missao, !questao

**Quest seems generic**
- This means Ollama might not be running
- System is using fallback (still uses world context, just not as creative)
- Start Ollama server: `ollama serve`

**Want more difficult quests?**
- Keep playing and leveling
- Generated quests scale with your progress
- Conflict and prophecy quests are harder by default

**Want specific quest types?**
- !quest = General contextual (all types)
- !profecia = Prophecy-focused (high difficulty)
- !conflito = Conflict-involved (moral choices)

---

## Next Steps (Future Enhancements)

Coming soon:
- **Quest Chains** - Multi-step quests toward prophecy fulfillment
- **NPC Quests** - Each NPC generates their own contextual quests
- **Legacy Quests** - Special quests based on your family history
- **World Events** - Events automatically spawn related quests
- **Quest Rewards** - Dynamic rewards based on YOUR skills

Your quests aren't just tasks anymore — they're **chapters of your unique story in a world that knows who you are**.
