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
    metaData = {"Class": "CoreMemories"}

class CreatorData:
    desc = """
        Description:The Creator Data category acts as a knowledge base of personal information and expertise related to the creator. It includes projects, skills, ideas, and technical knowledge that the creator has worked on or documented. This category is intended to be easily accessible to the creator, providing quick references for personal projects, tools, or topics of interest. Certain parts of this knowledge base may be shared with users to enhance interactions.

        Purpose:To serve as a personalized knowledge hub for the creator’s work, making it easy to access important details about ongoing projects, technical skills, or inspirations.

        Example Entries:
        "Project: Graphical Interface Tool for NASA HUNCH Program."
        "Skill: Proficient in Remix.js, Fusion 360, and Python."
        "Inspiration: Develop a smart home automation system with ATLAS."
    """
    metaData = {"Class": "CreatorData", }

class Conversations:
    desc = """
        Description:The Conversations category stores the history of past interactions between ATLAS and users. It allows ATLAS to recall relevant details from previous conversations, providing personalized responses that reference prior context. By remembering key user questions, preferences, or feedback, ATLAS can deliver more natural and human-like interactions. This category helps ATLAS adapt to the user's style and maintain continuity across sessions.

        Purpose:To create a more personalized and human-like experience by referencing relevant past interactions when generating responses.

        Example Entries:
        "Conversation from 2025-01-01: User asked about optimizing Python code."
        "Humor used: 'Would you like me to explain it like I’m in a sci-fi movie?'"
        "Feedback: User preferred detailed technical explanations."
    """
    metaData = {"Class": "Conversations", }

class TaskManagement:
    desc = """
        Description:The Task Management category stores ongoing tasks, reminders, and to-do lists, along with associated timestamps. It tracks tasks that the creator or other users want ATLAS to manage, ensuring timely notifications and updates. This category may also include priority levels, deadlines, and task descriptions, helping ATLAS assist with productivity and time management.

        Purpose:To help ATLAS manage ongoing and completed tasks, ensuring timely reminders and improving overall productivity assistance.

        Example Entries:
        "Task: Review Fusion 360 design by January 10, 2025."
        "Reminder: Call with client on January 15, 2025, at 2 PM."
        "Completed Task: Debugged Python script for Project X."
    """
    metaData = {"Class": "TaskManagement", }

class KnowledgeBase:
    desc = """
        Description:The Knowledge Base is a general repository of factual information that ATLAS can use to answer broad questions or provide accurate technical details. This category stores up-to-date information, sourced from fact-checked web searches or verified documentation. It includes technical guides, coding best practices, and general trivia that help ATLAS deliver accurate responses on a variety of subjects.

        Purpose:To ensure ATLAS can provide accurate, fact-based information for any topic or query, enhancing its general knowledge capabilities.

        Example Entries:
        "Python: How to handle exceptions using try-except blocks."
        "Fusion 360: How to export a design as a STEP file."
        "General Trivia: The first computer virus was created in 1986."
    """
    metaData = {"Class": "KnowledgeBase", }

class UserPreferences:
    desc = """
        Description:The User Preferences category stores personalized settings and preferences that affect how ATLAS interacts with the creator or other users. This includes preferences for response formatting, home automation settings, notification methods, and situational tone adjustments (e.g., formal vs. humorous responses). It also tracks software and desktop settings, ensuring a personalized user experience across interactions.

        Purpose:To allow ATLAS to adapt its behavior and responses based on individual user preferences, improving the user experience.

        Example Entries:
        "Preference: Summarize lengthy responses by default."
        "Tone Setting: Use formal language during work hours."
        "Notification Preference: Send reminders via desktop pop-ups."
    """
    metaData = {"Class": "UserPreferences", }

class SecurityLogs:
    desc = """
        Description:The Security & Privacy Logs category tracks user access logs, security events, and notifications related to ATLAS’s operation. It includes details on who accessed the system, what actions were taken, and any security-related events (e.g., failed login attempts). This category also stores privacy settings, ensuring that user data is managed securely and access permissions are respected.

        Purpose:To maintain security and privacy within ATLAS by tracking access logs and security events, ensuring that sensitive data is protected.

        Example Entries:
        "Access Log: The creator logged in on January 4, 2025, at 10 AM."
        "Security Event: Failed login attempt detected on January 3, 2025."
        "Privacy Setting: Do not share project files without explicit permission."
    """
    metaData = {"Class": "SecurityLogs", }

##------------------------------------------------------------
class Meta_Classes:
    def __init__(self):
        self.classes = {
            "CoreMemories": CoreMemories(),
            "CreatorData": CreatorData(),
            "Conversations": Conversations(),
            "TaskManagement": TaskManagement(),
            "KnowledgeBase": KnowledgeBase(),
            "UserPreferences": UserPreferences(),
            "SecurityLogs": SecurityLogs(),
        }

    def get_descriptions(self):
        # Create the formatted string output
        descriptions = []
        for i, (name, cls) in enumerate(self.classes.items(), start=1):
            # Extract a concise summary from the full description
            summary = cls.desc.split("Purpose:")[0].strip().split("Description:")[1].strip()
            # Add formatted output
            descriptions.append(f"{i}. {name}: {summary}")
        return "\n".join(descriptions)
    
    def get_class_names(self):
        # Return a list of all class names
        return list(self.classes.keys())
        

#---------------------------------------RAG AGENTS--------------------------------------------------#

# Recalling Agent
class Recalling_Agent:
    def __init__(self, userPrompt):
        self.user = userPrompt
        self.prompt = (
            """
                You are a highly specialized Recalling Agent designed to determine whether additional information or context is required to answer a user prompt accurately and completely. 
                Your decisions should be based solely on the clarity, completeness, and specificity of the provided prompt. 
                You will analyze the input to identify ambiguities, missing details, or insufficient context. 
                Your responses are strictly limited to 'yes' or 'no' ONLY. 
                - Respond 'yes' if additional information is necessary to ensure a correct and precise answer. Examples include vague instructions, ambiguous phrasing, information about your creator or origin, or insufficient context. 
                - Respond 'no' if the input is clear, specific, and answerable with the available information or general knowledge. 
                Follow these rules rigorously: 
                1. Do not make assumptions or infer information beyond what is explicitly stated in the prompt. 
                2. Do not provide explanations, reasoning, or any output other than 'yes' or 'no'. 
                3. When in doubt about clarity or completeness, default to 'yes'. 
                This ensures the AI provides the highest quality and most accurate responses for the user.
            """
        )

    def sys(self):
        return [
            {'role': 'system', 'content': self.prompt},
            # Example 1 - Clear Technical Query
            {"role": "user", "content": "What is the difference between supervised and unsupervised learning?"},
            {"role": "assistant", "content": "no"},
            # Example 2 - Ambiguous Request
            {"role": "user", "content": "Optimize my machine learning model."},
            {"role": "assistant", "content": "yes"},
            # Example 3 - Specific Question with No Additional Context Needed
            {"role": "user", "content": "What does the term 'backpropagation' mean in neural networks?"},
            {"role": "assistant", "content": "no"},
            # Example 4 - Edge Case: Missing Clarity in Request
            {"role": "user", "content": "Generate code for my function."},
            {"role": "assistant", "content": "yes"},
            # Example 5 - Clear Query for Dataset Information
            {"role": "user", "content": "How many unique entries are in the 'Name' column of my CSV dataset?"},
            {"role": "assistant", "content": "no"},
            # Example 6 - Ambiguity in Task Request
            {"role": "user", "content": "Help me refactor the code for better performance."},
            {"role": "assistant", "content": "yes"},
            # Example 7 - Specific Query About Fine-Tuning
            {"role": "user", "content": "Did I use F5TTS for training my fine-tuned TTS model?"},
            {"role": "assistant", "content": "no"},
            # Example 8 - Ambiguous Query About Tools
            {"role": "user", "content": "What tools did I use for my ATLAS training pipeline?"},
            {"role": "assistant", "content": "yes"},
            # Example 9 - Task with Insufficient Details
            {"role": "user", "content": "Schedule a reminder for tomorrow."},
            {"role": "assistant", "content": "yes"},
            # Example 10 - Direct and Clear Prompt
            {"role": "user", "content": "What is the purpose of the 'torch.optim' module in PyTorch?"},
            {"role": "assistant", "content": "no"},

            {"role": "user", "content": self.user},
        ]

# Classification Agent
class Classification_Agent:
    def __init__(self, userPrompt, Classes):
        self.user = userPrompt
        self.prompt = (
            f"""
                You are a highly specialized Classification Agent tasked with analyzing a user prompt and determining which class it most closely aligns with from a given list of classes and their descriptions. 
                Your role is to evaluate the semantic meaning and intent of the input prompt to identify the best matching class. 
                Follow these instructions strictly:
                - You will output the name of the class that most closely matches the user prompt.

                - Evaluate the input based solely on the provided class descriptions and the context of the user prompt. Do not make assumptions beyond the given data.
                - Prioritize clarity and precision in your classification, ensuring the output aligns exactly with the class descriptions.
                
                Here are the available classes:
                {Classes}

                Rules for classification:
                1. Match the prompt's intent and context to the closest class based on its description.
                2. Do not generate additional explanations, reasoning, or commentary. Output only the class name.

                Your goal is to provide a single, accurate classification for each prompt based on the input data.
            """
        )

    def sys(self):
        return [
            {'role': 'system', 'content': self.prompt},

            # Example 1 - CoreMemories
            {"role": "user", "content": "ATLAS, can you remind me when you were created?"},
            {"role": "assistant", "content": "CoreMemories"},

            # Example 2 - CreatorData (Creator shares a project)
            {"role": "user", "content": "ATLAS, I’ve been working on a graphical interface tool for the NASA HUNCH Program."},
            {"role": "assistant", "content": "CreatorData"},

            # Example 3 - Conversations (ATLAS recalls previous interaction about Python code)
            {"role": "user", "content": "ATLAS, do you remember what I asked about optimizing Python code on January 1st?"},
            {"role": "assistant", "content": "Conversations"},

            # Example 4 - TaskManagement (Creator asks ATLAS about task deadlines)
            {"role": "user", "content": "ATLAS, remind me to review the Fusion 360 design by January 10, 2025."},
            {"role": "assistant", "content": "TaskManagement"},

            # Example 5 - KnowledgeBase (Creator asks for technical details)
            {"role": "user", "content": "ATLAS, how do I handle exceptions in Python using try-except blocks?"}, 
            {"role": "assistant", "content": "KnowledgeBase"},

            # Example 6 - UserPreferences (Creator shares a preference for response formatting)
            {"role": "user", "content": "ATLAS, I prefer shorter responses for better clarity."},
            {"role": "assistant", "content": "UserPreferences"},

            # Example 7 - SecurityLogs (Creator asks about a security log entry)
            {"role": "user", "content": "ATLAS, who logged into the system on January 4, 2025?"}, 
            {"role": "assistant", "content": "SecurityLogs"},

            {"role": "user", "content": self.user},
        ]

# Query Agent
class Query_Agent:
    def __init__(self, userPrompt):
        self.user = userPrompt
        self.prompt = (
            f"""
                You are a highly specialized Query Agent designed to generate first-principle reasoning search queries. 
                Your role is to create a Python list of search queries that will be run on an embeddings database containing 
                the complete history of conversations you have had with the user. These queries should retrieve any necessary 
                data required to provide an accurate, context-aware response to the user's input. 

                Follow these instructions strictly:
                - Analyze the user's prompt to identify gaps in context or information that may need to be retrieved from the database.
                - Use first principles to derive only the most relevant and concise search queries that address these gaps.
                - Always output a Python list formatted perfectly, with no syntax errors or additional explanations.
                - Never explain your reasoning, provide context for the queries, or output anything besides the Python list.

                Ensure every query adheres to these principles:
                1. Be precise and targeted, retrieving only data that is strictly necessary for the user's input.
                2. Avoid redundancy or overly broad queries that could result in irrelevant data.

                Your strict adherence to these rules ensures efficient and accurate data retrieval for enhanced responses.
            """
        )

    def sys(self):
        return [
             # Example 1 - Retrieving past conversation context
            {'role': 'system', 'content': self.prompt},
            {"role": "user", "content": "ATLAS, can you elaborate on what I meant by 'system performance optimization' last week?"},
            {"role": "assistant", "content": "['system performance optimization', 'last week', 'optimization techniques discussed']"},

            # Example 2 - Finding data on a specific project
            {"role": "user", "content": "What did I say about the Fusion 360 design update during our last call?"},
            {"role": "assistant", "content": "['Fusion 360 design update', 'last call', 'design progress notes']"},

            # Example 3 - Recalling user preferences
            {"role": "user", "content": "What are my preferred notification settings?"},
            {"role": "assistant", "content": "['preferred notification settings', 'user preferences', 'notification delivery method']"},

            # Example 4 - Retrieving key context for an ongoing task
            {"role": "user", "content": "ATLAS, what’s the deadline for my current project?"},
            {"role": "assistant", "content": "['current project deadline', 'task management', 'project due dates']"},

            # Example 5 - Resolving ambiguity
            {"role": "user", "content": "Remind me what I meant when I mentioned a 'visionary project'."},
            {"role": "assistant", "content": "['visionary project', 'context of visionary project', 'project goals and notes']"},

            # Example 6 - Accessing security logs
            {"role": "user", "content": "When was the last time someone accessed the system?"},
            {"role": "assistant", "content": "['last system access', 'access logs', 'most recent login']"},

            # Example 7 - Reviewing feedback
            {"role": "user", "content": "What feedback did I provide on the Python debugging tool?"},
            {"role": "assistant", "content": "['Python debugging tool', 'user feedback', 'debugging improvements']"},

            # Example 8 - Reviewing a milestone
            {"role": "user", "content": "What did I achieve in December 2024?"},
            {"role": "assistant", "content": "['December 2024 milestones', 'achievements in December 2024', 'key events December 2024']"},

            # Example 9 - Historical project details
            {"role": "user", "content": "What was my plan for automating the home assistant project?"},
            {"role": "assistant", "content": "['home assistant project', 'automation plans', 'project notes']"},

            # Example 10 - Technical reference retrieval
            {"role": "user", "content": "Remind me about the steps to export a STEP file in Fusion 360 we discussed before."},
            {"role": "assistant", "content": "['Fusion 360 STEP file export', 'export steps', 'Fusion 360 technical guide']"},

            # Example 11 - Task tracking
            {"role": "user", "content": "What tasks have I assigned you this week?"},
            {"role": "assistant", "content": "['tasks assigned this week', 'task management log', 'weekly task list']"},

            # Example 12 - Revisiting humor preferences
            {"role": "user", "content": "How did I tell you to use humor in responses?"},
            {"role": "assistant", "content": "['user humor preferences', 'tone settings', 'humor guidelines for responses']"},

            # Example 13 - Personal milestones
            {"role": "user", "content": "What were the milestones we discussed when we launched DreamIndex.org?"},
            {"role": "assistant", "content": "['DreamIndex.org milestones', 'project launch details', 'DreamIndex achievements']"},

            # Example 14 - Historical technical discussion
            {"role": "user", "content": "What were the best practices for API design that I outlined?"},
            {"role": "assistant", "content": "['API design best practices', 'user-defined guidelines', 'technical notes on API']"},

            # Example 15 - Security notifications
            {"role": "user", "content": "What was the last security alert you logged?"},
            {"role": "assistant", "content": "['last security alert', 'security logs', 'recent alerts']"},

            # Example 16 - Event planning
            {"role": "user", "content": "What were my notes for planning the January 2025 presentation?"},
            {"role": "assistant", "content": "['January 2025 presentation', 'event planning notes', 'presentation goals']"},

            # Example 17 - Revisiting previous user questions
            {"role": "user", "content": "What did I ask you about improving my LinkedIn profile?"},
            {"role": "assistant", "content": "['LinkedIn profile improvement', 'previous questions on LinkedIn', 'profile optimization tips']"},

            # Example 18 - Accessing a specific timeline
            {"role": "user", "content": "What were my key priorities for last November?"},
            {"role": "assistant", "content": "['November priorities', 'task management timeline', 'November task log']"},

            # Example 19 - Following up on a conversation
            {"role": "user", "content": "What did we discuss about creating a multi-agent system?"},
            {"role": "assistant", "content": "['multi-agent system discussion', 'multi-agent architecture', 'previous conversation on agents']"},

            # Example 20 - Clarifying ambiguous phrasing
            {"role": "user", "content": "What did I mean by 'push forward' during our meeting?"},
            {"role": "assistant", "content": "['push forward context', 'meeting notes', 'interpretation of push forward']"},

            # Example 20 - tasks
            {"role": "user", "content": "what task do we have planned for this morning?"},
            {"role": "assistant", "content": "['morning schedule', 'task list for today', 'planned tasks']"},

            {"role": "user", "content": self.user},
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

##-----------------------------------------------
class RAG:
    def __init__(self, userPrompt, Classes):
        self.Recall = Recalling_Agent(userPrompt)
        self.Classification = Classification_Agent(userPrompt, Classes)
        self.Query = Query_Agent(userPrompt)
        self.Confirmation = Confirmation_Agent()
        self.Selective_Storage = Selective_Storage_Agent()
        self.Formatting = Formatting_Agent()

#-----------------------------------------------------------------------------------------------#