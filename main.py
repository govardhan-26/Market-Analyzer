
import sys
import subprocess

# --- Dependency check ---
# If running outside the project's virtual environment, required packages
# won't be available. Give a clear message instead of a cryptic ImportError.
try:
    from dotenv import load_dotenv
    from langchain_openai import ChatOpenAI
except ImportError as _e:
    print(
        f"Error: Missing dependency — {_e}\n\n"
        "This project uses 'uv' for dependency management.\n"
        "Please run the script using one of these methods:\n\n"
        "  uv run python main.py\n\n"
        "Or activate the virtual environment first:\n\n"
        "  .venv\\Scripts\\Activate.ps1   (PowerShell)\n"
        "  .venv\\Scripts\\activate.bat   (CMD)\n\n"
        "Then retry:  python main.py",
        file=sys.stderr,
    )
    sys.exit(1)
from langchain_core.tools import tool
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

load_dotenv()

set_llm_cache(SQLiteCache(database_path=".langchain_cache.db"))

model = ChatOpenAI(model="gpt-4o")

search_tool = DuckDuckGoSearchResults(name="web_search")

BLOCKED_PATTERNS = ["import os", "import sys", "import subprocess", "open(", "__import__"]


@tool
def run_code(code: str) -> str:
    """Execute Python code and return the output. Use for calculations, data analysis, and generating tables."""
    if any(pattern in code for pattern in BLOCKED_PATTERNS):
        return "Error: Potentially unsafe code detected. Only math and data operations are allowed."
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode != 0:
        return f"Error:\n{result.stderr}"
    return result.stdout.strip() or "Code executed successfully (no output)."


research_agent = create_agent(
    model=model,
    tools=[search_tool],
    name="researcher",
    system_prompt=(
        "You are a market research specialist. Search the web for data on job markets, "
        "salaries, industry trends, and economic indicators. Return detailed findings with numbers."
    ),
)

code_agent = create_agent(
    model=model,
    tools=[run_code],
    name="coder",
    system_prompt=(
        "You are a data analyst who writes Python code. When given research data, "
        "write code to calculate statistics, comparisons, percentage differences, "
        "and format results into clear tables. Always print the output."
    ),
)

workflow = create_supervisor(
    agents=[research_agent, code_agent],
    model=model,
    prompt=(
        "You are a market analysis project manager. Your goal is to produce a data-driven "
        "market comparison report. Workflow:\n"
        "1. Send the researcher to gather data on BOTH sides of the comparison\n"
        "2. Send the coder to calculate differences, ratios, and build comparison tables\n"
        "3. If the coder needs more data, send the researcher again\n"
        "4. Compile the final analysis with both qualitative insights and quantitative data"
    ),
)

app = workflow.compile()


def run_analysis(query: str) -> str:
    """Run a market analysis query and return the final result."""
    result = app.invoke({
        "messages": [{"role": "user", "content": query}]
    })
    return result["messages"][-1].content


if __name__ == "__main__":
    query = "Compare the tech job market in the US vs UK: average salaries, demand trends, and top hiring cities"
    print(run_analysis(query))
