import streamlit as st
from src.interpreter import Interpreter
from src.streamlit_utils import execute_with_pipeline, get_variable_state, format_ast_to_dot
from src.parser import Parser

st.set_page_config(
    page_title="SpeakMath Chatbot",
    page_icon="🧮",
    layout="wide"
)

# --- Custom CSS for Chatbot Style ---
st.markdown("""
<style>
    .element-container { margin-bottom: 0.5rem; }
    /* Hide default chat input if we use it, but we are using custom */
    
    /* Floating Chat Input Styling */
    div[data-testid="stBottom"] {
        bottom: 20px;
        padding-bottom: 0;
        background: transparent;
    }
    
    div[data-testid="stChatInput"] {
        background: rgba(30, 30, 40, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        max-width: 800px;
        margin: 0 auto;
        padding: 5px;
    }
    
    /* Remove default input styling reset */
    .stChatInputContainer {
        border-radius: 20px !important;
    }

    


    
    /* Token Badge Styling */
    .token-badge {
        display: inline-block;
        padding: 4px 8px;
        margin: 2px;
        border-radius: 12px;
        background-color: #3b4354;
        color: #e0e0e0;
        font-family: monospace;
        font-size: 0.85em;
        border: 1px solid #555;
    }
    .token-type {
        color: #ffcc80;
        font-weight: bold;
    }
    .token-val {
        color: #a5d6a7;
    }
    
    /* Adjust main content padding to not hide behind footer */
    .block-container {
        padding-bottom: 150px;
    }

    
    div[data-testid="stExpander"] details {
        background-color: #f0f2f6;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am SpeakMath. You can ask me to calculate things, working with lists, or even use natural language. Try 'sum [1, 2, 3]'!"}
    ]

if "interpreter" not in st.session_state:
    st.session_state.interpreter = Interpreter()

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

if "trigger_run" not in st.session_state:
    st.session_state.trigger_run = False

# --- Command Processing Logic (Callback) ---
def process_command():
    """Reads input, executes command, updates history, and clears input."""
    # Check what triggered: text input or button?
    # Both sync 'widget_input'.
    user_input = st.session_state.get("widget_input", "").strip()
    
    # Check if triggered by sidebar (via input_text)
    if st.session_state.get("input_text"):
        user_input = st.session_state.input_text
        st.session_state.input_text = "" # consume
        
    if not user_input:
        return

    # Add User Message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Execute Pipeline
    with st.spinner("Processing... 🤖"):
        pipeline, updated_interp = execute_with_pipeline(user_input, st.session_state.interpreter)
    st.session_state.interpreter = updated_interp
    
    # Format Output
    output_text = ""
    if pipeline.get('error'):
        output_text = f"❌ Error: {pipeline['error']}"
    else:
        res = pipeline['result']
        if res is not None:
             output_text = f"✅ Result: **{res}**"
        else:
             output_text = "✅ Done (No output)"

    # Add Assistant Message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": output_text,
        "pipeline": pipeline
    })
    
    # Clear Input Widget safely
    st.session_state.widget_input = ""

# --- Sidebar: Variables & Controls ---
with st.sidebar:
    st.title("🧮 SpeakMath")
    st.markdown("---")
    
    # Variable Inspector
    st.subheader("📊 Variables")
    vars = get_variable_state(st.session_state.interpreter)
    if vars:
        # Convert to simple list of dicts for dataframe
        var_data = [{"Name": k, "Value": str(v), "Type": type(v).__name__} for k, v in vars.items()]
        st.dataframe(var_data, hide_index=True, use_container_width=True)
    else:
        st.info("No variables set yet.")
        
    st.markdown("---")
    st.subheader("📚 Quick Examples")
    examples = [
        "sum [10, 20, 30]",
        "set nums to [1, 5, 2, 8]",
        "sort nums descending",
        "find the average of nums",
        "map add 5 over nums",
        "filter < 10 in [5, 12, 2, 20]"
    ]
    
    # Callback to handle example click
    def set_example(ex):
        st.session_state.input_text = ex
        st.session_state.trigger_run = True
        
    for ex in examples:
        # Use a unique key for each button to avoid generic state issues
        if st.button(ex, use_container_width=True, on_click=set_example, args=(ex,)):
            pass

            
    if st.button("🔄 Restart Session", type="primary"):
        st.session_state.messages = []
        st.session_state.interpreter = Interpreter()
        st.session_state.input_text = ""
        st.rerun()

# --- Logic Processing (PRE-RENDER) ---
# We check triggers here BEFORE widgets are rendered to avoid StreamlitAPIException
if st.session_state.get("trigger_run"):
    st.session_state.trigger_run = False
    process_command()
    st.rerun()

# --- Main Interface ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🧮 SpeakMath")

# Display History in a container
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "pipeline" in msg:
                 p = msg["pipeline"]
                 
                 tab1, tab2, tab3 = st.tabs(["1️⃣ Lexer", "2️⃣ Parser (AST)", "3️⃣ Interpreter"])
                 
                 with tab1:
                    if p.get('tokens'):
                         html_badges = ""
                         for t in p['tokens']:
                             html_badges += f'<span class="token-badge"><span class="token-type">{t["type"]}</span>(<span class="token-val">{t["value"]}</span>)</span>'
                         st.markdown(html_badges, unsafe_allow_html=True)
                         st.caption("Tokens generated by Lexer")

                 with tab2:
                    if p.get('ast_node'):
                         try:
                            dot = format_ast_to_dot(p['ast_node'])
                            st.graphviz_chart(dot)
                         except:
                            st.code(p['ast'], language="text")
                    elif p.get('ast'):
                         st.code(p['ast'], language="text")
                 with tab3:
                     if p.get('logs'): st.text(p['logs'])
                     if p.get('error'): st.error(p['error'])
                     else: st.success("Execution Successful")

# --- Input Handling (Native Chat Input) ---
if prompt := st.chat_input("Type a command..."):
    # This block runs when user types in chat input and hits enter
    st.session_state.widget_input = prompt # explicit sync for shared logic if needed, or just pass prompt
    
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Execute Pipeline
    with st.spinner("Processing... 🤖"):
        pipeline, updated_interp = execute_with_pipeline(prompt, st.session_state.interpreter)
    st.session_state.interpreter = updated_interp
    
    # Format Output
    output_text = ""
    if pipeline.get('error'):
        output_text = f"❌ Error: {pipeline['error']}"
    else:
        res = pipeline['result']
        if res is not None:
             output_text = f"✅ Result: **{res}**"
        else:
             output_text = "✅ Done (No output)"

    # Add Assistant Message
    st.session_state.messages.append({
        "role": "assistant", 
        "content": output_text,
        "pipeline": pipeline
    })
    st.rerun()
