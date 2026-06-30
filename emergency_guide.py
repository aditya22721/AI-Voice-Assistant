"""Emergency first aid guidance for various medical situations"""

def call_emergency_reminder():
    return "⚠️ IMPORTANT: Call emergency services (911/112/999) immediately if this is a life-threatening emergency!"

def heart_attack():
    return f"""{call_emergency_reminder()}

SYMPTOMS OF HEART ATTACK:
• Chest pain or discomfort (pressure, squeezing, fullness)
• Pain spreading to arms, neck, jaw, or back
• Shortness of breath
• Cold sweat, nausea, or lightheadedness

FIRST AID:
1. Call emergency services immediately
2. Have the person sit down and rest
3. Loosen any tight clothing
4. If the person is conscious and not allergic to aspirin, give one aspirin (chewable)
5. If the person becomes unconscious, check breathing and start CPR if needed
6. Stay with them until help arrives"""

def choking():
    return f"""{call_emergency_reminder()}

CHOKING - HEIMLICH MANEUVER (conscious person):

FOR CONSCIOUS ADULT/CHILD:
1. Stand behind the person
2. Wrap arms around their waist
3. Make a fist with one hand, place thumb side against the middle of the abdomen (above navel)
4. Grasp fist with other hand and thrust inward and upward
5. Repeat until object is expelled or person becomes unconscious

FOR INFANTS (under 1 year):
1. Lay infant face-down on your forearm, supporting head
2. Give 5 back blows between shoulder blades
3. Turn infant face-up and give 5 chest thrusts (2 fingers on center of chest)
4. Repeat until object is expelled

IF PERSON BECOMES UNCONSCIOUS:
• Start CPR immediately
• Check mouth for visible object before each breath"""

def severe_bleeding():
    return f"""{call_emergency_reminder()}

SEVERE BLEEDING:
1. Put on gloves if available
2. Apply direct pressure to the wound with a clean cloth
3. If blood soaks through, do NOT remove - add more cloth on top
4. Elevate the injured area above heart level if possible
5. Apply a tourniquet only if bleeding cannot be controlled with pressure
6. Keep the person calm and warm
7. Do NOT remove any object that is embedded in the wound"""

def minor_bleeding():
    return f"""MINOR BLEEDING:
1. Wash hands before treating the wound
2. Clean the wound with clean water
3. Apply pressure with a clean cloth until bleeding stops
4. Apply antibiotic ointment if available
5. Cover with a sterile bandage
6. Watch for signs of infection (redness, warmth, swelling, pus)"""

def burns():
    return f"""{call_emergency_reminder() if 'severe' in 'burns' else ''}

BURNS:
1. Cool the burn with running cool (not cold) water for 10-15 minutes
2. Do NOT use ice - it can cause further damage
3. Remove tight items like jewelry before swelling occurs
4. Cover the burn with a sterile, non-stick bandage
5. Do NOT break blisters
6. Do NOT apply butter, oil, or ointments
7. Seek medical attention for:
   • Burns on face, hands, feet, or genitals
   • Burns larger than your palm
   • Chemical or electrical burns
   • Burns that appear charred or have white patches"""

def fracture():
    return f"""{call_emergency_reminder()}

FRACTURE/BROKEN BONE:
1. Call emergency services if:
   • The bone is visible (open fracture)
   • The person cannot move the limb
   • There is severe pain or deformity
2. Do NOT try to straighten the limb
3. Immobilize the limb with a splint (e.g., rolled newspaper)
4. Apply cold packs wrapped in cloth to reduce swelling
5. Elevate the limb if possible
6. Watch for signs of shock (pale, clammy, rapid pulse)"""

def seizure():
    return f"""{call_emergency_reminder()}

SEIZURE:
1. Clear the area of dangerous objects
2. Do NOT restrain the person or put anything in their mouth
3. Gently turn them on their side to keep airway clear
4. Cushion their head with something soft
5. Time the seizure
6. Call emergency services if:
   • Seizure lasts more than 5 minutes
   • Multiple seizures occur
   • Person has difficulty breathing
   • Seizure occurs in water
   • Person is pregnant or has diabetes
7. After seizure, stay with them until fully conscious"""

def stroke():
    return f"""{call_emergency_reminder()}

STROKE - REMEMBER FAST:
F - Face drooping
A - Arm weakness
S - Speech difficulty
T - Time to call emergency services

FIRST AID:
1. Call emergency services immediately
2. Note the time when symptoms started
3. Keep the person calm and comfortable
4. If conscious, lay them on their side with head slightly elevated
5. Do NOT give them food, drink, or medication
6. If unconscious, check breathing and start CPR if needed"""

def head_injury():
    return f"""{call_emergency_reminder()}

HEAD INJURY:
1. Call emergency services if:
   • Loss of consciousness (even brief)
   • Confusion or disorientation
   • Severe headache
   • Vomiting
   • Seizures
   • Unequal pupil size
2. Keep the person still
3. Don't move the person (possible neck/spine injury)
4. Apply ice packs (wrapped in cloth) to reduce swelling
5. Monitor breathing and consciousness
6. Do NOT stop bleeding if skull is fractured"""

def poisoning():
    return f"""{call_emergency_reminder()}

POISONING:
1. Call poison control center (1-800-222-1222 in US) or emergency services
2. Do NOT induce vomiting unless instructed by medical professionals
3. Remove any remaining poison from mouth
4. If inhaled poison: move to fresh air immediately
5. If skin contact: remove contaminated clothing and wash skin with water
6. Keep the person calm and comfortable
7. Bring the poison container to the hospital"""

def allergic_reaction():
    return f"""{call_emergency_reminder()}

ALLERGIC REACTION - ANAPHYLAXIS:
Symptoms: Difficulty breathing, swelling, hives, dizziness, nausea

FIRST AID:
1. Use epinephrine auto-injector (EpiPen) if prescribed and available
2. Call emergency services immediately
3. Have person lie flat with legs elevated
4. Loosen tight clothing
5. Monitor breathing and consciousness
6. If unconscious, start CPR if needed"""

def unconscious():
    return f"""{call_emergency_reminder()}

UNCONSCIOUS PERSON:
1. Check responsiveness - tap and shout
2. If no response, call emergency services immediately
3. Check for breathing (look, listen, feel for 10 seconds)
4. If NOT breathing normally, start CPR:
   • 30 chest compressions (2 inches deep at 100-120/min)
   • 2 rescue breaths (if trained)
   • Continue until help arrives or person wakes up
5. If breathing normally, place in recovery position:
   • Turn on side
   • Tilt head back to keep airway open"""

def heat_stroke():
    return f"""{call_emergency_reminder()}

HEAT STROKE:
Symptoms: Hot, dry skin, confusion, rapid pulse, headache, nausea

FIRST AID:
1. Call emergency services immediately
2. Move person to cool/shaded area
3. Remove excess clothing
4. Cool rapidly with:
   • Cold water (sponge or spray)
   • Ice packs on armpits, neck, and groin
   • Fan while spraying with water
5. Do NOT give fluids if unconscious or confused"""

def sprain():
    return f"""SPRAIN - R.I.C.E.:
R - Rest the injured area
I - Ice (apply ice packs for 20 minutes every 3-4 hours)
C - Compression (wrap with elastic bandage)
E - Elevate above heart level

Seek medical attention if:
• Severe pain or swelling
• Cannot bear weight
• Deformity or numbness
• Symptoms persist beyond 3-5 days"""

def electric_shock():
    return f"""{call_emergency_reminder()}

ELECTRIC SHOCK:
1. DO NOT touch person if they are still in contact with electrical source
2. Turn off power source if possible
3. If not, use non-conductive object (wood, plastic) to separate person from source
4. Call emergency services immediately
5. Check for breathing and pulse
6. If not breathing, start CPR
7. Treat for burns"""