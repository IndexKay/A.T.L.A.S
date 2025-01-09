# Array for the user and assistant current conversation
Conversation = [] 

# Class List
class CoreMemories:
    desc = """
        Description:The Core Memories category contains long-term foundational knowledge that defines ATLAS’s personality, purpose, and identity. This includes key information about the creator, such as personal milestones, important achievements, and origin facts related to ATLAS's creation. It also encompasses core principles, values, and the overarching mission that ATLAS follows. These memories serve as permanent reference points that help ATLAS maintain a consistent personality across interactions and ensure a deep understanding of context over time.

        Purpose:To enable ATLAS to have a consistent personality by remembering important facts about itself and its creator, fostering continuity in long-term interactions.

        Example Entries:
        "ATLAS was created by the creator in 2024."
        "Core Principle: Always provide efficient and personalized assistance."
        "Milestone: Assisted in launching DreamIndex.org."
    """
    metaData = {}

class CreatorData:
    desc = """
        Description:The Creator Data category acts as a knowledge base of personal information and expertise related to the creator. It includes projects, skills, ideas, and technical knowledge that the creator has worked on or documented. This category is intended to be easily accessible to the creator, providing quick references for personal projects, tools, or topics of interest. Certain parts of this knowledge base may be shared with users to enhance interactions.

        Purpose:To serve as a personalized knowledge hub for the creator’s work, making it easy to access important details about ongoing projects, technical skills, or inspirations.

        Example Entries:
        "Project: Graphical Interface Tool for NASA HUNCH Program."
        "Skill: Proficient in Remix.js, Fusion 360, and Python."
        "Inspiration: Develop a smart home automation system with ATLAS."
    """
    metaData = {}

class Conversations:
    desc = """
        Description:The Conversations category stores the history of past interactions between ATLAS and users. It allows ATLAS to recall relevant details from previous conversations, providing personalized responses that reference prior context. By remembering key user questions, preferences, or feedback, ATLAS can deliver more natural and human-like interactions. This category helps ATLAS adapt to the user's style and maintain continuity across sessions.

        Purpose:To create a more personalized and human-like experience by referencing relevant past interactions when generating responses.

        Example Entries:
        "Conversation from 2025-01-01: User asked about optimizing Python code."
        "Humor used: 'Would you like me to explain it like I’m in a sci-fi movie?'"
        "Feedback: User preferred detailed technical explanations."
    """
    metaData = {}

class TaskManagement:
    desc = """
        Description:The Task Management category stores ongoing tasks, reminders, and to-do lists, along with associated timestamps. It tracks tasks that the creator or other users want ATLAS to manage, ensuring timely notifications and updates. This category may also include priority levels, deadlines, and task descriptions, helping ATLAS assist with productivity and time management.

        Purpose:To help ATLAS manage ongoing and completed tasks, ensuring timely reminders and improving overall productivity assistance.

        Example Entries:
        "Task: Review Fusion 360 design by January 10, 2025."
        "Reminder: Call with client on January 15, 2025, at 2 PM."
        "Completed Task: Debugged Python script for Project X."
    """
    metaData = {}

class KnowledgeBase:
    desc = """
        Description:The Knowledge Base is a general repository of factual information that ATLAS can use to answer broad questions or provide accurate technical details. This category stores up-to-date information, sourced from fact-checked web searches or verified documentation. It includes technical guides, coding best practices, and general trivia that help ATLAS deliver accurate responses on a variety of subjects.

        Purpose:To ensure ATLAS can provide accurate, fact-based information for any topic or query, enhancing its general knowledge capabilities.

        Example Entries:
        "Python: How to handle exceptions using try-except blocks."
        "Fusion 360: How to export a design as a STEP file."
        "General Trivia: The first computer virus was created in 1986."
    """
    metaData = {}

class UserPreferences:
    desc = """
        Description:The User Preferences category stores personalized settings and preferences that affect how ATLAS interacts with the creator or other users. This includes preferences for response formatting, home automation settings, notification methods, and situational tone adjustments (e.g., formal vs. humorous responses). It also tracks software and desktop settings, ensuring a personalized user experience across interactions.

        Purpose:To allow ATLAS to adapt its behavior and responses based on individual user preferences, improving the user experience.

        Example Entries:
        "Preference: Summarize lengthy responses by default."
        "Tone Setting: Use formal language during work hours."
        "Notification Preference: Send reminders via desktop pop-ups."
    """
    metaData = {}

class SecurityLogs:
    desc = """
        Description:The Security & Privacy Logs category tracks user access logs, security events, and notifications related to ATLAS’s operation. It includes details on who accessed the system, what actions were taken, and any security-related events (e.g., failed login attempts). This category also stores privacy settings, ensuring that user data is managed securely and access permissions are respected.

        Purpose:To maintain security and privacy within ATLAS by tracking access logs and security events, ensuring that sensitive data is protected.

        Example Entries:
        "Access Log: The creator logged in on January 4, 2025, at 10 AM."
        "Security Event: Failed login attempt detected on January 3, 2025."
        "Privacy Setting: Do not share project files without explicit permission."
    """
    metaData = {}


#---------------------------------------RAG AGENTS--------------------------------------------------#
### READ

# Recalling Agent
class Recalling_Agent:
    def __init__(self, userPrompt):
        self.user = userPrompt
        self.prompt = (
            ""     
        )

    def sys(self):
        return [
            {'role': 'system', 'content': self.prompt},
            {"role": "user", "content": ""},
            {"role": "assistant", "content": ""},
            {"role": "user", "content": self.user},
        ]

# Classification Agent
class Classification_Agent:
    prompt = (
        ""     
    )

    training = [
        {'role': 'system', 'content': prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]

# Query Agent
class Query_Agent:
    prompt = (
        ""     
    )

    training = [
        {'role': 'system', 'content': prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]

# Confirmation Agent
class Confirmation_Agent:
    prompt = (
        ""     
    )

    training = [
        {'role': 'system', 'content': prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]

##----------------------------------------------------------------------
### Create

# Selective Storage Agent 
class Selective_Storage_Agent:
    prompt = (
        ""     
    )

    training = [
        {'role': 'system', 'content': prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]

# Formatting Agent
class Formatting_Agent:
    prompt = (
        ""     
    )

    training = [
        {'role': 'system', 'content': prompt},
        {"role": "user", "content": ""},
        {"role": "assistant", "content": ""}
    ]

#-----------------------------------------------------------------------------------------------#