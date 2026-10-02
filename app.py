# """Streamlit Web Interface for Agentic Code Reviewer."""

# import streamlit as st
# import asyncio
# from reviewer.config import config
# from reviewer.utils import parse_pr_url
# from reviewer.graph import run_review

# # Page configuration
# st.set_page_config(
#     page_title="Agentic Code Reviewer",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Custom CSS
# st.markdown("""
# <style>
# .big-font {
#     font-size:50px !important;
#     font-weight: bold;
# }
# .stProgress > div > div > div > div {
#     background-color: #1f77b4;
# }
# </style>
# """, unsafe_allow_html=True)

# # Title
# st.markdown('<p class="big-font">🤖 Agentic Code Reviewer</p>', unsafe_allow_html=True)
# st.markdown("**AI-powered PR review with parallel agents**")
# st.markdown("---")

# # Sidebar
# with st.sidebar:
#     st.header("⚙️ Configuration")
    
#     # Check configuration
#     try:
#         config.validate()
#         st.success("✅ API Keys Configured")
#         st.info(f"**Model:** {config.model}")
#         st.info(f"**GitHub Token:** {config.github_token[:15]}...")
#         st.info(f"**Groq API Key:** {config.groq_api_key[:15]}...")
#     except ValueError as e:
#         st.error("❌ Configuration Error")
#         st.error(str(e))
#         st.warning("Please update your `.env` file with:")
#         st.code("GITHUB_TOKEN=your_token\nGROQ_API_KEY=your_key\nMODEL=llama-3.3-70b-versatile")
#         st.stop()
    
#     st.markdown("---")
#     st.markdown("### About")
#     st.markdown("""
#     This tool uses **3 AI agents** running in parallel:
#     - 🐛 **Bug Agent**: Logic errors & edge cases
#     - 🔒 **Security Agent**: Vulnerabilities
#     - ✨ **Style Agent**: Code quality
    
#     Then a **Synthesizer** combines all findings into one review.
#     """)
    
#     st.markdown("---")
#     st.markdown("**Powered by:**")
#     st.markdown("- LangGraph (orchestration)")
#     st.markdown("- Groq (LLM inference)")
#     st.markdown("- GitHub API")

# # Main content
# col1, col2 = st.columns([2, 1])

# with col1:
#     st.header("🔗 Enter Pull Request URL")
#     pr_url = st.text_input(
#         "GitHub PR URL",
#         placeholder="https://github.com/owner/repo/pull/123",
#         help="Paste the URL of any GitHub pull request"
#     )
    
#     # Post option
#     should_post = st.checkbox(
#         "Post review to GitHub",
#         value=False,
#         help="If checked, the review will be posted as a comment on the PR. Otherwise, it will only be displayed here."
#     )

# with col2:
#     st.header("📊 Review Stats")
#     stats_placeholder = st.empty()
    
#     # Initial stats
#     with stats_placeholder.container():
#         col_a, col_b, col_c = st.columns(3)
#         col_a.metric("🐛 Bugs", "0")
#         col_b.metric("🔒 Security", "0")
#         col_c.metric("✨ Style", "0")

# # Review button
# if st.button("🚀 Start Review", type="primary", use_container_width=True):
#     if not pr_url:
#         st.error("Please enter a GitHub PR URL")
#         st.stop()
    
#     # Parse URL
#     try:
#         owner, repo, pr_number = parse_pr_url(pr_url)
#     except ValueError as e:
#         st.error(f"Invalid URL: {e}")
#         st.stop()
    
#     # Create placeholders for output
#     status_placeholder = st.empty()
#     progress_bar = st.progress(0)
#     output_placeholder = st.empty()
    
#     # Run the review
#     with status_placeholder.container():
#         st.info(f"📥 Reviewing PR #{pr_number} from {owner}/{repo}...")
    
#     try:
#         # Create status updates
#         progress_bar.progress(10)
        
#         with st.spinner("Fetching PR data..."):
#             # Import the graph components
#             from reviewer.github_client import GitHubClient
#             from reviewer.state import create_initial_state
#             from reviewer.agents.bug_agent import bug_agent
#             from reviewer.agents.security_agent import security_agent
#             from reviewer.agents.style_agent import style_agent
#             from reviewer.agents.synthesizer import synthesizer_agent
#             from reviewer.graph import fetch_pr_node
            
#             # Create initial state
#             initial_state = create_initial_state(owner, repo, pr_number, pr_url)
#             initial_state["should_post"] = should_post
            
#             progress_bar.progress(20)
            
#             # Fetch PR
#             with output_placeholder.container():
#                 st.write("### 📥 Fetching PR Data")
#                 fetch_output = st.empty()
            
#             state = asyncio.run(fetch_pr_node(initial_state))
            
#             with fetch_output:
#                 st.success(f"✅ Fetched **{len(state.get('files', []))}** files")
#                 st.info(f"**Title:** {state.get('pr_title', 'N/A')}")
#                 st.info(f"**Author:** @{state.get('pr_author', 'N/A')}")
            
#             progress_bar.progress(40)
            
#             # Run agents
#             with output_placeholder.container():
#                 st.write("### 🤖 Running AI Agents")
                
#                 col1, col2, col3 = st.columns(3)
                
#                 with col1:
#                     st.write("🐛 **Bug Agent**")
#                     bug_status = st.empty()
#                     bug_status.info("Analyzing...")
                
#                 with col2:
#                     st.write("🔒 **Security Agent**")
#                     sec_status = st.empty()
#                     sec_status.info("Analyzing...")
                
#                 with col3:
#                     st.write("✨ **Style Agent**")
#                     style_status = st.empty()
#                     style_status.info("Analyzing...")
            
#             # Run agents (simulating parallel with asyncio)
#             async def run_all_agents(state):
#                 bug_result, sec_result, style_result = await asyncio.gather(
#                     bug_agent(state),
#                     security_agent(state),
#                     style_agent(state)
#                 )
#                 # Merge results
#                 state["bug_findings"] = bug_result.get("bug_findings", [])
#                 state["security_findings"] = sec_result.get("security_findings", [])
#                 state["style_findings"] = style_result.get("style_findings", [])
#                 return state
            
#             state = asyncio.run(run_all_agents(state))
            
#             # Update status
#             bug_count = len(state.get("bug_findings", []))
#             sec_count = len(state.get("security_findings", []))
#             style_count = len(state.get("style_findings", []))
            
#             bug_status.success(f"✅ Found {bug_count} issue(s)")
#             sec_status.success(f"✅ Found {sec_count} issue(s)")
#             style_status.success(f"✅ Found {style_count} issue(s)")
            
#             # Update stats
#             with stats_placeholder.container():
#                 col_a, col_b, col_c = st.columns(3)
#                 col_a.metric("🐛 Bugs", bug_count)
#                 col_b.metric("🔒 Security", sec_count)
#                 col_c.metric("✨ Style", style_count)
            
#             progress_bar.progress(70)
            
#             # Synthesize
#             with output_placeholder.container():
#                 st.write("### 🔄 Synthesizing Review")
#                 synth_status = st.empty()
#                 synth_status.info("Combining findings...")
            
#             synth_result = asyncio.run(synthesizer_agent(state))
#             state["final_review"] = synth_result.get("final_review", "")
#             state["summary"] = synth_result.get("summary", "")
            
#             synth_status.success("✅ Review synthesized")
            
#             progress_bar.progress(90)
            
#             # Post review if requested
#             if should_post:
#                 with output_placeholder.container():
#                     st.write("### 📤 Posting Review")
#                     post_status = st.empty()
#                     post_status.info("Posting to GitHub...")
                
#                 from reviewer.graph import post_review_node
#                 state = asyncio.run(post_review_node(state))
                
#                 if state.get("error"):
#                     post_status.error(f"❌ Error: {state['error']}")
#                 else:
#                     post_status.success(f"✅ Review posted to PR!")
#                     st.success(f"[View PR]({pr_url})")
            
#             progress_bar.progress(100)
            
#             # Display final review
#             st.markdown("---")
#             st.markdown("## 📝 Final Review")
            
#             final_review = state.get("final_review", "No review generated")
            
#             # Display as markdown
#             st.markdown(final_review)
            
#             # Download button
#             st.download_button(
#                 label="📥 Download Review",
#                 data=final_review,
#                 file_name=f"review_pr{pr_number}.md",
#                 mime="text/markdown"
#             )
            
#             status_placeholder.success("✅ Review Complete!")
        
#     except Exception as e:
#         status_placeholder.error(f"❌ Error: {str(e)}")
#         st.exception(e)

# # Footer
# st.markdown("---")
# st.markdown("""
# <div style='text-align: center; color: gray;'>
# Built with  using Streamlit | Powered by Groq & LangGraph
# </div>
# """, unsafe_allow_html=True)


"""Streamlit Web Interface for Agentic Code Reviewer."""

import streamlit as st
import asyncio
from reviewer.config import config
from reviewer.utils import parse_pr_url
from reviewer.graph import run_review

# Page configuration
st.set_page_config(
    page_title="Agentic Code Reviewer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.big-font {
    font-size:50px !important;
    font-weight: bold;
}
.stProgress > div > div > div > div {
    background-color: #1f77b4;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="big-font">🤖 Agentic Code Reviewer</p>', unsafe_allow_html=True)
st.markdown("**AI-powered PR review with parallel agents**")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check configuration
    try:
        config.validate()
        st.success("✅ API Keys Configured")
        st.info(f"**Model:** {config.model}")
    except ValueError as e:
        st.error("❌ Configuration Error")
        st.error(str(e))
        st.warning("Please update your `.env` file with:")
        st.code("GITHUB_TOKEN=your_token\nGROQ_API_KEY=your_key\nMODEL=llama-3.3-70b-versatile")
        st.stop()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool uses **3 AI agents** running in parallel:
    - 🐛 **Bug Agent**: Logic errors & edge cases
    - 🔒 **Security Agent**: Vulnerabilities
    - ✨ **Style Agent**: Code quality
    
    Then a **Synthesizer** combines all findings into one review.
    """)
    
    st.markdown("---")
    st.markdown("**Powered by:**")
    st.markdown("- LangGraph (orchestration)")
    st.markdown("- Groq (LLM inference)")
    st.markdown("- GitHub API")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🔗 Enter Pull Request URL")
    pr_url = st.text_input(
        "GitHub PR URL",
        placeholder="https://github.com/owner/repo/pull/123",
        help="Paste the URL of any GitHub pull request"
    )
    
    # Post option
    should_post = st.checkbox(
        "Post review to GitHub",
        value=False,
        help="If checked, the review will be posted as a comment on the PR. Otherwise, it will only be displayed here."
    )

with col2:
    st.header("📊 Review Stats")
    stats_placeholder = st.empty()
    
    # Initial stats
    with stats_placeholder.container():
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("🐛 Bugs", "0")
        col_b.metric("🔒 Security", "0")
        col_c.metric("✨ Style", "0")

# Review button
if st.button("🚀 Start Review", type="primary", use_container_width=True):
    if not pr_url:
        st.error("Please enter a GitHub PR URL")
        st.stop()
    
    # Parse URL
    try:
        owner, repo, pr_number = parse_pr_url(pr_url)
    except ValueError as e:
        st.error(f"Invalid URL: {e}")
        st.stop()
    
    # Create placeholders for output
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    output_placeholder = st.empty()
    
    # Run the review
    with status_placeholder.container():
        st.info(f"📥 Reviewing PR #{pr_number} from {owner}/{repo}...")
    
    try:
        # Create status updates
        progress_bar.progress(10)
        
        with st.spinner("Fetching PR data..."):
            # Import the graph components
            from reviewer.github_client import GitHubClient
            from reviewer.state import create_initial_state
            from reviewer.agents.bug_agent import bug_agent
            from reviewer.agents.security_agent import security_agent
            from reviewer.agents.style_agent import style_agent
            from reviewer.agents.synthesizer import synthesizer_agent
            from reviewer.graph import fetch_pr_node
            
            # Create initial state
            initial_state = create_initial_state(owner, repo, pr_number, pr_url)
            initial_state["should_post"] = should_post
            
            progress_bar.progress(20)
            
            # Fetch PR
            with output_placeholder.container():
                st.write("### 📥 Fetching PR Data")
                fetch_output = st.empty()
            
            state = asyncio.run(fetch_pr_node(initial_state))
            
            with fetch_output:
                st.success(f"✅ Fetched **{len(state.get('files', []))}** files")
                st.info(f"**Title:** {state.get('pr_title', 'N/A')}")
                st.info(f"**Author:** @{state.get('pr_author', 'N/A')}")
            
            progress_bar.progress(40)
            
            # Run agents
            with output_placeholder.container():
                st.write("### 🤖 Running AI Agents")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("🐛 **Bug Agent**")
                    bug_status = st.empty()
                    bug_status.info("Analyzing...")
                
                with col2:
                    st.write("🔒 **Security Agent**")
                    sec_status = st.empty()
                    sec_status.info("Analyzing...")
                
                with col3:
                    st.write("✨ **Style Agent**")
                    style_status = st.empty()
                    style_status.info("Analyzing...")
            
            # Run agents (simulating parallel with asyncio)
            async def run_all_agents(state):
                bug_result, sec_result, style_result = await asyncio.gather(
                    bug_agent(state),
                    security_agent(state),
                    style_agent(state)
                )
                # Merge results
                state["bug_findings"] = bug_result.get("bug_findings", [])
                state["security_findings"] = sec_result.get("security_findings", [])
                state["style_findings"] = style_result.get("style_findings", [])
                return state
            
            state = asyncio.run(run_all_agents(state))
            
            # Update status
            bug_count = len(state.get("bug_findings", []))
            sec_count = len(state.get("security_findings", []))
            style_count = len(state.get("style_findings", []))
            
            bug_status.success(f"✅ Found {bug_count} issue(s)")
            sec_status.success(f"✅ Found {sec_count} issue(s)")
            style_status.success(f"✅ Found {style_count} issue(s)")
            
            # Update stats
            with stats_placeholder.container():
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("🐛 Bugs", bug_count)
                col_b.metric("🔒 Security", sec_count)
                col_c.metric("✨ Style", style_count)
            
            progress_bar.progress(70)
            
            # Synthesize
            with output_placeholder.container():
                st.write("### 🔄 Synthesizing Review")
                synth_status = st.empty()
                synth_status.info("Combining findings...")
            
            synth_result = asyncio.run(synthesizer_agent(state))
            state["final_review"] = synth_result.get("final_review", "")
            state["summary"] = synth_result.get("summary", "")
            
            synth_status.success("✅ Review synthesized")
            
            progress_bar.progress(90)
            
            # Post review if requested
            if should_post:
                with output_placeholder.container():
                    st.write("### 📤 Posting Review")
                    post_status = st.empty()
                    post_status.info("Posting to GitHub...")
                
                from reviewer.graph import post_review_node
                state = asyncio.run(post_review_node(state))
                
                if state.get("error"):
                    post_status.error(f"❌ Error: {state['error']}")
                else:
                    post_status.success(f"✅ Review posted to PR!")
                    st.success(f"[View PR]({pr_url})")
            
            progress_bar.progress(100)
            
            # Display final review
            st.markdown("---")
            st.markdown("## 📝 Final Review")
            
            final_review = state.get("final_review", "No review generated")
            
            # Display as markdown
            st.markdown(final_review)
            
            # Download button
            st.download_button(
                label="📥 Download Review",
                data=final_review,
                file_name=f"review_pr{pr_number}.md",
                mime="text/markdown"
            )
            
            status_placeholder.success("✅ Review Complete!")
        
    except Exception as e:
        status_placeholder.error(f"❌ Error: {str(e)}")
        st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
Built with  using Streamlit | Powered by Groq & LangGraph
</div>
""", unsafe_allow_html=True)