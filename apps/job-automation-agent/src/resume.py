import os

from jinja2 import BaseLoader, Environment, FileSystemLoader

# Template dir with check
template_dir = os.path.join(os.path.dirname(__file__), "../../templates")
if os.path.exists(template_dir):
    env = Environment(loader=FileSystemLoader(template_dir),
                      block_start_string="[%", block_end_string="%]")
else:
    env = Environment(loader=BaseLoader())  # Fallback empty
    print("Warning: templates not found, using fallback.")


async def generate_resume(profile: dict, job_description: str) -> str:
    """Generates a resume based on user profile and job description."""
    template = env.from_string("""{{ name }} has skills in {{ skills|join(', ') }}.""")
    return template.render(**profile)

