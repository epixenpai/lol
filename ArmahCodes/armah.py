import logging
import time
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from gradio_client import Client
from reportlab.lib.units import inch
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_section(prompt, retries=5, model_endpoint=""):
    """
    Function to generate content from an AI model based on a prompt.
    Retries several times in case of failure.
    """
    client = Client(model_endpoint)
    attempt = 0
    while attempt < retries:
        try:
            logging.info(f"Attempting to generate content from {model_endpoint}. Attempt {attempt + 1}/{retries}")
            result = client.predict(message=prompt, system_prompt=prompt, max_new_tokens=4000, temperature=0.6, api_name="/chat")
            return result
        except Exception as e:
            logging.error(f"Error occurred: {e}. Retrying...")
            attempt += 1
            time.sleep(5)  # Brief pause before retry
    raise Exception(f"Failed to generate content from {model_endpoint} after {retries} attempts")

def generate_chapters(prompts, model_endpoint):
    """
    Function to generate multiple chapters of the book by iterating through prompts.
    """
    chapters = []
    total_word_count = 0
    total_pages = 0

    for i, prompt in enumerate(prompts):
        logging.info(f"Generating content for Chapter {i + 1}")
        chapter_content = generate_section(prompt, model_endpoint=model_endpoint)
        
        # Track word count and estimate pages
        chapter_word_count = len(chapter_content.split())
        total_word_count += chapter_word_count
        estimated_pages = chapter_word_count // 400  # Assuming 400 words per page
        total_pages += estimated_pages

        logging.info(f"Chapter {i + 1} generated: {chapter_word_count} words, ~{estimated_pages} pages.")
        chapters.append(chapter_content)

        # Log progress after each chapter
        logging.info(f"Total word count so far: {total_word_count} words (~{total_pages} pages).")
    
    return chapters, total_word_count, total_pages

def generate_pdf(chapters, cover_text, cover_image_path):
    """
    Function to generate a high-quality PDF book with a cover, table of contents, and multiple chapters.
    """
    # Create the document
    doc = SimpleDocTemplate("professional_ebook.pdf", pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Cover Page Style
    cover_style = ParagraphStyle(
        name='Cover',
        fontSize=30,
        leading=36,
        alignment=1,
        spaceAfter=40,
    )

    # Chapter Title Style
    chapter_title_style = ParagraphStyle(
        name='ChapterTitle',
        fontSize=20,
        leading=24,
        spaceAfter=14,
        textColor=colors.HexColor("#0033A0")
    )

    # Body Text Style
    body_text_style = ParagraphStyle(
        name='BodyText',
        fontSize=12,
        leading=18,
        spaceAfter=12,
    )

    # Add Cover Page
    if cover_image_path:
        story.append(Image(cover_image_path, width=6*inch, height=9*inch))
        story.append(PageBreak())
    else:
        story.append(Paragraph(cover_text, cover_style))
        story.append(PageBreak())

    # Add Chapters
    for i, chapter in enumerate(chapters):
        chapter=chapter.replace("assistant", "").strip()
        chapter_title = f"Chapter {i + 1}: {chapter.splitlines()[0]}"
        story.append(Paragraph(chapter_title, chapter_title_style))
        story.append(Spacer(1, 12))

        lines = chapter.split('\n')[1:]  # Skip title line
        for line in lines:
            story.append(Paragraph(line, body_text_style))
            story.append(Spacer(1, 12))

        story.append(PageBreak())

    # Build the PDF
    doc.build(story)
    logging.info("PDF created successfully")

if __name__ == "__main__":
    # Book Title and Cover Text
    cover_text = "Unlocking Your Potential: The Science of Self-Growth"
    cover_image_path = "cover_image.jpg"  # Optional cover image

    # Model Endpoint for Content Generation
    model_endpoint = "https://chuanli11-chat-llama-3-2-3b-instruct-uncensored.hf.space"  # Gradio endpoint for AI model

    # Expanded Chapter Prompts
   
        
    chapter_prompts = [
        # Chapter 1: Understanding Motivation
        """Provide an in-depth introduction to the concept of motivation. Discuss its definition and significance in modern society. 
        Explore the different types of motivation, such as intrinsic and extrinsic motivation, and how they impact our actions and decisions. 
        Delve into the psychological and biological foundations of motivation, including key theories like Maslow's Hierarchy of Needs. 
        Include real-life examples of individuals who have harnessed motivation to achieve significant accomplishments and exercises to assess readers' current motivational state.""",

        # Chapter 2: The Psychology of Willpower
        """Explain the concept of willpower and its critical role in achieving goals. Discuss scientific studies on willpower, self-control, and how they are linked to success. 
        Explore the connection between willpower and habit formation, and the strategies to strengthen willpower over time. 
        Highlight techniques such as delayed gratification and mental toughness that can help enhance willpower. 
        Include practical exercises to help readers build and maintain strong willpower for long-term success.""",

        # Chapter 3: Setting Powerful Goals
        """Discuss the importance of setting clear and achievable goals in personal and professional life. Explain the SMART goals framework (Specific, Measurable, Achievable, Relevant, Time-bound) and its effectiveness in goal-setting. 
        Illustrate the role of visualization and mental imagery in achieving goals and how these techniques can be incorporated into daily routines. 
        Provide real-life examples of successful goal-setting and achievement. 
        Include practical exercises for readers to create their own powerful and actionable goals.""",

        # Chapter 4: Overcoming Procrastination
        """Identify the root causes and psychological factors behind procrastination. Discuss various strategies and techniques to overcome procrastination, including the Pomodoro Technique, time-blocking, and breaking tasks into smaller, manageable steps. 
        Provide case studies of individuals who overcame chronic procrastination to achieve their goals. 
        Explore the role of mindset and self-discipline in combating procrastination. 
        Include practical exercises to help readers eliminate procrastination from their daily lives and build a more productive routine.""",

        # Chapter 5: Building and Sustaining Habits
        """Explain the science behind habit formation and change, including the Habit Loop (cue, routine, reward). Discuss strategies to build positive habits and break negative ones. 
        Explore the role of environment, social support, and accountability in developing and sustaining new habits. 
        Provide real-life examples of individuals who successfully transformed their habits to achieve personal and professional growth. 
        Include exercises for readers to create and maintain healthy and productive habits.""",

        # Chapter 6: Developing a Growth Mindset
        """Define the concepts of fixed and growth mindsets and their impact on personal development. Explain how a growth mindset can transform one's approach to challenges, learning, and self-improvement. 
        Discuss the role of self-belief and perseverance in developing a growth mindset. 
        Provide techniques to cultivate a growth mindset, including embracing failure as a learning opportunity and seeking continuous improvement. 
        Include exercises to help readers shift from a fixed mindset to a growth mindset and foster a love for learning and growth.""",

        # Chapter 7: Managing Stress and Avoiding Burnout
        """Discuss the impact of stress on motivation, productivity, and overall well-being. Explore various techniques for managing stress, including mindfulness, meditation, physical activity, and effective time management. 
        Identify the signs of burnout and provide strategies to prevent and recover from it. 
        Share real-life stories of individuals who successfully managed stress and avoided burnout to achieve long-term success. 
        Include practical exercises and tips for readers to manage stress and maintain a healthy work-life balance.""",

        # Chapter 8: The Power of Positive Self-Talk
        """Explain the influence of self-talk on motivation, confidence, and mental health. Discuss techniques for transforming negative self-talk into positive affirmations and constructive inner dialogue. 
        Explore the role of self-compassion and kindness in personal growth and overcoming setbacks. 
        Provide real-life examples of individuals who benefited from positive self-talk and its impact on their achievements. 
        Include exercises for readers to practice positive self-talk and develop a more optimistic and resilient mindset.""",

        # Chapter 9: Building a Support System
        """Highlight the importance of a strong support system in achieving personal and professional goals. Discuss strategies for building and maintaining supportive relationships with family, friends, mentors, and peers. 
        Explore the role of mentorship, networking, and community in personal development and growth. 
        Provide real-life examples of individuals who achieved success with the help of a robust support system. 
        Include exercises for readers to create and strengthen their own support networks to foster motivation and accountability.""",

        # Chapter 10: Creating a Personalized Motivation Plan
        """Synthesize the concepts from previous chapters into a comprehensive and personalized motivation plan. Discuss strategies for staying motivated, adapting to challenges, and maintaining momentum over time. 
        Emphasize the importance of regular self-reflection, goal reassessment, and flexibility in the motivation journey. 
        Provide real-life examples of successful motivation plans and how they were tailored to individual needs and circumstances. 
        Include practical exercises and templates for readers to create, implement, and refine their personalized motivation plans for long-term success.""",

        # Chapter 11: Mastering Time Management
            """Discuss the importance of effective time management in achieving personal and professional goals. Explain various time management techniques such as the Eisenhower Matrix, time-blocking, and prioritization. 
            Explore the role of planning, scheduling, and setting boundaries in managing time efficiently. Provide real-life examples of individuals who excelled in time management and its impact on their success. 
            Include practical exercises and tools for readers to improve their time management skills and maximize productivity.""",

        # Chapter 12: Cultivating Resilience and Grit
        """Define resilience and grit, and explain their significance in overcoming challenges and achieving long-term success. Discuss the psychological and behavioral traits associated with resilience and grit. 
        Explore strategies to develop and strengthen these qualities, such as embracing failure, maintaining a positive attitude, and practicing self-compassion. 
        Provide real-life examples of individuals who demonstrated exceptional resilience and grit in the face of adversity. 
        Include practical exercises for readers to build their resilience and grit, and maintain perseverance in their personal and professional endeavors.""",

        # Special Thanks
        """In this section, express gratitude to individuals and entities who contributed to the creation of the book. Acknowledge the support of family, friends, mentors, and colleagues who provided inspiration, guidance, and encouragement. 
        Highlight the contributions of experts, researchers, and authors whose work influenced the content of the book. 
        Thank the readers for their interest and commitment to self-improvement. 
        Include a heartfelt note of appreciation for everyone involved in the journey of writing and publishing the book."""
    

    ]
  
        
        
        # Additional prompts for more chapters can be added here to meet the target length.
    

    # Generate content for each chapter
    chapters, total_word_count, total_pages = generate_chapters(chapter_prompts, model_endpoint)

    # Log final progress
    logging.info(f"Final Word Count: {total_word_count} words (~{total_pages} pages).")
    cover_image_path="/home/armaan/ArmahCodes/cover_page.png"
    # Generate the professional eBook PDF
    generate_pdf(chapters, cover_text, cover_image_path)

