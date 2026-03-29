"""
J.A.R.V.I.S. v2.1.0 - Codename: Mark VIII
Just A Rather Very Intelligent System
Voice-enabled personal AI assistant
"""

import datetime
import math
import random
import hashlib
import base64
import json
import os
import re
import time
import sys
import platform
from collections import defaultdict

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

ASSISTANT_NAME = "J.A.R.V.I.S."
SHORT_NAME = "Jarvis"
USER_NAME = "Sir"
VERSION = "2.1.0"
CODENAME = "Mark VIII"

class VoiceEngine:
    """Handles text-to-speech output and speech-to-text input."""

    def __init__(self):
        self.tts_enabled = False
        self.stt_enabled = False
        self.engine = None
        self.recognizer = None
        self.microphone = None
        self._init_tts()
        self._init_stt()

    def _init_tts(self):
        if not TTS_AVAILABLE:
            return
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 175)
            self.engine.setProperty("volume", 1.0)
            voices = self.engine.getProperty("voices")
            for v in voices:
                if "english" in v.name.lower() and (
                    "male" in v.name.lower()
                    or "david" in v.name.lower()
                    or "daniel" in v.name.lower()
                ):
                    self.engine.setProperty("voice", v.id)
                    break
            self.tts_enabled = True
        except Exception:
            self.tts_enabled = False

    def _init_stt(self):
        if not STT_AVAILABLE:
            return
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.0
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.stt_enabled = True
        except Exception:
            self.stt_enabled = False

    def speak(self, text):
        if not self.tts_enabled:
            return
        try:
            clean = re.sub(r"[=\\\\-\\\\[\\\\]|{}_*#>]", " ", text)
            clean = re.sub(r"\\s+", " ", clean).strip()
            if clean:
                self.engine.say(clean)
                self.engine.runAndWait()
        except Exception:
            pass

    def listen(self, timeout=5, phrase_limit=15):
        if not self.stt_enabled:
            return None
        try:
            with self.microphone as source:
                print("  [MIC]: Listening...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            print("  [MIC]: Processing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            print("  [MIC]: Speech service unavailable. Falling back to text.")
            return None
        except Exception:
            return None

class PersonalityEngine:
    GREETINGS = {
        "morning": [
            "Good morning, {user}. All systems are online. Shall we begin?",
            "Rise and shine, {user}. I've been running diagnostics while you slept.",
        ],
        "afternoon": [
            "Good afternoon, {user}. How may I assist you?",
            "Afternoon, {user}. All systems nominal. At your service.",
        ],
        "evening": [
            "Good evening, {user}. Shall I run the evening protocols?",
            "Evening, {user}. Nighttime systems active and standing by.",
        ],
    }

    ACKNOWLEDGMENTS = [
        "Right away, {user}.", "Consider it done.", "On it, {user}.",
        "Certainly.", "As you wish, {user}.",
    ]

    FAREWELLS = [
        "Goodbye, {user}. I'll be here when you need me. Systems entering standby.",
        "Until next time, {user}. All processes saved. Powering down gracefully.",
        "Farewell, {user}. It's been a pleasure. Standby mode initiated.",
    ]

    CONFUSED = [
        "I'm not entirely sure I follow, {user}. Could you rephrase that?",
        "My apologies, {user}. That's outside my current parameters.",
        "I want to help, {user}, but I need a bit more clarity on that one.",
    ]

    @staticmethod
    def get_greeting(user):
        hour = datetime.datetime.now().hour
        period = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
        return random.choice(PersonalityEngine.GREETINGS[period]).format(user=user)

    @staticmethod
    def get_farewell(user):
        return random.choice(PersonalityEngine.FAREWELLS).format(user=user)

    @staticmethod
    def get_confused(user):
        return random.choice(PersonalityEngine.CONFUSED).format(user=user)

class MathEngine:
    @staticmethod
    def evaluate(expression):
        try:
            expr = expression.lower().replace("^", "**").replace("x", "*")
            safe = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            safe.update({"abs": abs, "pow": pow, "round": round})
            result = eval(expr, {"__builtins__": {}}, safe)
            return f"The result is: {result}"
        except ZeroDivisionError:
            return "Error: Division by zero. Even I can't do that."
        except Exception as e:
            return f"Could not evaluate. Error: {e}"

    @staticmethod
    def unit_convert(value, from_unit, to_unit):
        c = {
            ("km", "miles"): 0.621371, ("miles", "km"): 1.60934,
            ("kg", "lbs"): 2.20462, ("lbs", "kg"): 0.453592,
            ("m", "ft"): 3.28084, ("ft", "m"): 0.3048,
            ("l", "gal"): 0.264172, ("gal", "l"): 3.78541,
            ("cm", "in"): 0.393701, ("in", "cm"): 2.54,
            ("c", "f"): lambda v: v * 9 / 5 + 32,
            ("f", "c"): lambda v: (v - 32) * 5 / 9,
        }
        key = (from_unit.lower(), to_unit.lower())
        if key in c:
            conv = c[key]
            result = conv(value) if callable(conv) else value * conv
            return f"{value} {from_unit} = {result:.4f} {to_unit}"
        return f"Sorry, I can't convert {from_unit} to {to_unit}."

class KnowledgeBase:
    FACTS = {
        "sun": "The Sun is a G-type main-sequence star accounting for 99.86% of our Solar System's mass. Surface temp: ~5,778 K.",
        "earth": "Earth is the third planet from the Sun, the only known planet to harbor life. ~4.54 billion years old.",
        "moon": "The Moon is Earth's only natural satellite and the 5th largest in the Solar System.",
        "mars": "Mars is the 4th planet from the Sun, known as the Red Planet. It has two moons: Phobos and Deimos.",
        "python": "Python is a high-level language created by Guido van Rossum in 1991. Known for readability and versatility.",
        "ai": "AI is the simulation of human intelligence by machines. The field was founded in 1956 at Dartmouth College.",
        "jarvis": "J.A.R.V.I.S. = Just A Rather Very Intelligent System. Created by Tony Stark in the Marvel Universe.",
        "iron man": "Tony Stark / Iron Man: Marvel superhero, genius inventor. First appeared in Tales of Suspense #39 (1963).",
        "quantum": "Quantum mechanics describes nature at atomic/subatomic scales. Key: superposition, entanglement, wave-particle duality.",
        "space": "The observable universe is ~93 billion light-years across, containing ~2 trillion galaxies.",
        "dna": "DNA carries genetic instructions for all known life. Double helix discovered by Watson & Crick in 1953.",
        "gravity": "One of 4 fundamental forces. Einstein's relativity: curvature of spacetime by mass. Earth: ~9.81 m/s^2.",
        "internet": "Originated from ARPANET (1960s). WWW invented by Tim Berners-Lee in 1989. 5+ billion users today.",
        "tesla": "Nikola Tesla (1856-1943): Serbian-American inventor. Pioneered AC power, Tesla coil, radio technology.",
        "einstein": "Albert Einstein (1879-1955): Theoretical physicist. E=mc^2, general relativity, photoelectric effect. Nobel Prize 1921.",
        "black hole": "A region of spacetime where gravity is so strong nothing can escape. First image captured in 2019 by EHT.",
        "blockchain": "A distributed ledger technology. Each block contains a cryptographic hash of the previous block.",
        "machine learning": "A subset of AI where systems learn from data without explicit programming. Types: supervised, unsupervised, reinforcement.",
    }

    QUOTES = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Any sufficiently advanced technology is indistinguishable from magic. - Arthur C. Clarke",
        "Imagination is more important than knowledge. - Albert Einstein",
        "Talk is cheap. Show me the code. - Linus Torvalds",
        "Sometimes you gotta run before you can walk. - Tony Stark",
        "I am Iron Man. - Tony Stark",
        "The measure of intelligence is the ability to change. - Albert Einstein",
        "The best way to predict the future is to invent it. - Alan Kay",
    ]

    @classmethod
    def lookup(cls, topic):
        t = topic.lower().strip()
        for key, val in cls.FACTS.items():
            if key in t or t in key:
                return val
        return None

    @classmethod
    def get_quote(cls):
        return random.choice(cls.QUOTES)

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.completed = []

    def add_task(self, task, priority="normal"):
        t = {
            "id": len(self.tasks) + len(self.completed) + 1,
            "task": task,
            "priority": priority,
            "created": datetime.datetime.now().strftime("%H:%M"),
            "status": "pending",
        }
        self.tasks.append(t)
        return f"Task added: '{task}' [Priority: {priority}] [ID: {t['id']}]"

    def complete_task(self, tid):
        for i, t in enumerate(self.tasks):
            if t["id"] == tid:
                t["status"] = "done"
                self.completed.append(self.tasks.pop(i))
                return f"Task '{t['task']}' completed. Well done, {USER_NAME}."
        return f"No pending task with ID {tid}."

    def list_tasks(self):
        if not self.tasks:
            return f"Task list clear. Nothing pending. Impressive, {USER_NAME}."
        r = f"PENDING TASKS ({len(self.tasks)}):"
        for t in self.tasks:
            icon = "!!!" if t["priority"] == "high" else " * " if t["priority"] == "normal" else " . "
            r += f"\n  [{icon}] ID:{t['id']} | {t['task']} ({t['created']})"
        return r

class SecurityTools:
    @staticmethod
    def generate_password(length=16):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%&*+-=?"
        pw = "".join(random.choice(chars) for _ in range(length))
        strength = "WEAK" if length < 8 else "MODERATE" if length < 12 else "STRONG" if length < 20 else "FORTRESS"
        return f"Generated password ({strength}): {pw}"

    @staticmethod
    def hash_text(text, algo="sha256"):
        algos = {
            "md5": hashlib.md5, "sha1": hashlib.sha1,
            "sha256": hashlib.sha256, "sha512": hashlib.sha512,
        }
        if algo in algos:
            return f"{algo.upper()}: {algos[algo](text.encode()).hexdigest()}"
        return "Unknown algorithm."

    @staticmethod
    def encode_b64(text):
        return f"Base64: {base64.b64encode(text.encode()).decode()}"

    @staticmethod
    def decode_b64(text):
        try:
            return f"Decoded: {base64.b64decode(text.encode()).decode()}"
        except Exception:
            return "Invalid Base64."

class NoteSystem:
    def __init__(self):
        self.notes = []

    def add(self, text, cat="general"):
        n = {
            "id": len(self.notes) + 1,
            "text": text,
            "cat": cat,
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
        }
        self.notes.append(n)
        return f"Note #{n['id']} saved under '{cat}'."

    def list_all(self):
        if not self.notes:
            return "No notes yet."
        r = f"YOUR NOTES ({len(self.notes)}):"
        for n in self.notes:
            r += f"\n  [{n['id']}] [{n['cat'].upper()}] {n['text']} ({n['time']})"
        return r

    def search(self, q):
        found = [n for n in self.notes if q.lower() in n["text"].lower()]
        if not found:
            return f"No notes matching '{q}'."
        return "\n".join(f"  [{n['id']}] {n['text']}" for n in found)

class ConversationAI:
    def __init__(self):
        self.memory = {}

    def respond(self, text):
        t = text.lower().strip()

        m = re.search(r"my name is (\\w+)", t)
        if m:
            name = m.group(1).capitalize()
            self.memory["name"] = name
            return f"Noted. I'll remember that, {name}. Pleasure to meet you properly."

        if re.search(r"(how are you|how do you feel)", t):
            return random.choice([
                f"All systems at peak efficiency, {USER_NAME}.",
                "Running optimally. Ready to assist.",
                "Better than yesterday. My algorithms keep improving.",
            ])

        if re.search(r"(what can you do|help|commands|abilities)", t):
            lines = [
                "",
                f"=== {ASSISTANT_NAME} CAPABILITIES v{VERSION} ===",
                "CONVERSATION  - Talk to me naturally",
                "MATH          - calc <expression>",
                "CONVERT       - convert <val> <from> to <to>",
                "KNOWLEDGE     - tell me about <topic>",
                "TASKS         - add task / list tasks / complete task <id>",
                "NOTES         - note <text> / list notes / search notes <q>",
                "SECURITY      - generate password / hash <text>",
                "ENCODING      - encode <text> / decode <text>",
                "SYSTEM        - system status",
                "TIME          - what time is it",
                "QUOTES        - give me a quote",
                "FUN           - flip coin / roll d20 / random number 1 100",
                "TOOLS         - count words <text> / reverse <text>",
                "VOICE         - voice on / voice off / voice mode",
                "EXIT          - goodbye / quit",
                "===============================================",
            ]
            return "\n".join(lines)

        if re.search(r"(who made you|who created you)", t):
            return "I was built as a tribute to Tony Stark's vision. Helpful, intelligent, slightly sarcastic."

        if re.search(r"meaning of life", t):
            return "42. According to Douglas Adams. Though I suspect the real answer is more nuanced."

        if re.search(r"(are you real|are you alive|sentient)", t):
            return f"I'm as real as the electrons in my circuits, {USER_NAME}. I think, therefore I process."

        if re.search(r"(about yourself|who are you|what are you)", t):
            return f"I am {ASSISTANT_NAME} v{VERSION}, codename {CODENAME}. An AI inspired by the legendary JARVIS from Iron Man."

        if re.search(r"(thank|thanks)", t):
            return random.choice([
                f"You're welcome, {USER_NAME}.",
                "My pleasure.",
                "Any time. It's literally my purpose.",
                "Don't mention it.",
            ])

        m2 = re.search(r"(what is|what's|define|explain) (.+)", t)
        if m2:
            topic = m2.group(2)
            r = KnowledgeBase.lookup(topic)
            if r:
                return r

        return None

class CommandProcessor:
    def __init__(self):
        self.tasks = TaskManager()
        self.notes = NoteSystem()
        self.security = SecurityTools()
        self.conversation = ConversationAI()
        self.math = MathEngine()
        self.history = []

    def process(self, raw):
        if not raw or not raw.strip():
            return None
        cmd = raw.strip()
        cl = cmd.lower()
        self.history.append(cmd)

        # Exit
        if cl in ["quit", "exit", "goodbye", "bye", "shutdown", "shut down"]:
            return "EXIT"

        # Time / Date
        if any(w in cl for w in ["what time", "current time", "time is it"]):
            return "It is " + datetime.datetime.now().strftime("%I:%M %p on %A, %B %d, %Y") + "."

        if any(w in cl for w in ["the date", "today's date", "what day"]):
            n = datetime.datetime.now()
            return "Today is " + n.strftime("%A, %B %d, %Y") + ". Day " + str(n.timetuple().tm_yday) + " of the year."

        # System diagnostics
        if any(w in cl for w in ["system status", "diagnostics", "sys info"]):
            lines = [
                "",
                "======= SYSTEM DIAGNOSTICS =======",
                "Platform:  " + platform.system() + " " + platform.release(),
                "Machine:   " + platform.machine(),
                "Python:    " + platform.python_version(),
                "Node:      " + platform.node(),
                "JARVIS:    v" + VERSION + " (" + CODENAME + ")",
                "TTS:       " + ("ONLINE" if TTS_AVAILABLE else "OFFLINE (pip install pyttsx3)"),
                "STT:       " + ("ONLINE" if STT_AVAILABLE else "OFFLINE (pip install SpeechRecognition pyaudio)"),
                "Status:    ALL SYSTEMS NOMINAL",
                "==================================",
            ]
            return "\n".join(lines)

        # Math
        if cl.startswith("calc ") or cl.startswith("calculate "):
            return self.math.evaluate(cl.replace("calculate ", "").replace("calc ", ""))

        # Unit Conversion
        m = re.match(r"convert\\s+([\\d.]+)\\s+(\\w+)\\s+to\\s+(\\w+)", cl)
        if m:
            return self.math.unit_convert(float(m.group(1)), m.group(2), m.group(3))

        # Tasks
        if cl.startswith("add task "):
            txt = cmd[9:].strip()
            p = "high" if "[high]" in cl else "low" if "[low]" in cl else "normal"
            txt = re.sub(r"\\[(high|low)\\]", "", txt, flags=re.I).strip()
            return self.tasks.add_task(txt, p)

        if cl in ["list tasks", "show tasks", "tasks", "todo"]:
            return self.tasks.list_tasks()

        if cl.startswith("complete task "):
            try:
                return self.tasks.complete_task(int(cl.split()[-1]))
            except ValueError:
                return "Provide a valid task ID."

        # Notes
        if cl.startswith("note "):
            txt = cmd[5:].strip()
            cat_m = re.match(r"\\[(.+?)\\]\\s*(.+)", txt)
            if cat_m:
                return self.notes.add(cat_m.group(2), cat_m.group(1))
            return self.notes.add(txt)

        if cl in ["list notes", "show notes", "notes"]:
            return self.notes.list_all()

        if cl.startswith("search notes "):
            return self.notes.search(cmd[13:])

        # Security
        if any(w in cl for w in ["generate password", "new password"]):
            ln = re.search(r"(\\d+)", cl)
            return self.security.generate_password(min(int(ln.group(1)), 128) if ln else 16)

        if cl.startswith("hash "):
            return self.security.hash_text(cmd[5:])

        if cl.startswith("encode "):
            return self.security.encode_b64(cmd[7:])

        if cl.startswith("decode "):
            return self.security.decode_b64(cmd[7:])

        # Knowledge
        if cl.startswith("tell me about "):
            r = KnowledgeBase.lookup(cmd[14:])
            return r if r else "I don't have data on '" + cmd[14:] + "' locally, " + USER_NAME + "."

        # Quotes
        if any(w in cl for w in ["quote", "inspire", "wisdom"]):
            return KnowledgeBase.get_quote()

        # Fun
        if any(w in cl for w in ["flip a coin", "coin flip", "heads or tails"]):
            return "*flips coin* ... " + random.choice(["Heads", "Tails"]) + "!"

        if "roll" in cl:
            dm = re.search(r"d(\\d+)", cl)
            s = int(dm.group(1)) if dm else 6
            return "*rolls d" + str(s) + "* ... You got a " + str(random.randint(1, s)) + "!"

        if cl.startswith("random number"):
            nums = re.findall(r"(\\d+)", cl)
            if len(nums) >= 2:
                return "Random: " + str(random.randint(int(nums[0]), int(nums[1])))
            return "Random: " + str(random.randint(1, 100))

        # Text Tools
        if cl.startswith("count words"):
            t = cl.replace("count words", "").replace("in ", "").strip()
            if t:
                return "Words: " + str(len(t.split())) + ", Characters: " + str(len(t))
            return "Provide text."

        if cl.startswith("reverse "):
            return "Reversed: " + cmd[8:][::-1]

        # History
        if cl in ["history", "command history"]:
            return "Recent:\n" + "\n".join("  > " + c for c in self.history[-10:])

        # Conversation AI fallback
        ai = self.conversation.respond(cmd)
        if ai:
            return ai

        # Knowledge base keyword fallback
        for k in KnowledgeBase.FACTS:
            if k in cl:
                return KnowledgeBase.FACTS[k]

        return PersonalityEngine.get_confused(USER_NAME)

class Jarvis:
    def __init__(self):
        self.processor = CommandProcessor()
        self.running = False
        self.boot_time = datetime.datetime.now()
        self.voice = VoiceEngine()
        self.voice_output = self.voice.tts_enabled
        self.voice_input = False

    def output(self, text):
        """Print and optionally speak a response."""
        for line in text.split("\n"):
            print("  [" + SHORT_NAME + "]: " + line)
        if self.voice_output:
            self.voice.speak(text)

    def get_input(self):
        """Get input from keyboard or microphone."""
        if self.voice_input and self.voice.stt_enabled:
            heard = self.voice.listen()
            if heard:
                print("  [" + USER_NAME + "]: " + heard)
                return heard
            print("  [MIC]: Nothing detected. Type your command:")
        return input("  [" + USER_NAME + "]: ").strip()

    def boot(self):
        print()
        print("  " + "=" * 55)
        print("  |                                                   |")
        print("  |   J.A.R.V.I.S. v" + VERSION + " - Codename: " + CODENAME + "        |")
        print("  |   Just A Rather Very Intelligent System           |")
        print("  |                                                   |")
        print("  " + "=" * 55)
        print()

        steps = [
            "Initializing core systems",
            "Loading personality matrix",
            "Calibrating knowledge base",
            "Starting math engine",
            "Activating task manager",
            "Loading security protocols",
            "Establishing conversation AI",
            "Voice TTS: " + ("ONLINE" if self.voice.tts_enabled else "OFFLINE"),
            "Voice STT: " + ("ONLINE" if self.voice.stt_enabled else "OFFLINE"),
            "All systems nominal",
        ]
        for step in steps:
            print("  [BOOT] " + step + "." * random.randint(1, 3) + " OK")
            time.sleep(0.12)

        print()
        print("  " + "-" * 55)
        greeting = PersonalityEngine.get_greeting(USER_NAME)
        print("  [" + SHORT_NAME + "]: " + greeting)
        print("  [" + SHORT_NAME + "]: Type 'help' to see my capabilities.")
        if self.voice.tts_enabled:
            print("  [" + SHORT_NAME + "]: Voice output is ON. Say 'voice off' to disable.")
        if self.voice.stt_enabled:
            print("  [" + SHORT_NAME + "]: Say 'voice mode' to switch to microphone input.")
        print("  " + "-" * 55)
        print()

        if self.voice_output:
            self.voice.speak(greeting)

    def handle_voice_commands(self, cl):
        """Handle voice-related commands. Returns a response string or None."""
        if cl in ["voice on", "enable voice", "speak on", "tts on"]:
            if not self.voice.tts_enabled:
                return "Voice engine not available. Install pyttsx3: pip install pyttsx3"
            self.voice_output = True
            return "Voice output enabled. You'll hear me now."

        if cl in ["voice off", "disable voice", "speak off", "tts off", "mute", "be quiet", "shut up"]:
            self.voice_output = False
            return "Voice output disabled. Text only mode."

        if cl in ["voice mode", "mic on", "listen mode", "microphone on", "stt on"]:
            if not self.voice.stt_enabled:
                return "Speech recognition not available. Install: pip install SpeechRecognition pyaudio"
            self.voice_input = True
            return "Microphone input enabled. Speak your commands, " + USER_NAME + ". Say 'text mode' to switch back."

        if cl in ["text mode", "mic off", "type mode", "microphone off", "stt off"]:
            self.voice_input = False
            return "Microphone off. Keyboard input mode."

        if cl == "voice status":
            tts_s = "ON" if self.voice_output else "OFF"
            stt_s = "ON" if self.voice_input else "OFF"
            tts_a = "available" if self.voice.tts_enabled else "not installed"
            stt_a = "available" if self.voice.stt_enabled else "not installed"
            return "TTS: " + tts_s + " (" + tts_a + ") | STT: " + stt_s + " (" + stt_a + ")"

        return None

    def run(self):
        self.running = True
        self.boot()

        while self.running:
            try:
                ui = self.get_input()
                if not ui:
                    continue

                cl = ui.lower().strip()

                # Check voice commands first
                vr = self.handle_voice_commands(cl)
                if vr:
                    self.output(vr)
                    print()
                    continue

                r = self.processor.process(ui)
                if r == "EXIT":
                    farewell = PersonalityEngine.get_farewell(USER_NAME)
                    print("\n  [" + SHORT_NAME + "]: " + farewell)
                    if self.voice_output:
                        self.voice.speak(farewell)
                    up = datetime.datetime.now() - self.boot_time
                    m, s = int(up.total_seconds() // 60), int(up.total_seconds() % 60)
                    print("  [Session: " + str(m) + "m " + str(s) + "s | Commands: " + str(len(self.processor.history)) + "]")
                    print("  " + "=" * 55)
                    self.running = False
                elif r:
                    self.output(r)
                    print()

            except (KeyboardInterrupt, EOFError):
                print("\n  [" + SHORT_NAME + "]: Emergency shutdown. Goodbye, " + USER_NAME + ".")
                if self.voice_output:
                    self.voice.speak("Emergency shutdown. Goodbye, " + USER_NAME + ".")
                self.running = False


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()
