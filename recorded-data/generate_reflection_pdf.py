"""Generate a clean, corrected version of the Robo Chat project reflection slides."""

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Colors
BG = HexColor("#0f172a")
TEXT = HexColor("#1e1e1e")
HEADING = HexColor("#c2410c")  # Dark orange
SUBHEADING = HexColor("#0e7490")  # Dark cyan
MUTED = HexColor("#475569")
ACCENT = HexColor("#fbbf24")  # Yellow

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "SlideTitle", parent=styles["Title"],
    fontSize=24, textColor=HEADING, spaceAfter=20, alignment=TA_CENTER
)
heading_style = ParagraphStyle(
    "SlideHeading", parent=styles["Heading2"],
    fontSize=18, textColor=SUBHEADING, spaceAfter=12, spaceBefore=16
)
body_style = ParagraphStyle(
    "SlideBody", parent=styles["Normal"],
    fontSize=12, textColor=TEXT, leading=18, spaceAfter=6
)
bullet_style = ParagraphStyle(
    "SlideBullet", parent=body_style,
    leftIndent=20, bulletIndent=10, spaceAfter=4
)
sub_bullet_style = ParagraphStyle(
    "SubBullet", parent=bullet_style,
    leftIndent=40, bulletIndent=30, fontSize=11, textColor=MUTED
)
slide_num_style = ParagraphStyle(
    "SlideNum", parent=styles["Normal"],
    fontSize=9, textColor=MUTED, alignment=TA_CENTER
)


def make_slide(story, slide_num, title, sections):
    """Add a slide to the story."""
    if slide_num > 1:
        story.append(PageBreak())

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.2 * inch))

    for section in sections:
        if isinstance(section, str):
            # Simple paragraph
            story.append(Paragraph(section, body_style))
        elif isinstance(section, tuple):
            kind, text = section
            if kind == "heading":
                story.append(Paragraph(text, heading_style))
            elif kind == "bullet":
                story.append(Paragraph(f"\u2022 {text}", bullet_style))
            elif kind == "sub":
                story.append(Paragraph(f"  \u2013 {text}", sub_bullet_style))
            elif kind == "spacer":
                story.append(Spacer(1, 0.15 * inch))

    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"Slide {slide_num}", slide_num_style))


def build_pdf():
    output_path = "/home/vivekkarmarkar/Python Files/livekit-project/recorded-data/reflection_slides_clean.pdf"
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        leftMargin=1 * inch, rightMargin=1 * inch,
        topMargin=0.5 * inch, bottomMargin=0.5 * inch,
    )

    story = []

    # --- Slide 1: Title ---
    make_slide(story, 1, "Robo Chat: Project Reflection", [
        ("heading", "A voice AI system built with Claude Code in ~1.5 days"),
        ("spacer", ""),
        ("bullet", "Cute orange animated robot avatar with LED blue eyes"),
        ("bullet", "Natural voice conversation powered by LiveKit + OpenAI Realtime API"),
        ("bullet", "Visual pane for LaTeX equations, code, notes, and ASCII diagrams"),
        ("bullet", "Blackboard mode with live typewriter rendering effect"),
        ("bullet", "Slideshow navigation with download (slides + transcripts)"),
        ("spacer", ""),
        "Built by Vivek Karmarkar using Claude Code, March 2026",
    ])

    # --- Slide 2: Origin Story ---
    make_slide(story, 2, "Origin Story", [
        ("heading", "The Seed Motivation"),
        ("bullet", "Had been working extensively with Claude and Claude Code on PhD project"),
        ("bullet", "Idea came BEFORE the PhD comprehensive exam: have Claude attend the exam virtually"),
        ("bullet", "Inspired by how humans join via Zoom or Google Meet when not physically present"),
        ("bullet", "Vision: Claude joins with a cute orange animated robot face, LED blue eyes, natural conversation style"),
        ("bullet", "Doesn't interrupt, could ask questions during Q&A"),
        ("bullet", "Even without Zoom/Google Meet, a standalone system like this would have been fine"),
        ("spacer", ""),
        ("heading", "The Irony"),
        ("bullet", "Tried 3-4 times before the comps to build it \u2014 failed every time"),
        ("bullet", "Got it working right AFTER the comps while doomscrolling Twitter"),
    ])

    # --- Slide 3: Challenges Before the Comps ---
    make_slide(story, 3, "Challenges Before the Comps", [
        ("heading", "Failed Attempts"),
        ("bullet", "Tried 3-4 times to build the system before the comprehensive exam"),
        ("bullet", "Each time, Claude Code's research suggested similar tech stacks"),
        ("bullet", "These tech stacks were biased toward certain approaches that didn't work in practice"),
        ("bullet", "The same pattern repeated every time:"),
        ("sub", "Define the vision"),
        ("sub", "Claude Code suggests a tech stack"),
        ("sub", "Attempt to implement \u2014 fails"),
        ("spacer", ""),
        ("bullet", "No breakthrough before the comprehensive exam"),
    ])

    # --- Slide 4: The Breakthrough ---
    make_slide(story, 4, "The Breakthrough: Finding LiveKit", [
        ("heading", "Doomscrolling to Discovery"),
        ("bullet", "After the comps, while casually browsing Twitter, a post from LiveKit caught attention"),
        ("bullet", "The post mentioned a voice agent and real-time audio"),
        ("bullet", "Curiosity led to watching a YouTube demo video"),
        ("bullet", "The demo showed a human avatar (Anam) that could talk naturally and fill out medical forms"),
        ("spacer", ""),
        ("heading", "The Realization"),
        ("bullet", "The core functionality already existed"),
        ("bullet", "Just needed to swap the human avatar for the cute orange robot"),
        ("bullet", "Strip out the medical form component"),
        ("bullet", "Keep the natural conversation and live interaction"),
        ("bullet", "Claude Code could clone the repository and run it"),
    ])

    # --- Slide 5: Design Philosophy ---
    make_slide(story, 5, "Core Philosophy: Using Claude Code to Solve the Problem", [
        ("heading", "A. Workflow Inside Claude Code"),
        ("bullet", "Uses specific skills invoked by slash commands"),
        ("bullet", "Examples: sycophancy detection, GitHub cloning, niche library research, add-on feature"),
        ("spacer", ""),
        ("heading", "B. Design Philosophy"),
        ("bullet", "Solve the problem efficiently rather than building from scratch"),
        ("bullet", "If a solution exists out there, use it out of the box with Claude Code and tweak only what's needed"),
        ("bullet", "Started by cloning the LiveKit repo and running it with API keys"),
        ("bullet", "Even correcting initial mistakes from Claude Code along the way"),
    ])

    # --- Slide 6: Building Chill Mode ---
    make_slide(story, 6, "Building Chill Mode", [
        ("heading", "Step 1: Run the LiveKit Demo Out of the Box"),
        ("bullet", "Cloned the Anam healthcare intake example repo"),
        ("bullet", "Set up API keys (LiveKit Cloud + Anam)"),
        ("bullet", "Got it running \u2014 human avatar with medical form"),
        ("spacer", ""),
        ("heading", "Step 2: Analyze and Remove Anam"),
        ("bullet", "Anam had a 3-minute free tier limit (discovered via niche library research skill)"),
        ("bullet", "Decision: remove the Anam layer entirely"),
        ("sub", "Eliminates the 3-minute conversation limit"),
        ("sub", "Claude Code confirmed building a custom avatar was feasible"),
        ("spacer", ""),
        ("heading", "Step 3: Custom Avatar + Simplification"),
        ("bullet", "Claude Code built the custom orange robot avatar (SVG with animated eyes/mouth)"),
        ("bullet", "Stripped out the medical form \u2014 pure voice chat"),
        ("bullet", "Switched from LiveKit Inference (STT+LLM+TTS pipeline) to OpenAI Realtime API"),
        ("bullet", "Result: Chill mode \u2014 the cute orange robot talks naturally with no time limit"),
    ])

    # --- Slide 7: Refining Chill Mode ---
    make_slide(story, 7, "Refining the Chill Mode: API Engineering", [
        ("heading", "Goal: Minimize Costs and Cut Bloat"),
        ("bullet", "Removed the Anam API layer (already done)"),
        ("bullet", "Focused on using LiveKit free tier for core WebRTC transport"),
        ("bullet", "Introduced OpenAI Realtime API with user's own API key"),
        ("sub", "OpenAI handles the heavy lifting (real-time audio, responses)"),
        ("sub", "Reduces reliance on paid tiers of LiveKit"),
        ("spacer", ""),
        ("heading", "How This Was Achieved"),
        ("bullet", "Used niche library research skill to investigate OpenAI and LiveKit features"),
        ("bullet", "Confirmed OpenAI's suitability for real-time audio and natural conversation"),
        ("spacer", ""),
        ("heading", "Result"),
        ("bullet", "Streamlined chill mode with minimal cost and dependencies"),
    ])

    # --- Slide 8: Professor Claude Motivation ---
    make_slide(story, 8, "Second Motivation: Professor Claude", [
        ("heading", "The Broader Vision"),
        ("bullet", "PhD comps was the seed motivation, but it grew into something bigger"),
        ("bullet", 'Core idea: create a "Professor Claude" experience'),
        ("sub", "Natural voice conversation PLUS a visual pane"),
        ("sub", "Write equations (LaTeX), display code, take notes, draw diagrams"),
        ("spacer", ""),
        ("heading", "Visual Mode Implementation"),
        ("bullet", "Used niche library research to find rendering approach"),
        ("bullet", "Easy part came first: code blocks, notes, and LaTeX equations in the visual pane"),
        ("bullet", "All rendered through one tool (show_content) and one pipeline"),
        ("bullet", "The model decides what format to use based on conversation context"),
    ])

    # --- Slide 9: Slideshow + Downloads ---
    make_slide(story, 9, "Slideshow and Download Features", [
        ("heading", "Slideshow"),
        ("bullet", "Each show_content call becomes a slide"),
        ("bullet", "Prev/next navigation for browsing slides during conversation"),
        ("bullet", "Implemented using the add-on feature skill to avoid breaking existing features"),
        ("spacer", ""),
        ("heading", "Downloads"),
        ("bullet", "Download slides as PDF (via browser print)"),
        ("bullet", "Download full conversation transcript as .txt"),
        ("bullet", "Used niche library research to investigate OpenAI and LiveKit transcript APIs"),
        ("spacer", ""),
        ("heading", "Trade-off"),
        ("bullet", "Downloaded slides contain raw content (LaTeX source, markdown, ASCII)"),
        ("bullet", "Not as visually polished as the live slideshow but captures all information"),
        ("bullet", "Raw content can be reconstructed and beautified later"),
    ])

    # --- Slide 10: Diagram Challenge ---
    make_slide(story, 10, "Tackling the Diagram Challenge", [
        ("heading", "The Search for Live Sketching"),
        ("bullet", "Used the swarm skill to deploy multiple research agents"),
        ("bullet", "Explored: Framer Motion (latency issues), image models (too slow), ELK.js (too complicated)"),
        ("spacer", ""),
        ("heading", "Key Realization"),
        ("bullet", "LLMs are fundamentally limited in spatial manipulation, layout, and diagrammatic reasoning"),
        ("bullet", "Over-engineering a solution would always be capped by LLM spatial intelligence limits"),
        ("spacer", ""),
        ("heading", "Pragmatic Solution: ASCII Diagrams"),
        ("bullet", "Opted for ASCII diagrams using Unicode box-drawing characters"),
        ("bullet", "Works well for system diagrams, architecture sketches, flowcharts, and trees"),
        ("bullet", "Not ideal for physics force diagrams (angles), but practical for ML and CS topics"),
        ("bullet", "Zero latency \u2014 goes through the same show_content pipeline"),
    ])

    # --- Slide 11: Blackboard Mode ---
    make_slide(story, 11, "Blackboard Mode: The Hardest Problem", [
        ("heading", "Initial Failure"),
        ("bullet", "Wanted a live blackboard effect \u2014 character-by-character rendering"),
        ("bullet", "Asked Claude Code to research and implement it \u2014 failed 4-5 times"),
        ("bullet", "Claude Code kept coupling live streaming with live rendering into one complex problem"),
        ("spacer", ""),
        ("heading", "The Insight: Decoupling the Problem"),
        ("bullet", "Claude Code was trying: live streaming + live rendering = live effect"),
        ("bullet", "I said: we only care about the live rendering EFFECT"),
        ("bullet", "The visual pane already has the content (rendered in one shot)"),
        ("bullet", "Solution: just add a live renderer ON TOP of the existing visual pane content"),
        ("sub", "Don't stream things live and then render"),
        ("sub", "Get all the content first, then render it character by character"),
        ("spacer", ""),
        ("heading", "Result"),
        ("bullet", "Blackboard mode works by revealing existing content progressively via Streamdown"),
        ("bullet", "Solved a rendering problem, not a streaming problem"),
        ("bullet", "Physics-informed first-principles thinking cracked this"),
    ])

    # --- Slide 12: Testing & Fun ---
    make_slide(story, 12, "Testing and Fun", [
        ("heading", "Chill Mode Testing"),
        ("bullet", "Cricket commentary in Punjabi, Bhojpuri, and Marathi"),
        ("bullet", "Three-way commentary battle: Bhojpuri commentator vs Tony Greig vs Punjabi commentator"),
        ("bullet", "Fun Marathi conversations, songs, and laughter"),
        ("bullet", "Multilingual switching works natively via OpenAI Realtime API"),
        ("spacer", ""),
        ("heading", "Professor Claude Testing"),
        ("bullet", "Physics: static friction problem \u2014 conceptual mistakes from OpenAI Realtime"),
        ("sub", "LLM pattern-matched formulas instead of reasoning through physics"),
        ("sub", "Substituted F(t) into the equation without understanding conditional logic"),
        ("bullet", "Lesson: not ready for deployment to others, but usable for personal learning"),
        ("bullet", "Works better for ML/CS topics where ASCII diagrams and code rendering shine"),
    ])

    # --- Slide 13: Technical Toolbox ---
    make_slide(story, 13, "Technical Toolbox Used", [
        ("heading", "Solution Scouting"),
        ("bullet", "Finding and recognizing useful niche solutions (e.g., the LiveKit post on Twitter)"),
        ("bullet", "Applying discovered solutions creatively to the problem at hand"),
        ("spacer", ""),
        ("heading", "Systems Thinking"),
        ("bullet", "Seeing the whole picture and breaking problems into smaller pieces"),
        ("bullet", "Decoupling live streaming from live rendering (the blackboard insight)"),
        ("bullet", "Understanding where AI strengths and limitations lie"),
        ("spacer", ""),
        ("heading", "Claude Code Mastery"),
        ("bullet", "Custom skills invoked via slash commands"),
        ("bullet", "Adaptive problem-solving \u2014 knowing when to guide, when to let Claude Code work"),
        ("bullet", "Skills used: sycophancy debugger, niche library research, swarm, add-on feature, "
         "code audit swarm, Git skills (init, commit, push, branch, readme), standalone experimental test"),
    ])

    # --- Slide 14: Reflection on Skills ---
    make_slide(story, 14, "Reflection: What Made This Possible", [
        ("heading", "Not Vibe Coding \u2014 A Claude Code Project"),
        ("bullet", "Didn't write code from scratch \u2014 orchestrated existing tools and solutions"),
        ("bullet", "Physics background provided systems thinking and first-principles decomposition"),
        ("bullet", "AI collaboration skills: prompting, guiding, detecting when things go off track"),
        ("bullet", "Software development awareness: APIs, GitHub, dependency management"),
        ("spacer", ""),
        ("heading", "Key Insight from Robo"),
        ("bullet", '"Your approach shows a physics-trained analytical mindset \u2014 breaking problems down, '
         'experimenting through trial and error, balancing theory and practice"'),
        ("bullet", "Robo correctly guessed physics as the undergraduate background from conversation alone"),
    ])

    # --- Slide 15: Tags ---
    make_slide(story, 15, "Project Tags", [
        ("heading", "Techniques"),
        ("bullet", "Claude Code, Voice Agents, OpenAI Realtime API, LiveKit"),
        ("spacer", ""),
        ("heading", "Domains"),
        ("bullet", "Creative Technology"),
        ("bullet", "EdTech (Professor Claude concept)"),
        ("bullet", "Dev Tooling"),
        ("bullet", "AI Infrastructure"),
    ])

    # --- Slide 16: Demos & Next Steps ---
    make_slide(story, 16, "Planned Demos and Next Steps", [
        ("heading", "Demo Ideas (Loom Recordings)"),
        ("bullet", "Julia code walkthrough with differential equations and LaTeX"),
        ("bullet", "Physics example with ASCII diagrams"),
        ("bullet", "Machine learning concept with ASCII system diagram"),
        ("bullet", "Technical explainer in Punjabi cricket commentary style"),
        ("spacer", ""),
        ("heading", "Future Vision: Idealized Claude Code Workflow"),
        ("bullet", "Part 1: Remote control workflow \u2014 walk outside all day, get projects done remotely"),
        ("bullet", "Part 2: Professor Claude mode \u2014 voice brainstorming, reflection, and learning"),
        ("bullet", "Connect this system to Claude Code via MCP server and Channels"),
        ("bullet", "Even if the bridge doesn't work fully \u2014 learning MCP servers and Channels is valuable"),
    ])

    doc.build(story)
    print(f"PDF saved to: {output_path}")


if __name__ == "__main__":
    build_pdf()
