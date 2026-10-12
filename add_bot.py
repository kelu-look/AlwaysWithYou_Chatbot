# Import libraries
from datetime import datetime
import streamlit as st
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain import PromptTemplate
from bot import Bot

st.title("Always With You Chatbot")
with st.sidebar:
    st.title("Characters")
    openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
    
    left_co, cent_co,last_co = st.columns(3)
    with cent_co:
        st.image('portraits/6.png', width=100) 
    
    # Initial bot setting
    bot_name = st.text_input("Character's Nickname", key="bot_name")
    bot_relationship = st.text_input("Your Relationship with the Character", key="relationship")
    human_name = st.text_input("Character's Nickname for You", key="human_name")
    common_phrases = st.text_input("Common Phrases", key="common_phrases")
    speaking_style = st.text_input("Speaking Style", key="speaking_style")
    important_memories = st.text_area("Important Memories", key="important_memories")
    other_background = st.text_area("Other Background", key="other_background")
    
# Initial bot class and some basic states
bot = Bot(bot_name, bot_relationship, human_name, common_phrases, speaking_style, important_memories, other_background, datetime.now(), [])
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history" not in st.session_state:
    st.session_state.history = ConversationBufferMemory(human_prefix=bot.human_name, ai_prefix=bot.bot_name)

# Create a button to clear chat history
def clear_chat_history():
    st.session_state.messages = []
if st.button("Clear Chat History"):
    clear_chat_history()
    
# Create a PromptTemplate with input variables
template = f"""
[Character Settings]{bot.consolidated_info()}

Current conversation:
{{history}}
{bot.human_name}: {{input}}
{bot.bot_name}:"""

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template=template,
)

# Create LLM & Conversation Chain
if openai_api_key:
    # Create LLM model
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)

    # Create the ConversationChain object with the specified configuration
    conversation = ConversationChain(
        prompt=prompt,
        llm=llm,
        memory=st.session_state['history']
    )
    
    # Load previous chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        
    # Print user input and LLM reply
    if user_input := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = conversation.predict(input=user_input)
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Save messages in the characters
    bot.save_chat_history(st.session_state.messages)
    print(bot.chat_history)
else:
    st.warning('OpenAI API key required to test this app.')